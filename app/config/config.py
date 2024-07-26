import os
from dotenv import load_dotenv


load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class Config:
    milvus_host = 'milvus-standalone'
    milvus_port = 19530
    redis_host = 'redis'
    redis_port = 6379
    openai_api_key = OPENAI_API_KEY
    tokenizer_ner_model = "Babelscape/wikineural-multilingual-ner"
    model_ner = "Babelscape/wikineural-multilingual-ner"
    openai_dim = 1536
    openai_model = 'gpt-4o-mini'
    collection_name = ""
