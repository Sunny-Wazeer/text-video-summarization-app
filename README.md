# Project Name: Text and YouTube Video Summarization App
This project is a Flask-based web application designed to summarize text from YouTube videos, PDFs, and plain text files. It integrates machine learning models like Pegasus for summarization and uses YouTubeTranscriptApi for fetching transcripts from YouTube. Additionally, it supports translation of transcripts from Hindi/Urdu to English and provides summaries in both English and Urdu.
# Key Components:
Flask: Powers the web framework, managing routes, user sessions, and form handling.
SQLAlchemy: Used for database management, including user authentication (registration and login).
Pegasus (Transformers): Generates summaries of the text, using a pre-trained Pegasus model.
YouTubeTranscriptApi: Fetches transcripts for YouTube videos, handling multiple languages.
Google Translate: Automatically translates Hindi and Urdu transcripts to English for summarization.
