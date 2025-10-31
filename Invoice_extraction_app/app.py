"""
Invoice Extraction App - Multi-Agent Pipeline
---------------------------------------------
Features:
- Supports images (OCR with GPT-4o-mini vision), .docx, and plain text.
- Multi-agent workflow:
  1. Extract text
  2. Detect language + translate if needed
  3. Extract structured invoice fields into JSON
- OpenAI key loaded from .env .
"""

import os
import base64
from dotenv import load_dotenv
import gradio as gr
from openai import OpenAI
from docx import Document

# ===============================
# 1. Load API key
# ===============================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI key not found. Add it to your .env file.")

client = OpenAI(api_key=OPENAI_API_KEY)


# ===============================
# 2. Extract text from input files
# ===============================
def extract_text_from_docx(docx_path):
    """Extract text from a .docx file."""
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()


def extract_text_from_image(image_path):
    """Extract text from an image file using GPT-4o-mini vision."""
    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()
    b64_image = base64.b64encode(img_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an OCR agent. Extract all text from the image."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all invoice text."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
                ],
            },
        ],
    )
    return response.choices[0].message.content


def extract_text(input_path, input_type="text"):
    """Extract text based on input type."""
    if input_type == "text":
        with open(input_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    elif input_type == "docx":
        return extract_text_from_docx(input_path)
    elif input_type == "image":
        return extract_text_from_image(input_path)
    else:
        raise ValueError("Unsupported input type.")


# ===============================
# 3. Agents
# ===============================
class Agent:
    def __init__(self, name, instructions, model="gpt-4o-mini"):
        self.name = name
        self.instructions = instructions
        self.model = model

    def run(self, text):
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.instructions},
                {"role": "user", "content": text},
            ],
            temperature=0,
        )
        return response.choices[0].message.content


# ===============================
# 4. Define Agents
# ===============================
# Language detection + translation
lang_agent = Agent(
    "Language Agent",
    instructions="Detect the language of the text. If it is not English, translate it into English. Output only the translated or original English text.",
)

# Invoice field extractor
extraction_agent = Agent(
    "Extraction Agent",
    instructions=(
        "You are an invoice extraction agent. Extract the following fields in JSON format: "
        "invoice_number, date, vendor, total. If missing, use null. Return ONLY valid JSON."
    ),
)


# ===============================
# 5. Orchestration Agent
# ===============================
def orchestration_agent(input_path, input_type="text"):
    raw_text = extract_text(input_path, input_type)
    english_text = lang_agent.run(raw_text)
    result = extraction_agent.run(english_text)
    return raw_text, english_text, result


# ===============================
# 6. Gradio UI
# ===============================
def process_file(file, file_type):
    if not file:
        return "No file uploaded", "", "{}"
    raw, english, json_out = orchestration_agent(file, file_type)
    return raw, english, json_out


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🧾 Invoice Extraction App (Multi-Agent AI)")
    gr.Markdown("Upload an invoice (Image, DOCX, or Text) and get structured JSON output.")

    with gr.Row():
        file_input = gr.File(label="Upload Invoice File")
        file_type = gr.Dropdown(choices=["image", "docx", "text"], value="image", label="File Type")

    extract_btn = gr.Button("Extract Invoice")

    with gr.Row():
        raw_text_box = gr.Textbox(label="Raw Extracted Text", lines=10)
        english_text_box = gr.Textbox(label="Translated/English Text", lines=10)
        json_output_box = gr.Textbox(label="Structured JSON", lines=10)

    extract_btn.click(process_file, inputs=[file_input, file_type], outputs=[raw_text_box, english_text_box, json_output_box])


if __name__ == "__main__":
    demo.launch()
