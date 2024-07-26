**Install and run project:** 
-
- clone the repo: ```git clone https://github.com/shtilev/MilvusFastAPIChat```
- create ```.env```file in the folder ```/app``` and put into ```OPENAI_API_KEY= ...```
- run ```docker compose up```
- after starting all services you can go http://localhost:8000/docs

**Routes**:
-
*main_routes*:

- ```/api/v1/process/``` - create a background task to parse necessary info from Wikipedeia, create embdedding`s and upload them into milvus database
- ```/api/v1/status``` - give`s status of background task (pending, running, failed, finished)
- ```/api/v1/chat``` - RAG chat

*additional_routes*:

- ```/api/v1/get_chat_history``` - show chat history by session_id
- ```/api/v1/redis/all``` - show all info from redis database (including background tasks, texts and chat history)
- ```/api/v1/milvus/vectors``` - show all vectors from milvus database

**Application Description**
-
This project is a vector-based search application using FastAPI, Milvus, Redis, and Docker. It is designed to provide efficient storage, retrieval, and management of vector data, ideal for tasks like similarity search and natural language processing.

**How It Works:**
-
**Data Storage**: Vector data is stored in Milvus, which supports fast and efficient querying of high-dimensional vectors.

**API Interaction**: The FastAPI application provides endpoints for interacting with the vector data, including adding vectors and performing search queries.
Caching: Redis is used to cache frequent queries and manage session data, optimizing response times and reducing load on the database.