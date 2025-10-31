# 🤖 Agentic RAG Chatbot

An advanced Retrieval-Augmented Generation (RAG) chatbot application that intelligently routes user queries to specialized AI agents (Q&A, Summarization, PPT Creation) based on the user's intent. The system is built using a modern **React** frontend and a performant **FastAPI** Python backend, featuring Ollama for the Language Model and FAISS for vector storage and semantic caching.

## 🚀 Key Features

* **Agentic Routing:** Automatically detects user intent (question, summary request, PPT creation) and dispatches the query to the correct specialized agent.
* **PDF Processing:** Upload any PDF document to serve as the knowledge base for RAG.
* **Specialized Agents:**
    * **PDF Q&A Agent:** Answers direct questions using RAG over the uploaded document.
    * **Summarization Agent:** Provides concise summaries of the document.
    * **PPT Creation Agent:** Generates a full Microsoft PowerPoint (`.pptx`) presentation based on the document content and user prompts.
* **Caching:** Implements both local dictionary and **FAISS Semantic Caching** for faster, cost-effective, and consistent LLM responses.
* **Modern Stack:** Utilizes React (with Vite/Tailwind) for the frontend and FastAPI for a production-ready, asynchronous backend.

## 🏗️ Project Structure

The project is split into a `backend` (Python/FastAPI) and a `frontend` (React/Vite) directory.
## ⚙️ Getting Started

### Prerequisites

1.  **Python 3.8+**
2.  **Node.js / npm (or yarn)**
3.  **Ollama:** The backend relies on Ollama to run the Language Model (LLM) locally.
    * Install Ollama: `https://ollama.com/`
    * Pull the required model (used in `llm_clients.py`):
        ```bash
        ollama pull gemma2:2b
        ```
4.  **A running Ollama Server:** Ensure the server is running on the default port:
    ```bash
    ollama serve
    ```

### 1. Backend Setup (Python / FastAPI)

1.  Navigate to the `backend/` directory.
2.  Create a virtual environment (recommended) and activate it.
3.  Install the required Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Start the FastAPI server:
    ```bash
    python main.py
    # or using uvicorn (as configured in main.py)
    # uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    The API will be available at `http://localhost:8000`.

### 2. Frontend Setup (React / Vite)

1.  Navigate to the `frontend/` directory.
2.  Install Node dependencies:
    ```bash
    npm install
    # or yarn install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    # or yarn dev
    ```
    The frontend should open in your browser, typically at `http://localhost:5173` or `http://localhost:3000`.

---

## 👩‍💻 Usage Guide

1.  **Launch the App:** Open the frontend URL in your browser (`http://localhost:3000`).
2.  **Upload a PDF:** Click the "**Upload New PDF**" button and select a document. The backend will automatically extract text, chunk the content, and create a **FAISS vector index** for RAG.
3.  **Select an Agent (Optional):** Use the dropdown to choose a specific agent, or leave it on **`Auto`** for smart routing.
    * **Auto:** Recommended. The system analyzes your message for keywords like "summarize" or "create ppt."
4.  **Start Chatting:**
    * **Q&A:** Ask a question like "What are the main topics discussed?" (Routes to PDF Q&A Agent).
    * **Summarize:** Ask for "a brief summary of the document" (Routes to Summarization Agent).
    * **PPT:** Ask to "create a presentation with 5 slides" (Routes to PPT Creation Agent).
5.  **Download PPT:** If the **PPT Creation Agent** is used, a "⬇️ Download PPT" link will appear in the chat for the generated file from the `/outputs` directory.
6.  **Reset:** Click the "**Upload New PDF**" button in the sidebar to delete the current FAISS index and prepare for a new document.