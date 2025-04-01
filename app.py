from flask import Flask, request, jsonify, send_from_directory
import os
import pandas as pd
from PyPDF2 import PdfReader
import re
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)



# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'your-mail'  # Replace with your email
SENDER_PASSWORD = 'your-password'  # Replace with your email password

# SQLite Database setup
DATABASE = 'recruitment.db'

# Function to send email
def send_email(recipient_email, subject, body):
    try:
        # Create a multipart message and set headers
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))

        # Establish connection with Gmail's SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Send email
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to extract text from PDF (CV)
def extract_text_from_pdf(cv_path):
    try:
        with open(cv_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting CV text: {e}"

# Function to extract text from CSV (Job Description)
def extract_text_from_csv(jd_path):
    try:
        jd_df = pd.read_csv(jd_path, encoding='ISO-8859-1')
        jd_df.dropna(axis=0, how='all', inplace=True)
        jd_df.dropna(axis=1, how='all', inplace=True)
        jd_text = jd_df.to_string(index=False, header=False)
        jd_text = jd_text.replace("\u0092", "'")
        return jd_text
    except Exception as e:
        return f"Error extracting JD text: {e}"

# Preprocessing function to clean the text
def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = text.lower()  # Convert text to lowercase
    return text

# List of common skills
skills_list = [
    "java", "python", "sql", "javascript", "html", "css", "c++", "react", "nodejs", "aws", 
    "docker", "kubernetes", "azure", "machine learning", "data science", "deep learning", 
    "devops", "android", "flutter", "java spring", "c", "ruby", "mysql", "mongodb", "power bi"
]

# Function to extract skills from text
def extract_skills(text):
    processed_text = preprocess_text(text)
    skills_found = [skill for skill in skills_list if skill in processed_text]
    return skills_found

# Function to match skills between CV and JD
def match_skills(cv_text, jd_text):
    cv_skills = extract_skills(cv_text)
    jd_skills = extract_skills(jd_text)
    matching_skills = list(set(cv_skills) & set(jd_skills))  # Intersection
    return matching_skills

# Function to calculate the match score (e.g., based on number of matching skills)
def calculate_match_score(matching_skills, total_skills_in_jd):
    return len(matching_skills) / len(total_skills_in_jd) * 100

# Function to extract email from CV text using regex
def extract_email_from_text(cv_text):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email = re.findall(email_regex, cv_text)
    return email[0] if email else None  # Return the first email found or None if no email is found

# Function to create and initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Drop the table if it already exists (only for testing purposes, you can remove this in production)
    c.execute('DROP TABLE IF EXISTS candidates')
    
    # Create the candidates table with the match_score column
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            match_score REAL,
            skills TEXT,
            jd_text TEXT,
            cv_text TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert candidate information into the database
def insert_candidate(name, email, match_score, skills, jd_text, cv_text):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(''' 
        INSERT INTO candidates (name, email, match_score, skills, jd_text, cv_text)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, email, match_score, ', '.join(skills), jd_text, cv_text))
    conn.commit()
    conn.close()

@app.route('/upload', methods=['POST'])
def upload_files():
    cv_file = request.files['cv']
    jd_file = request.files['jd']
    
    # Ensure that the 'uploads' directory exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    cv_path = os.path.join('uploads', cv_file.filename)
    jd_path = os.path.join('uploads', jd_file.filename)
    
    # Save the uploaded files
    cv_file.save(cv_path)
    jd_file.save(jd_path)
    
    # Log file paths
    print(f"CV file saved at: {cv_path}")
    print(f"JD file saved at: {jd_path}")
    
    # Extract text from the uploaded CV and JD
    cv_text = extract_text_from_pdf(cv_path)
    jd_text = extract_text_from_csv(jd_path)
    
    # Match skills between CV and JD
    matching_skills = match_skills(cv_text, jd_text)
    
    # Calculate match score
    match_score = calculate_match_score(matching_skills, skills_list)

    # Extract the email from the CV text
    recipient_email = extract_email_from_text(cv_text)

    if recipient_email:
        # Send email if candidate is shortlisted
        if match_score >= 80:
            subject = "Interview Invitation"
            body = f"Dear Candidate,\n\nWe are pleased to inform you that your application for the position has been shortlisted based on a match score of {match_score:.2f}%.\n\nPlease let us know your availability for the interview.\n\nBest regards,\nRecruitment Team"
            send_email(recipient_email, subject, body)
            message = f"Email sent to {recipient_email}."
        else:
            message = "Match score below threshold. No email sent."
    else:
        message = "No email address found in CV."
    
    # Store candidate details in the database
    insert_candidate("Candidate", recipient_email, match_score, matching_skills, jd_text, cv_text)
    
    return jsonify({
        "cv_text": cv_text, 
        "jd_text": jd_text,
        "matching_skills": matching_skills,
        "match_score": match_score,
        "message": message
    })

# Serve uploaded files for testing
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    # Initialize the database
    init_db()
    
    # Start Flask app
    app.run(debug=True)
