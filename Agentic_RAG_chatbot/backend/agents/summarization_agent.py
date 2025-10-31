from backend.core.llm_clients import llm_client

class SummarizationAgent:
    def __init__(self, faiss_store):
        self.faiss_store = faiss_store
        self.name = "Summarization Agent"
    
    async def process(self, query: str, full_text: str) -> str:
        """Generate a summary of the document."""
        
        # Determine summary type from query
        if "brief" in query.lower() or "short" in query.lower():
            summary_length = "brief (3-4 sentences)"
            max_chars = 3000
        elif "detailed" in query.lower() or "comprehensive" in query.lower():
            summary_length = "detailed and comprehensive"
            max_chars = 8000
        else:
            summary_length = "moderate (1-2 paragraphs)"
            max_chars = 5000
        
        # Truncate text if too long to avoid context limits
        if len(full_text) > max_chars:
            text_to_summarize = full_text[:max_chars] + "..."
        else:
            text_to_summarize = full_text
        
        system_prompt = f"""You are an expert at creating {summary_length} summaries. 
Your summaries should:
1. Capture the main ideas and key points
2. Be written in a clear, engaging style
3. Flow naturally and be easy to read
4. Highlight important themes, characters, or concepts
5. Be coherent and well-structured"""

        prompt = f"""Please provide a {summary_length} summary of the following document:

{text_to_summarize}

Summary:"""

        try:
            response = await llm_client.generate(prompt, system_prompt=system_prompt)
            
            if not response:
                return "I apologize, but I couldn't generate a summary. Please try again."
            
            return response
        
        except Exception as e:
            return f"Error generating summary: {str(e)}. Make sure Ollama is running."