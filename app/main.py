from fastapi import FastAPI
from redis import Redis
from services import connect_milvus
from config import Config
import logging
import openai
from routes import main_routes, additional_routes


# logging
logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

# services
app = FastAPI()
redis_client = Redis(host=Config.redis_host, port=Config.redis_port)
connect_milvus()
client = openai.Client(api_key=Config.openai_api_key)

# routes
app.include_router(main_routes.router, tags=["main_routes"], prefix="/api/v1")
app.include_router(additional_routes.router, tags=["add_routes"], prefix="/api/v1")

