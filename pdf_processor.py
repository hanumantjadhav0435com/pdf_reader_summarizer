import PyPDF2
import logging
import re
from typing import List, Dict

class PDFProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_and_chunk_text(self, pdf_path: str) -> List[Dict]:
        """
        Extract text from PDF and split into manageable chunks
        Returns list of dictionaries with text, page number, and chunk info
        """
        try:
            chunks = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if len(pdf_reader.pages) == 0:
                    raise Exception("PDF has no pages")
                
                full_text = ""
                page_texts = []
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            page_texts.append({
                                'text': page_text,
                                'page': page_num + 1
                            })
                            full_text += f"\n\nPage {page_num + 1}:\n{page_text}"
                    except Exception as e:
                        logging.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                        continue
                
                if not full_text.strip():
                    raise Exception("No readable text found in PDF")
                
                # Clean the text
                cleaned_text = self._clean_text(full_text)
                
                # Create chunks
                chunks = self._create_chunks(cleaned_text, page_texts)
                
                logging.info(f"Extracted {len(chunks)} chunks from PDF with {len(pdf_reader.pages)} pages")
                return chunks
                
        except Exception as e:
            logging.error(f"PDF processing error: {str(e)}")
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove weird characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\(\)\-\'\"]+', ' ', text)
        # Remove excessive spaces
        text = re.sub(r' +', ' ', text)
        return text.strip()
    
    def _create_chunks(self, text: str, page_texts: List[Dict]) -> List[Dict]:
        """Split text into overlapping chunks"""
        chunks = []
        words = text.split()
        
        if len(words) <= self.chunk_size:
            # If text is shorter than chunk size, return as single chunk
            return [{
                'text': text,
                'page': self._get_page_for_text(text, page_texts),
                'chunk_index': 0
            }]
        
        start = 0
        chunk_index = 0
        
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            # Determine which page this chunk primarily comes from
            page_num = self._get_page_for_text(chunk_text, page_texts)
            
            chunks.append({
                'text': chunk_text,
                'page': page_num,
                'chunk_index': chunk_index
            })
            
            # Move start forward, considering overlap
            start = end - self.chunk_overlap
            chunk_index += 1
            
            # Prevent infinite loop
            if start >= end:
                break
        
        return chunks
    
    def _get_page_for_text(self, chunk_text: str, page_texts: List[Dict]) -> int:
        """Determine which page a chunk of text primarily comes from"""
        best_page = 1
        max_overlap = 0
        
        # Simple approach: find page with most word overlap
        chunk_words = set(chunk_text.lower().split()[:50])  # Use first 50 words for matching
        
        for page_info in page_texts:
            page_words = set(page_info['text'].lower().split())
            overlap = len(chunk_words.intersection(page_words))
            
            if overlap > max_overlap:
                max_overlap = overlap
                best_page = page_info['page']
        
        return best_page
