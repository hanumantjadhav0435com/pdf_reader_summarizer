# PDF Chat Assistant

## Overview

This is a Flask-based web application that enables users to upload PDF documents and engage in conversational interactions with the content using Google's Gemini AI. Users can ask questions about uploaded PDFs and receive intelligent responses based on the document's content.

## System Architecture

The application follows a traditional client-server architecture with the following components:

- **Frontend**: HTML/CSS/JavaScript with Bootstrap for responsive UI
- **Backend**: Flask web framework with Python
- **Database**: SQLAlchemy ORM with SQLite (configurable to other databases via DATABASE_URL)
- **AI Integration**: Google Gemini API for natural language processing
- **File Processing**: PyPDF2 for PDF text extraction and chunking

## Key Components

### Backend Components

1. **Flask Application** (`app.py`)
   - Main application entry point
   - Handles file uploads with 16MB size limit
   - Manages session state and routing
   - Configures SQLAlchemy for database operations

2. **PDF Processing** (`pdf_processor.py`)
   - Extracts text from PDF files using PyPDF2
   - Implements text chunking strategy (1000 char chunks with 200 char overlap)
   - Handles text cleaning and preprocessing
   - Tracks page numbers for source attribution

3. **AI Chat Integration** (`gemini.py`)
   - Interfaces with Google Gemini 2.5 Flash model
   - Implements context-aware question answering
   - Provides source attribution for responses
   - Uses simple keyword matching for chunk relevance

4. **Database Models** (`models.py`)
   - `ChatSession`: Tracks upload sessions and associated files
   - `ChatMessage`: Stores conversation history with timestamps

### Frontend Components

1. **User Interface** (`templates/index.html`)
   - Single-page application with dark theme
   - Drag-and-drop file upload interface
   - Real-time chat interface
   - Source citation sidebar

2. **JavaScript Client** (`static/app.js`)
   - Handles file upload with progress tracking
   - Manages WebSocket-style chat interactions
   - Implements drag-and-drop functionality
   - Provides error handling and user feedback

3. **Styling** (`static/style.css`)
   - Custom styles extending Bootstrap dark theme
   - Responsive design for multiple screen sizes
   - Smooth animations and transitions

## Data Flow

1. **File Upload Process**:
   - User uploads PDF via drag-and-drop or file picker
   - File validation (PDF format, size limits)
   - PDF text extraction and chunking
   - Session creation with unique identifier
   - Text chunks stored for later retrieval

2. **Chat Interaction**:
   - User submits question through chat interface
   - System retrieves relevant text chunks using keyword matching
   - Context and question sent to Gemini API
   - AI response processed and returned with source citations
   - Conversation stored in database for session persistence

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and request handling
- **SQLAlchemy**: Database ORM and management
- **PyPDF2**: PDF text extraction
- **Google Genai**: Gemini AI API integration
- **Bootstrap**: Frontend UI framework
- **Font Awesome**: Icon library

### Environment Variables Required
- `GEMINI_API_KEY`: Google Gemini API authentication
- `SESSION_SECRET`: Flask session encryption key
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)

## Deployment Strategy

The application is configured for deployment on Replit with the following considerations:

- **ProxyFix Middleware**: Handles reverse proxy headers for proper request handling
- **Environment Configuration**: Uses environment variables for sensitive data
- **File Storage**: Local file system for PDF uploads (uploads/ directory)
- **Database**: SQLite by default, easily configurable for PostgreSQL or other databases
- **Logging**: Debug-level logging enabled for development

## Changelog

- July 04, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.