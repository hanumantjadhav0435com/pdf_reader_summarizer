import os
import logging
from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import uuid
from pdf_processor import PDFProcessor
from gemini import PDFChatClient

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB limit

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///chat.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize processors
pdf_processor = PDFProcessor()
chat_client = PDFChatClient()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(filepath)
        
        # Process PDF
        try:
            text_chunks = pdf_processor.extract_and_chunk_text(filepath)
            if not text_chunks:
                os.remove(filepath)  # Clean up
                return jsonify({'error': 'Could not extract text from PDF. Please ensure it contains readable text.'}), 400
            
            # Store in session
            session_id = str(uuid.uuid4())
            session[session_id] = {
                'filename': filename,
                'filepath': filepath,
                'chunks': text_chunks
            }
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'filename': filename,
                'chunks_count': len(text_chunks)
            })
            
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)  # Clean up on error
            logging.error(f"PDF processing error: {str(e)}")
            return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500
            
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed. Please try again.'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data or 'session_id' not in data:
            return jsonify({'error': 'Missing message or session_id'}), 400
        
        session_id = data['session_id']
        message = data['message'].strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if session_id not in session:
            return jsonify({'error': 'Session not found. Please upload a PDF first.'}), 404
        
        pdf_data = session[session_id]
        chunks = pdf_data['chunks']
        
        # Get response from Gemini
        try:
            response = chat_client.chat_with_pdf(message, chunks)
            return jsonify({
                'response': response['answer'],
                'sources': response['sources']
            })
        except Exception as e:
            logging.error(f"Gemini API error: {str(e)}")
            return jsonify({'error': 'Failed to get response from AI. Please try again.'}), 500
            
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return jsonify({'error': 'Chat request failed. Please try again.'}), 500

@app.route('/clear_session', methods=['POST'])
def clear_session():
    try:
        data = request.get_json()
        session_id = data.get('session_id') if data else None
        
        if session_id and session_id in session:
            pdf_data = session[session_id]
            # Clean up uploaded file
            if 'filepath' in pdf_data and os.path.exists(pdf_data['filepath']):
                os.remove(pdf_data['filepath'])
            # Remove from session
            del session[session_id]
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Clear session error: {str(e)}")
        return jsonify({'error': 'Failed to clear session'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
