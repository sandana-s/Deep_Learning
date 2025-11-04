# 🧾 Invoice Extraction App (Multi-Agent AI)

This is a Multi-Agent AI application that extracts invoice details from uploaded files and converts them into structured **JSON output**. It supports **Images (OCR)**, **DOCX**, and **plain text** files.

---

## 🚀 Features

- 🖼 Image OCR using GPT-4o-mini Vision  
- 📄 Reads DOCX & text files  
- 🌍 Detects language & auto-translation to English  
- 🔍 Extracts fields:  
  - invoice_number  
  - date  
  - vendor  
  - total  
- 🤖 Multi-agent pipeline for better accuracy  
- ✅ Gradio Web UI for easy usage  

---
## 📥 Input → Output Workflow

1️⃣ Extract Text  
2️⃣ Detect & Translate Language  
3️⃣ Extract JSON invoice details  

**Example Output:**

{
  "invoice_number": "INV-1029",
  "date": "2025-10-21",
  "vendor": "ABC Supplies",
  "total": "$1299.55"
}


# 🏗 Installation

git clone https://github.com/sandana-s/invoice_extraction.git
cd invoice-extraction-app
pip install -r requirements.txt


OPENAI_API_KEY="your_openai_api_key_here"

-python app.py

## Project Structure

|-- app.py
|-- README.md
|-- requirements.txt
|-- .env


|-- .env (ignored - created by user)



