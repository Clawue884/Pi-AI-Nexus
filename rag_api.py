from fastapi import FastAPI
from pydantic import BaseModel
import openai
import requests
from elasticsearch import Elasticsearch
import pinecone
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# Inisialisasi FastAPI
app = FastAPI()

# API Key OpenAI & Pinecone
openai.api_key = "YOUR_OPENAI_API_KEY"
pinecone.init(api_key="YOUR_PINECONE_API_KEY", environment="us-west1-gcp")

# Inisialisasi Elasticsearch untuk indeks pencarian teks
es = Elasticsearch("http://localhost:9200")

# Inisialisasi Pinecone untuk pencarian vektor AI
index = pinecone.Index("pi-rag-search")
embedding_model = OpenAIEmbeddings()

# Model LLM untuk AI Generatif
llm = OpenAI(temperature=0.5, model_name="gpt-4-turbo")

# Class Input
class QueryInput(BaseModel):
    query: str

# Fungsi Retrieval + Augmentation
def retrieve_data(query):
    # **Langkah 1: Cari di Elasticsearch (Teks)**
    es_results = es.search(index="pi-dapps", body={"query": {"match": {"content": query}}})

    # **Langkah 2: Cari di Pinecone (Vektor)**
    vector = embedding_model.embed_query(query)
    pinecone_results = index.query(vector, top_k=3, include_metadata=True)

    # **Langkah 3: Gabungkan hasil retrieval**
    retrieved_docs = []
    for hit in es_results["hits"]["hits"]:
        retrieved_docs.append(hit["_source"]["content"])
    for match in pinecone_results["matches"]:
        retrieved_docs.append(match["metadata"]["text"])

    return " ".join(retrieved_docs)

# API Endpoint untuk Generatif RAG
@app.post("/rag")
async def generate_rag(request: QueryInput):
    context = retrieve_data(request.query)

    # **Langkah 4: Gunakan GPT-4 Turbo untuk generasi jawaban**
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Anda adalah AI Pi Network yang menjawab dengan informasi akurat dari blockchain."},
            {"role": "user", "content": f"Pertanyaan: {request.query}\n\nKonteks: {context}"}
        ]
    )
    return {"response": response["choices"][0]["message"]["content"]}

# Jalankan server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
