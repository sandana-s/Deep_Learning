import React, { useState } from "react";

function ChatUI({ selectedAgent }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: "user",
      content: input,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          agent_type: selectedAgent,
        }),
      });

      const data = await response.json();
      console.log("Response:", data);

      let content = "";
      let fileLink = null;
      if (typeof data.response === "object" && data.response !== null) {
        content = data.response.message || "";
        fileLink = data.response.file_path || null;
      } else {
        content = data.response;
      }

      const botMessage = {
        role: "bot",
        content,
        fileLink,
        agent: data.agent_used,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    // Check if the key pressed is 'Enter' (e.key === 'Enter') 
    // AND if the bot is not currently loading/typing (!loading)
    if (e.key === 'Enter' && !loading) {
      e.preventDefault(); // Prevent default form submission behavior
      handleSend();       // Call the send function
    }
  };

  return (
    <div className="flex flex-col  h-[450px] bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-inner p-4 overflow-hidden">
      <h2 className="text-xl font-semibold text-gray-800 mb-3 flex items-center gap-2">

      </h2>

      <div className="flex-1 overflow-y-auto space-y-3 px-1 scrollbar-thin scrollbar-thumb-blue-200">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex flex-col ${m.role === "user" ? "items-end" : "items-start"
              }`}
          >
            <div
              className={`p-3 rounded-2xl max-w-[80%] shadow-md text-sm transition-all ${m.role === "user"
                  ? "bg-blue-600 text-white rounded-br-none"
                  : "bg-white text-gray-800 rounded-bl-none"
                }`}
            >
              {m.content}
              {m.fileLink && (
                <a
                  href={m.fileLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  download
                  className="block mt-2 bg-blue-100 text-blue-700 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-blue-200 transition"
                >
                  ⬇️ Download PPT
                </a>
              )}
            </div>
            <div className="text-xs text-gray-400 mt-1">{m.timestamp}</div>
          </div>
        ))}

        {loading && (
          <div className="text-gray-500 italic animate-pulse">Bot is typing...</div>
        )}
      </div>

      <div className="flex items-center mt-4 border-t pt-3">
        <input
          className="flex-1 border rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="ml-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-full px-5 py-2 font-medium hover:scale-105 transition-all disabled:opacity-50"
        >
          ➤
        </button>
      </div>
    </div>
  );
}

export default ChatUI;
