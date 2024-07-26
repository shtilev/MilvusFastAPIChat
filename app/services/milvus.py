import logging
from config import Config
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection, connections, Index, utility
import numpy as np


def connect_milvus():
    connections.connect(alias="default", host=Config.milvus_host, port=Config.milvus_port)


def create_collection(collection_name, dim=Config.openai_dim):
    try:
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim)
        ]
        schema = CollectionSchema(fields=fields, description="Collection for storing text embeddings")
        collection = Collection(name=collection_name, schema=schema)

        logging.info(f"Created collection {collection_name} with schema: {schema}")
        return collection

    except Exception as e:
        logging.error(f"Error creating collection {collection_name}: {e}")
        raise e


def create_index(collection_name):
    collection = Collection(collection_name)
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    }
    index_name = "vec_index"
    collection.create_index(
        field_name="embedding",
        index_params=index_params,
        index_name=index_name
    )


def insert_vectors(collection, vectors, ids):
    try:
        logging.info(f"Inserting vectors into collection {collection.name}. IDs: {ids}")
        collection.insert([ids, vectors])
        logging.info(f"Successfully inserted vectors into collection {collection.name}.")
    except Exception as e:
        logging.error(f"Error inserting vectors into collection {collection.name}: {e}")
        raise e


def search_vectors(collection_name, query_vector, limit=10):
    collection = Collection(collection_name)
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = collection.search([query_vector], "embedding", search_params, limit=limit)
    return results


def get_all_vectors(collection_name: str):
    try:
        logging.info(f"Checking if collection {collection_name} has an index.")
        hi = has_index(collection_name)
        logging.info(f"Has index: {hi}")

        if not utility.has_collection(collection_name):
            logging.error(f"Collection {collection_name} does not exist.")
            raise ValueError(f"Collection {collection_name} does not exist.")

        collection = Collection(collection_name)
        logging.info(f"Querying collection {collection_name} for vectors.")

        results = collection.query(expr="", output_fields=["embedding"], limit=10)
        vectors = [result["embedding"] for result in results]

        # Перетворимо numpy масиви в списки Python і елементи в float
        def convert_to_list(vec):
            if isinstance(vec, np.ndarray):
                return [float(item) for item in vec]
            elif isinstance(vec, list):
                return [float(item) if isinstance(item, (np.float32, np.float64)) else item for item in vec]
            else:
                return float(vec)

        vectors = [convert_to_list(vec) for vec in vectors]

        logging.info(f"Retrieved vectors: {vectors}")
        return vectors

    except Exception as e:
        logging.error(f"Error in get_all_vectors: {e}")
        raise e


def has_index(collection_name):
    collection = Collection(name=collection_name)
    return collection.index() is not None


def check_index_exists(collection_name, index_name="vec_index"):
    collection = Collection(collection_name)
    return collection.has_index(index_name=index_name)