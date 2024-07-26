import wikipediaapi
from services import create_collection, insert_vectors, check_index_exists, create_index
import logging
from openai import OpenAI
from config import Config
from services import extract_main_entity

logger = logging.getLogger(__name__)

wiki = wikipediaapi.Wikipedia('MyWork (valitovalexey@gmail.com)', 'en')

client = OpenAI(api_key=Config.openai_api_key)


def encode_text(text):
    logging.info(f'Length for embedding text: {len(text)}')
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding


def process_query(query):
    extracted_entities = extract_main_entity(query)
    logging.info(f'Extracted entities: {extracted_entities}')

    page = wiki.page(extracted_entities)
    logger.info(f'Wiki request: {page}')

    if not page.exists():
        return None, None

    paragraphs = [p for p in page.text.split('\n') if p.strip()]
    filtered_paragraphs = []
    vectors = []

    # if paragraph is smaller than 200 symbols and extracted main entity exist in paragraph
    for paragraph in paragraphs:
        if len(paragraph) > 200 and extracted_entities in paragraph:
            filtered_paragraphs.append(paragraph)
            vectors.append(encode_text(paragraph))

    return vectors, filtered_paragraphs


def handle_task(task_id, query, collection_name, redis_client):
    redis_client.set(f"task:{task_id}", 'running')
    collection = create_collection(collection_name)
    vectors, paragraphs = process_query(query)

    if vectors is None or paragraphs is None:
        redis_client.set(f"task:{task_id}", 'failed')
        logger.error("Error: No vectors or paragraphs found.")
        return

    logger.info(f'Number of vectors: {len(vectors)}')
    logger.info(f'Number of paragraphs: {len(paragraphs)}')
    logger.info(f'First paragraph: {paragraphs[0]}')

    if len(vectors) == len(paragraphs):
        ids = [i for i in range(len(vectors))]

        # save data to milvus
        insert_vectors(collection, vectors, ids)

        # save data to redis
        for i, paragraph in enumerate(paragraphs):
            redis_client.set(f"text:{collection_name}:{ids[i]}", paragraph)

        redis_client.set(f"task:{task_id}", 'finished')
    else:
        redis_client.set(f"task:{task_id}", 'failed')
        logger.error("Error: Mismatch between vectors and paragraphs length after filtering.")

    try:
        if not check_index_exists(collection_name, "vec_index"):
            create_index(collection_name)
        collection.load()
        logger.info(f'Collection {collection_name} successfully loaded.')
    except Exception as e:
        logger.error(f'Error loading collection: {e}')
        redis_client.set(f"task:{task_id}", 'failed')
        return




