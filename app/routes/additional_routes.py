from fastapi import APIRouter
from redis import Redis
from services import connect_milvus, search_vectors, get_all_vectors
from config import Config
import logging
import openai


# services
router = APIRouter()
redis_client = Redis(host=Config.redis_host, port=Config.redis_port)
connect_milvus()
client = openai.Client(api_key=Config.openai_api_key)


# get chat history by session_id
@router.get("/get_chat_history")
def get_chat_history(session_id: str):
    history_key = f"chat_history:{session_id}"
    chat_history = redis_client.lrange(history_key, 0, -1)
    if not chat_history:
        return {"error": "Session ID not found"}

    history = [{"role": entry.decode('utf-8').split(':', 1)[0], "content": entry.decode('utf-8').split(':', 1)[1]} for entry in chat_history]
    return {"session_id": session_id, "history": history}


# show all redis info
@router.get("/redis/all")
def get_redis_info():
    try:
        keys = redis_client.keys('*')
        result = {}

        for key in keys:
            key_str = key.decode('utf-8')
            key_type = redis_client.type(key_str).decode('utf-8')

            if key_type == 'list':
                values = redis_client.lrange(key_str, 0, -1)
                result[key_str] = [value.decode('utf-8') for value in values]
            else:
                value = redis_client.get(key)
                result[key_str] = value.decode('utf-8') if value else None

        return {"data": result}
    except Exception as e:
        logging.error(f'Error retrieving Redis data: {e}')
        return {"error": str(e)}


# show all embeddings from milvus
@router.get("/milvus/vectors")
def get_milvus_vectors():
    try:
        vectors = get_all_vectors('text_collection')
        return {"vectors": vectors}
    except Exception as e:
        logging.error(f'Error retrieving vectors: {e}')
        return {"error": str(e)}


