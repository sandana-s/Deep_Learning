\# 🧾 Invoice Extraction App (Multi-Agent AI)



This is a Multi-Agent AI application that extracts invoice details from uploaded files and converts them into structured \*\*JSON output\*\*. It supports \*\*Images (OCR)\*\*, \*\*DOCX\*\*, and \*\*plain text\*\* files.



---



\## 🚀 Features



\- 🖼 Image OCR using GPT-4o-mini Vision

\- 📄 Reads DOCX \& text files

\- 🌍 Detects language \& auto-translation to English

\- 🔍 Extracts fields:

&nbsp; - invoice\_number

&nbsp; - date

&nbsp; - vendor

&nbsp; - total

\- 🤖 Multi-agent pipeline for better accuracy

\- ✅ Gradio Web UI for easy usage



---



\## 📥 Input → Output Workflow



1️⃣ Extract Text  

2️⃣ Detect \& Translate Language  

3️⃣ Extract JSON invoice details  



Example Output:

{

&nbsp; "invoice\_number": "INV-1029",

&nbsp; "date": "2025-10-21",

&nbsp; "vendor": "ABC Supplies",

&nbsp; "total": "$1299.55"

}



\# 🏗 Installation



-git clone <https://github.com/sandana-s/invoice\_extraction.git>



-cd invoice-extraction-app



-pip install -r requirements.txt



OPENAI\_API\_KEY="your\_openai\_api\_key\_here"



-python app.py



\## Project Structure



|-- app.py



|-- README.md



|-- requirements.txt



|-- .env (ignored - created by user)



