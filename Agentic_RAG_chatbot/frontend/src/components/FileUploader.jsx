import React, { useState } from "react";

function FileUploader({ onUploadSuccess }) {
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);

    try {
      const res = await fetch("http://localhost:8000/upload-pdf", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      onUploadSuccess(data);
    } catch (error) {
      console.error("Error uploading:", error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="text-center py-8">
      <label className="cursor-pointer bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-3 rounded-xl shadow-md font-semibold hover:scale-105 transition">
        {uploading ? "Uploading..." : "Upload PDF"}
        <input type="file" accept="application/pdf" hidden onChange={handleUpload} />
      </label>
    </div>
  );
}

export default FileUploader;
