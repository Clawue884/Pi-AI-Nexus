from fastapi import FastAPI
from pydantic import BaseModel
import openai
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

# Inisialisasi FastAPI
app = FastAPI()

# Konfigurasi OpenAI API Key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Model Input
class ChatRequest(BaseModel):
    prompt: str

# Fungsi AI Generatif
def generate_response(prompt: str):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "Kamu adalah AI yang cerdas untuk ekosistem Pi."},
                  {"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# API Endpoint
@app.post("/chat")
async def chat_ai(request: ChatRequest):
    response = generate_response(request.prompt)
    return {"response": response}

# Jalankan server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
