import streamlit as st
from transformers import pipeline
import pdfplumber

# Initialize the QA pipeline
def initialize_qa_model():
    return pipeline('question-answering', model="deepset/roberta-base-squad2")

# Extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# Ask a question based on the extracted text
def ask_question(qa_pipeline, context, question):
    if not context:
        return "Please load a PDF first."
    try:
        result = qa_pipeline(question=question, context=context)
        return result['answer'] or "Sorry, I couldn't find an answer in the document."
    except Exception as e:
        return f"An error occurred: {e}"

# Main function to run the Streamlit app
def main():
    st.title("AskYourPDF")

    # Upload PDF file
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    # Initialize session state for messages and context
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "context" not in st.session_state:
        st.session_state.context = ""

    # If a PDF is uploaded, extract text and store it in session state
    if uploaded_file:
        st.session_state.context = extract_text_from_pdf(uploaded_file)
        st.success("PDF loaded successfully!")

    # Display chat history
    for message in st.session_state.messages:
        role, content = message["role"], message["content"]
        st.markdown(f"**{role.capitalize()}:** {content}")

    # Input for user question
    question = st.text_input("Ask a question:")
    if st.button("Send") and question:
        # Add user question to chat history
        st.session_state.messages.append({"role": "user", "content": question})

        # Initialize QA model
        qa_pipeline = initialize_qa_model()

        # Get answer from the QA model
        answer = ask_question(qa_pipeline, st.session_state.context, question)

        # Add bot response to chat history
        st.session_state.messages.append({"role": "bot", "content": answer})

        # Display the latest question and answer
        st.markdown(f"**User:** {question}")
        st.markdown(f"**Bot:** {answer}")

# Run the app
if __name__ == "__main__":
    main()