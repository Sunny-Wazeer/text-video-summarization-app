from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript
from googletrans import Translator
import re

app = Flask(__name__)
app.secret_key = 'sunnyl3l'  # Set your secret key for session management

# Construct the full path to the database file within the 'instance' directory
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'users.db')

# Set the SQLAlchemy Database URI to use the constructed path
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Load the Pegasus model and tokenizer
model = PegasusForConditionalGeneration.from_pretrained("FYPFINAL/pegasus-samsum-model")
tokenizer = PegasusTokenizer.from_pretrained("FYPFINAL/Tokenizer")

# Create the database tables
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

with app.app_context():
    db.create_all()

def chunk_text(text, max_chunk_length):
    words = text.split()
    chunks = [' '.join(words[i:i + max_chunk_length]) for i in range(0, len(words), max_chunk_length)]
    return chunks

def generate_summary(text, chunk_size=500):
    chunks = chunk_text(text, chunk_size)
    summaries = []
    for chunk in chunks:
        inputs = tokenizer([chunk], max_length=512, return_tensors='pt', truncation=True)
        summary_ids = model.generate(inputs['input_ids'], max_length=150, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summaries.append(summary)
    combined_summary = ' '.join(summaries)
    return combined_summary

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

#---------------------------------------------------------------
#---------------------------------------------------------------
#-------------------------VIDEO SUMMARY-------------------------
#---------------------------------------------------------------
#---------------------------------------------------------------

# Load all environment variables
load_dotenv()

# Function to extract YouTube video ID from different formats of YouTube URLs
def extract_video_id(youtube_url):
    video_id_match = re.search(r'(v=|\/)([a-zA-Z0-9_-]{11})', youtube_url)
    if video_id_match:
        return video_id_match.group(2)
    else:
        return None

# Getting the transcript data from YouTube videos
def extract_transcript_details(youtube_video_url, lang):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            return None

        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        return transcript_text
    except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript) as e:
        return None

# Combine the transcript segments into a single string
def combine_transcript(transcript_text):
    return " ".join([i["text"] for i in transcript_text])

# Translate the transcript to English if it is in Hindi or Urdu
def translate_transcript(transcript_text, source_lang, target_lang='en'):
    try:
        translator = Translator()
        translated = translator.translate(transcript_text, src=source_lang, dest=target_lang)
        return translated.text
    except Exception as e:
        return None

# Convert plain text summary into HTML bullet points
def format_summary_to_html(summary_text):
    points = summary_text.split("*")
    html_summary = "<ul>"
    for point in points:
        if point.strip():
            html_summary += f"<li>{point.strip()}</li>"
    html_summary += "</ul>"
    return html_summary

@app.route('/video', methods=['GET', 'POST'])
def videosummary():
    if request.method == 'POST':
        youtube_link = request.form['youtube_link']
        transcript_lang = request.form['transcript_lang']
        
        video_id = extract_video_id(youtube_link)
        if not video_id:
            return render_template('videosummary.html', error="Invalid YouTube URL")
        
        transcript_segments = extract_transcript_details(youtube_link, transcript_lang)
        if not transcript_segments:
            return render_template('videosummary.html', error="Error fetching transcript")

        transcript_text = combine_transcript(transcript_segments)

        if transcript_lang in ['hi', 'ur']:
            transcript_text = translate_transcript(transcript_text, transcript_lang, 'en')

        if transcript_text:
            summary = generate_summary(transcript_text)
            if summary:
                formatted_summary = format_summary_to_html(summary)
                urdu_translator = Translator()
                urdu_summary = urdu_translator.translate(summary, src='en', dest='ur').text
                formatted_urdu_summary = format_summary_to_html(urdu_summary)
                return render_template('videosummary.html', summary=formatted_summary, urdu_summary=formatted_urdu_summary, video_id=video_id)
            else:
                return render_template('videosummary.html', error="Error generating summary")
    return render_template('videosummary.html')

#---------------------------------------------------------------
#---------------------------------------------------------------
#--------------------------------ROUTES-------------------------
#---------------------------------------------------------------
#---------------------------------------------------------------

@app.route('/about')
def about():
    return render_template("aboutus.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/video')
def video():
    return render_template('videosummary.html')

@app.route('/text')
def text():
    return render_template('textsummary.html')

@app.route('/')
def home():
    if 'user_id' not in session:
        return render_template('home.html', form_type = "nologin")
    return render_template('home.html', username=session['username'], form_type = "login")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful, please log in', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('There was an issue adding your registration', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return render_template('textsummary.html', form_type="login")
        else:
            flash('Login unsuccessful. Please check your email and password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return render_template('home.html',form_type = "nologin")

@app.route('/summary', methods=['POST'])
def get_summary():
    text = request.form.get('text', '')
    file = request.files.get('file')

    if file and (file.filename.endswith('.txt') or file.filename.endswith('.pdf')):
        if file.filename.endswith('.txt'):
            text = file.read().decode('utf-8')
        elif file.filename.endswith('.pdf'):
            # Ensure the 'temp' directory exists
            if not os.path.exists('temp'):
                os.makedirs('temp')

            file_path = os.path.join("temp", file.filename)
            file.save(file_path)
            text = extract_text_from_pdf(file_path)
            os.remove(file_path)

    if text.strip():
        summary = generate_summary(text)
        return render_template('textsummary.html', text=text, summary=summary)
    else:
        error_message = "Please provide some text or upload a file."
        return render_template('textsummary.html', error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
