# import logging
# import google.generativeai as genai  # ✅ Use the correct import

# # ✅ Configure directly with API key (older SDKs don't expose genai.configure)
# genai.configure(api_key="AIzaSyAKiKWyZ7W7dR3sCYMAfQyOTICrvA4vGEg")

# class PDFChatClient:
#     def __init__(self):
#         self.model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        
#     def chat_with_pdf(self, question, text_chunks):
#         """
#         Chat with PDF content using Gemini API.
#         Returns response with answer and relevant sources.
#         """
#         try:
#             # Find most relevant chunks
#             relevant_chunks = self._find_relevant_chunks(question, text_chunks)

#             # Prepare context from top 5 relevant chunks
#             context = "\n\n".join([chunk['text'] for chunk in relevant_chunks[:5]])

#             # Build prompt
#             prompt = f"""You are an AI assistant helping users understand a PDF document. 
# Based on the following context from the document, please answer the user's question accurately and helpfully.

# Context from PDF:
# {context}

# User Question: {question}

# Please provide a comprehensive answer based on the context provided. If the question cannot be answered from the given context, please say so clearly."""

#             # Generate response
#             response = self.model.generate_content(prompt)

#             if not response.text:
#                 raise Exception("Empty response from Gemini API")

#             return {
#                 'answer': response.text,
#                 'sources': relevant_chunks[:3]
#             }

#         except Exception as e:
#             logging.error(f"Gemini chat error: {str(e)}")
#             raise Exception(f"Failed to get response from AI: {str(e)}")

#     def _find_relevant_chunks(self, question, text_chunks):
#         """
#         Basic keyword matching for chunk relevance.
#         """
#         question_words = set(question.lower().split())
#         scored_chunks = []

#         for chunk in text_chunks:
#             chunk_words = set(chunk['text'].lower().split())
#             score = len(question_words.intersection(chunk_words))

#             if score > 0:
#                 scored_chunks.append({
#                     'text': chunk['text'],
#                     'page': chunk['page'],
#                     'score': score
#                 })

#         scored_chunks.sort(key=lambda x: x['score'], reverse=True)
#         return scored_chunks if scored_chunks else text_chunks[:3]
# pdf_chat.py

import logging
import google.generativeai as genai
import os

# ✅ Use API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("Missing GEMINI_API_KEY in environment variables.")

genai.configure(api_key=API_KEY)


class PDFChatClient:
    def __init__(self):
        self.model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

    def chat_with_pdf(self, question, text_chunks):
        """
        Chat with PDF content using Gemini API.
        Returns response with answer and relevant sources.
        """
        try:
            # Find most relevant chunks
            relevant_chunks = self._find_relevant_chunks(question, text_chunks)

            # Prepare context from top 5 relevant chunks
            context = "\n\n".join([chunk['text'] for chunk in relevant_chunks[:5]])

            # Build prompt
            prompt = f"""You are an AI assistant helping users understand a PDF document. 
Based on the following context from the document, please answer the user's question accurately and helpfully.

Context from PDF:
{context}

User Question: {question}

Please provide a comprehensive answer based on the context provided. 
If the question cannot be answered from the given context, please say so clearly."""

            # Generate response
            response = self.model.generate_content(prompt)

            if not response.text:
                raise Exception("Empty response from Gemini API")

            return {
                'answer': response.text,
                'sources': relevant_chunks[:3]
            }

        except Exception as e:
            logging.error(f"Gemini chat error: {str(e)}")
            raise Exception(f"Failed to get response from AI: {str(e)}")

    def _find_relevant_chunks(self, question, text_chunks):
        """
        Basic keyword matching for chunk relevance.
        """
        question_words = set(question.lower().split())
        scored_chunks = []

        for chunk in text_chunks:
            chunk_words = set(chunk['text'].lower().split())
            score = len(question_words.intersection(chunk_words))

            if score > 0:
                scored_chunks.append({
                    'text': chunk['text'],
                    'page': chunk['page'],
                    'score': score
                })

        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        return scored_chunks if scored_chunks else text_chunks[:3]
