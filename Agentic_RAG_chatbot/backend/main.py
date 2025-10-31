from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import os
import shutil
from contextlib import asynccontextmanager
from typing import Any

from backend.core.pdf_utils import extract_text_from_pdf
from backend.core.embeddings import create_embeddings, get_query_embedding
from backend.core.faiss_store import FAISSStore
from backend.agents.pdf_qa_agent import PDFQAAgent
from backend.agents.summarization_agent import SummarizationAgent
from backend.agents.ppt_agent import PPTAgent
from backend.core.llm_clients import llm_client  

# -------------------- FASTAPI SETUP -------------------- #

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up Agentic RAG Chatbot...")
    await llm_client.warm_up()   # preload Ollama model for instant response
    print("🔥 Model is warmed up and FAISS initialized.")
    yield
    await llm_client.close()
    print("🛑 Shutting down Agentic RAG Chatbot...")

app = FastAPI(title="⚡ Agentic RAG Chatbot", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# mount static file after app creation
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


# -------------------- DIRECTORIES -------------------- #

UPLOAD_DIR = Path("uploads")
FAISS_DIR = Path("faiss_index")
OUTPUT_DIR = Path("outputs")

for d in [UPLOAD_DIR, FAISS_DIR, OUTPUT_DIR]:
    d.mkdir(exist_ok=True)

# -------------------- GLOBAL STATE -------------------- #

faiss_store = FAISSStore(str(FAISS_DIR))
pdf_qa_agent = PDFQAAgent(faiss_store)
summarization_agent = SummarizationAgent(faiss_store)
ppt_agent = PPTAgent(faiss_store)
current_pdf_text = ""
last_uploaded_file = None

# -------------------- MODELS -------------------- #

class ChatRequest(BaseModel):
    message: str
    agent_type: str = "auto"  # "auto", "qa", "summarize", "ppt"

class ChatResponse(BaseModel):
    response: Any
    agent_used: str

# -------------------- ROUTES -------------------- #

@app.get("/")
async def root():
    return {"message": "Agentic RAG Chatbot API is running ⚡"}

# ---------- Upload PDF and Create FAISS Index ---------- #
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global current_pdf_text, last_uploaded_file

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = UPLOAD_DIR / file.filename

    # Skip reprocessing if same PDF uploaded
    if last_uploaded_file == file.filename and faiss_store.index is not None:
        print("⚡ Skipping reprocessing, PDF already processed.")
        return {"message": "PDF already processed", "filename": file.filename}

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        current_pdf_text = extract_text_from_pdf(str(file_path))
        if not current_pdf_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        chunks = create_embeddings(current_pdf_text)
        faiss_store.create_index(chunks)
        last_uploaded_file = file.filename

        return {
            "message": "✅ PDF uploaded and processed successfully",
            "filename": file.filename,
            "text_length": len(current_pdf_text),
            "chunks_created": len(chunks),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")

# ---------- Chat with the System (QA / Summarize / PPT) ---------- #
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    global current_pdf_text

    if not current_pdf_text:
        raise HTTPException(status_code=400, detail="Please upload a PDF first.")

    try:
        agent_type = request.agent_type.lower()
        message = request.message.lower()

        # Auto agent detection
        if agent_type == "auto":
            if any(word in message for word in ["summarize", "overview", "brief", "summary"]):
                agent_type = "summarize"
            elif any(word in message for word in ["create ppt","ppt","create a ppt","make appt","slides", "make ppt", "powerpoint", "slides"]):
                agent_type = "ppt"
            else:
                agent_type = "qa"

        # Route to correct agent
        if agent_type == "summarize":
            response = await summarization_agent.process(request.message, current_pdf_text)
            agent_used = "Summarization Agent"

        elif agent_type == "ppt":
            result = await ppt_agent.process(request.message, current_pdf_text)
            agent_used = "PPT Creation Agent"

            # extract file name if PPT created
            if isinstance(result, str) and "generated_ppt_" in result:
                # extract filename
                filename = result.split("generated_ppt_")[-1].split(".pptx")[0]
                filename = f"generated_ppt_{filename}.pptx"

                file_path = f"/outputs/{filename}"
                download_url = f"http://localhost:8000{file_path}"

                return ChatResponse(
                    response={
                        "message": "✅ PPT created successfully.",
                        "file_path": download_url
                    },
                    agent_used=agent_used
                )

            # if response didn’t contain file info
            return ChatResponse(response=result, agent_used=agent_used)

        else:
            response = await pdf_qa_agent.process(request.message)
            agent_used = "PDF Q&A Agent"

        return ChatResponse(response=response, agent_used=agent_used)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


# ---------- Download PPT ---------- #
@app.get("/download-ppt/{filename}")
async def download_ppt(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PPT file not found")
    return FileResponse(file_path, filename=filename)

# ---------- Reset System ---------- #
@app.delete("/reset")
async def reset():
    global current_pdf_text, last_uploaded_file
    current_pdf_text = ""
    last_uploaded_file = None
    faiss_store.reset()
    return {"message": "System reset successfully 🧹"}

# ---------- Run the Server ---------- #
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
