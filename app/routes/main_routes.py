from fastapi import BackgroundTasks, APIRouter
from redis import Redis
import uuid
from utils import handle_task, encode_text
from services import connect_milvus, search_vectors, get_all_vectors
from config import Config
import logging
import openai
from typing import Optional


# services
router = APIRouter()
redis_client = Redis(host=Config.redis_host, port=Config.redis_port)
connect_milvus()
client = openai.Client(api_key=Config.openai_api_key)


@router.post("/process")
def process_request(text_query: str, background_tasks: BackgroundTasks):
    # create a task_id and pending into background tasks
    task_id = str(uuid.uuid4())
    redis_client.set(f"task:{task_id}", 'pending')
    background_tasks.add_task(handle_task, task_id, text_query, 'text_collection', redis_client)
    return {"task_id": task_id}


@router.get("/status")
def get_status(task_id: str):
    status = redis_client.get(f"task:{task_id}")
    if status:
        return {"status": status.decode('utf-8')}
    return {"status": "task_id does not exist"}


@router.post("/chat")
def chat(text_request: str, session_id: Optional[str] = None):
    collection_name = 'text_collection'

    # get embeddings from users request
    query_vector = encode_text(text_request)

    # search similarity texts in milvus
    results = search_vectors(collection_name, query_vector)

    # create a context after searching
    context = ""
    for result in results:
        for match in result:
            text = redis_client.get(f"text:{collection_name}:{match.id}")
            if text:
                context += f"Text: {text.decode('utf-8')}\nDistance: {match.distance}\n"
    logging.info(context)

    # get session_id if exists, else create a new session_id
    if session_id is None:
        session_id = str(uuid.uuid4())
    history_key = f"chat_history:{session_id}"

    # save user`s messages in chat_history
    redis_client.rpush(history_key, f"user:{text_request}")

    # get all history from user chat_history
    chat_history = redis_client.lrange(history_key, 0, -1)
    messages = []
    for entry in chat_history:
        role, content = entry.decode('utf-8').split(':', 1)
        messages.append({"role": role, "content": content})

    # Pending the chat_history and similarity embeddings to OpenAI
    messages.append({"role": "system", "content": f"Based on the following context:\n{context}"})
    messages.append({"role": "user", "content": text_request})

    logging.info(f'PROMPT to OpenAI: {messages}')

    response = client.chat.completions.create(
        model=Config.openai_model,
        max_tokens=300,
        messages=messages
    )
    # save the assistant message in chat_history
    assistant_response = response.choices[0].message.content.strip()
    redis_client.rpush(history_key, f"assistant:{assistant_response}")

    return {"response": assistant_response, "session_id": session_id}
