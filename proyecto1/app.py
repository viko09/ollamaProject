from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import os
import json

app = FastAPI()

# Serve frontend files: endpoint static para servir archivos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ollama Settings
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"  # Change if preferred

# Servir la pagina de inicio
@app.get("/")
def serve_homepage():
    return FileResponse(os.path.join("static", "index.html"))

@app.post("/chat")
def chat(prompt: str = Query(..., description="Prompt text")):
    headers = {"Content-Type": "application/json"}

    try:
        # Send request to Ollama
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            headers=headers
        )

        print("Ollama Response:", response.text)

        response_data = response.text.strip()
        try:
            json_response = json.loads(response_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail=f"Invalid JSON response: {response_data}")

        ai_response = json_response.get("response")
        if not ai_response:
            raise HTTPException(status_code=500, detail=f"No valid response from AI")

        return {"response": ai_response}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request to Ollama failed: {str(e)}")


# RUN API SERVER
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
