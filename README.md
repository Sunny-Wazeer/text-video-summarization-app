# Project Name: Text and YouTube Video Summarization App
This project is a Flask-based web application designed to summarize text from YouTube videos, PDFs, and plain text files. It integrates machine learning models like Pegasus for summarization and uses YouTubeTranscriptApi for fetching transcripts from YouTube. Additionally, it supports translation of transcripts from Hindi/Urdu to English and provides summaries in both English and Urdu.
# Key Components:
Flask: Powers the web framework, managing routes, user sessions, and form handling.
SQLAlchemy: Used for database management, including user authentication (registration and login).
Pegasus (Transformers): Generates summaries of the text, using a pre-trained Pegasus model.
YouTubeTranscriptApi: Fetches transcripts for YouTube videos, handling multiple languages.
Google Translate: Automatically translates Hindi and Urdu transcripts to English for summarization.

# 📝 Text and YouTube Video Summarization App

A full-stack web application that generates abstractive summaries from text input, PDF files, and YouTube videos. Built using Flask for the backend and HTML/CSS for the frontend, this app integrates a **fine-tuned Pegasus transformer model** to produce high-quality summaries. It supports multi-language transcripts, user authentication, and responsive design.

---

## Features

- 🔐 User registration and login system using Flask + SQLAlchemy
- 📄 Summarization of raw text, `.txt`, and `.pdf` files
- 📹 YouTube transcript support (multilingual)
- 🌐 Translation from Hindi/Urdu to English (via Google Translate API)
- 🧠 Abstractive summarization using a **custom fine-tuned Pegasus model**
- 🌍 Multilingual interface support (summary returned in English and Urdu)
- 💻 Responsive and user-friendly frontend

---

## Model Fine-Tuning

This app uses a **custom fine-tuned Pegasus model** trained on dialogue-based datasets to better understand conversational patterns and produce concise summaries.
Fine-tuned using the SAMSum dataset for summarizing conversations
Model and tokenizer stored locally in the FYPFINAL/ directory

# Code Overview (app.py)
1. Setup & Config
Initializes Flask app and SQLAlchemy

Loads Pegasus model and tokenizer

Sets the database location: instance/users.db

# 2. User Authentication
/register – creates new users (with hashed passwords)

/login – logs in existing users, using email/password

/logout – logs users out

# 3. Utility Functions
extract_text_from_pdf(path) – uses PyMuPDF to extract text from uploaded PDFs

chunk_text(text, n) – splits long text into chunks for the model

generate_summary(text) – summarizes each chunk using the Pegasus model

# 4. Routes
/ – main home page with login check

/summary – processes the uploaded file or user text and generates the summary

/about & /contact – static info pages

#  Frontend
Built with basic HTML/CSS and Flask templating:

Includes file input, textarea, and output summary block

Conditional login/logout buttons using Jinja2 templating

Integrated with Font Awesome for copy-to-clipboard functionality

# 5. Install dependencies
pip install -r requirements.txt
4. Run the application
python app.py


# ✅ Requirements
Python 3.7+
Flask
SQLAlchemy
Transformers (Hugging Face)
PyMuPDF (fitz)
Werkzeug (for password hashing)

