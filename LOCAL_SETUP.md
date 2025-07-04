# Local Setup Guide

This guide will help you run the PDF Chat Assistant application on your local system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation Steps

### 1. Clone or Download the Project

Download all the project files to your local machine.

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv pdf_chat_env

# Activate virtual environment
# On Windows:
pdf_chat_env\Scripts\activate
# On macOS/Linux:
source pdf_chat_env/bin/activate
```

### 3. Install Dependencies

Create a `requirements.txt` file with the following content:

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.23
PyPDF2==3.0.1
google-genai==0.8.0
gunicorn==21.2.0
Werkzeug==3.0.1
email-validator==2.1.0
python-dotenv==1.0.0
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root directory with:

```env
# Gemini API Key - Get from https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Session secret for Flask (generate a random string)
SESSION_SECRET=your_very_secret_random_string_here

# Database URL (optional, defaults to SQLite)
DATABASE_URL=sqlite:///chat.db
```

### 5. Get Your Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key and add it to your `.env` file

### 6. Run the Application

You can run the application in two ways:

#### Option A: Using Python directly
```bash
python main.py
```

#### Option B: Using Gunicorn (production-like)
```bash
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

### 7. Access the Application

Open your web browser and go to:
```
http://localhost:5000
```

## Project Structure

```
pdf-chat-assistant/
├── app.py              # Main Flask application
├── main.py             # Application entry point
├── models.py           # Database models
├── pdf_processor.py    # PDF text extraction and chunking
├── gemini.py          # Gemini AI integration
├── templates/
│   └── index.html     # Main web interface
├── static/
│   ├── app.js         # Frontend JavaScript
│   └── style.css      # Custom styles
├── uploads/           # PDF upload directory
├── .env               # Environment variables (create this)
├── requirements.txt   # Python dependencies (create this)
└── LOCAL_SETUP.md     # This file
```

## Features

- **Drag & Drop PDF Upload**: Easy file uploading interface
- **AI-Powered Chat**: Ask questions about your PDF content
- **Source Citations**: See relevant excerpts from your document
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Processing**: Instant responses powered by Gemini AI

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've activated your virtual environment and installed all dependencies.

2. **API Key Issues**: Ensure your Gemini API key is valid and properly set in the `.env` file.

3. **PDF Processing Errors**: Make sure your PDF contains readable text (not just images).

4. **Port Already in Use**: If port 5000 is busy, change the port in `main.py`:
   ```python
   app.run(host='0.0.0.0', port=5001, debug=True)
   ```

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Ensure all dependencies are installed correctly
3. Verify your API key is working at https://aistudio.google.com/
4. Make sure the `uploads/` directory exists and is writable

## Production Deployment

For production deployment:
1. Set `debug=False` in `main.py`
2. Use a production database (PostgreSQL recommended)
3. Set proper environment variables
4. Use a reverse proxy like Nginx
5. Consider using Docker for containerization

## License

This project is open source and available for modification and distribution.