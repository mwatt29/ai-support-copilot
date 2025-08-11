import ollama
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a client that points to Ollama running on the host machine
client = ollama.Client(host='http://host.docker.internal:11434')

def get_embeddings(texts: list[str], model: str = "mxbai-embed-large") -> list[list[float]]:
    """Generates embeddings for a list of texts using the local client."""
    logger.info(f"Generating embeddings for {len(texts)} documents using local model: {model}")
    try:
        return [client.embeddings(model=model, prompt=text)['embedding'] for text in texts]
    except Exception as e:
        logger.error(f"Error generating embeddings with Ollama: {e}")
        raise

def get_completion(prompt: str, model: str = "llama3") -> str:
    """Gets a completion from a locally running Ollama model using the local client."""
    logger.info(f"Getting completion from local Ollama model: {model}")
    try:
        response = client.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']
    except Exception as e:
        logger.error(f"Error getting completion from Ollama: {e}")
        raise