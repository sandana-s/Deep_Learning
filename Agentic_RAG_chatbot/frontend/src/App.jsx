import React, { useState } from "react";
import FileUploader from "./components/FileUploader";
import ChatUI from "./components/ChatUI";
import AgentSelector from "./components/AgentSelector";
import Lottie from "lottie-react";
import robotAnim from "./assets/AnimaBot.json";
import "./app.css"; // ✅ IMPORTANT FIX

function App() {
  const [pdfUploaded, setPdfUploaded] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState("auto");
  const [uploadInfo, setUploadInfo] = useState(null);

  const handleUploadSuccess = (info) => {
    setPdfUploaded(true);
    setUploadInfo(info);
  };

  const handleReset = async () => {
    try {
      const response = await fetch("http://localhost:8000/reset", {
        method: "DELETE",
      });
      if (response.ok) {
        setPdfUploaded(false);
        setUploadInfo(null);
        setSelectedAgent("auto");
      }
    } catch (error) {
      console.error("Error resetting:", error);
    }
  };

  return (
    <div className="app-container">
      {!pdfUploaded ? (
        <div className="upload-view">
          <Lottie animationData={robotAnim} loop className="w-20 h-20 mb-4" />
          <h2 className="bot-header-title">Agentic RAG Chatbot</h2>
          <p className="upload-subtitle">Upload a PDF to Get Started</p>
          <FileUploader onUploadSuccess={handleUploadSuccess} />
        </div>
      ) : (
        <>
          <div className="sidebar">
            <h3>Document</h3>
            <p className="file-name">{uploadInfo?.filename}</p>

            <h3>Agent</h3>
            <AgentSelector
              selectedAgent={selectedAgent}
              onSelectAgent={setSelectedAgent}
            />

            <button onClick={handleReset} className="upload-btn">
              Upload New PDF
            </button>
          </div>

          <div className="chat-section">
            <div className="bot-header">
              <Lottie animationData={robotAnim} loop className="w-14 h-14" />
              <h1>Agentic RAG Chatbot</h1>
            </div>

            <ChatUI selectedAgent={selectedAgent} />
          </div>
        </>
      )}
    </div>
  );
}

export default App;
