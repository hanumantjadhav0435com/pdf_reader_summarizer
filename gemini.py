import json
import logging
import os
from google import genai
from google.genai import types

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class PDFChatClient:
    def __init__(self):
        self.model = "gemini-2.5-flash"
        
    def chat_with_pdf(self, question, text_chunks):
        """
        Chat with PDF content using Gemini API
        Returns response with answer and relevant sources
        """
        try:
            # Find most relevant chunks (simple keyword matching for now)
            relevant_chunks = self._find_relevant_chunks(question, text_chunks)
            
            # Prepare context from relevant chunks
            context = "\n\n".join([chunk['text'] for chunk in relevant_chunks[:5]])  # Limit to 5 chunks
            
            # Create prompt
            prompt = f"""You are an AI assistant helping users understand a PDF document. 
            Based on the following context from the document, please answer the user's question accurately and helpfully.
            
            Context from PDF:
            {context}
            
            User Question: {question}
            
            Please provide a comprehensive answer based on the context provided. If the question cannot be answered from the given context, please say so clearly."""
            
            # Get response from Gemini
            response = client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if not response.text:
                raise Exception("Empty response from Gemini API")
            
            return {
                'answer': response.text,
                'sources': relevant_chunks[:3]  # Return top 3 relevant chunks as sources
            }
            
        except Exception as e:
            logging.error(f"Gemini chat error: {str(e)}")
            raise Exception(f"Failed to get response from AI: {str(e)}")
    
    def _find_relevant_chunks(self, question, text_chunks):
        """
        Simple relevance scoring based on keyword matching
        In a production app, you'd use semantic similarity/embeddings
        """
        question_words = set(question.lower().split())
        scored_chunks = []
        
        for chunk in text_chunks:
            chunk_words = set(chunk['text'].lower().split())
            # Simple scoring: count of matching words
            score = len(question_words.intersection(chunk_words))
            
            if score > 0:
                scored_chunks.append({
                    'text': chunk['text'],
                    'page': chunk['page'],
                    'score': score
                })
        
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        # If no keyword matches, return first few chunks
        if not scored_chunks:
            return text_chunks[:3]
        
        return scored_chunks
