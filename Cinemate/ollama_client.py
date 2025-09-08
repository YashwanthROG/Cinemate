# ollama_client.py
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

def query_ollama(prompt: str, model: str = "mistral", timeout: int = 30) -> str:
    """
    Sends prompt to local Ollama (Mistral). Returns text reply or empty string on failure.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        # Ollama responses vary slightly; try common keys
        return data.get("response") or data.get("text") or json.dumps(data)
    except Exception as e:
        print(f"[ollama_client] error calling Ollama: {e}")
        return ""
