AI Support Copilot (MVP)
An end-to-end vertical slice of an AI-powered support copilot that ingests a knowledge base, receives tickets, and suggests answers with sources using a local AI model.

Status: MVP. This version uses Docker for the backend and a Streamlit app for the user interface.

Stack
Backend: FastAPI (Python)

DB: PostgreSQL + pgvector

AI: Ollama (llama3 + mxbai-embed-large)

Web UI: Streamlit

How It Works
This project uses a Retrieval-Augmented Generation (RAG) pipeline:

Ingestion: Markdown files from a knowledge base are broken into chunks and converted into numerical vectors (embeddings) using a local AI model.

Storage: These vectors are stored in a PostgreSQL database with the pgvector extension.

Retrieval: When a new ticket comes in, its text is converted into a vector. The database is then searched to find the most similar knowledge base chunks.

Generation: The original ticket text and the retrieved chunks are passed to a local Large Language Model (LLM), which generates a helpful, cited answer.

Quick Start
This guide will get the backend API and the Streamlit web UI running on your local machine.

0) Prerequisites
Docker + Docker Compose

Ollama: Download and install from ollama.com.

Python 3.11+ installed on your local machine (for the Streamlit app).

1) Pull the AI Models
After installing Ollama, open your terminal and pull the required models. This will download them to your machine.


ollama pull llama3
ollama pull mxbai-embed-large
2) Start the Backend Services
With Docker running, start the API and database containers. This command will build the Docker image and start the services in the background.


docker compose up --build -d
Your API is now running. You can view the documentation at http://localhost:8000/docs.

3) Set Up the Database
In a new terminal, run the following commands to prepare your database.

First, create the database tables:
docker compose exec api python -m apps.api.scripts.create_tables

Second, ingest the sample knowledge base files:
docker compose exec api python -m apps.api.scripts.ingest_kb --org "Acme Inc" --path /app/data/kb
Your backend is now fully initialized and ready to serve requests.

4) Launch the Web App
The Streamlit app is the user interface for your copilot.


First, install the required Python libraries on your machine:
pip3 install streamlit requests

Second, launch the web app:
python3 -m streamlit run webapp.py
A new tab should automatically open in your web browser at http://localhost:8501. You can now use the interface to create tickets and get AI suggestions.

