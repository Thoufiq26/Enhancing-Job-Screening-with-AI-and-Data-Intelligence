# Enhancing-Job-Screening-with-AI-and-Data-Intelligence

-Overview
Smart Recruiter is an AI-powered solution that automates the process of matching resumes (CVs) with job descriptions (JDs). The system extracts key skills from both the CV and the JD, compares them, calculates a match score, and provides feedback to the recruiter. It also sends email notifications to candidates whose resumes meet the match criteria. This solution streamlines the recruitment process and ensures a better fit between candidates and job requirements.

-Features
Skill Extraction: Extracts and compares relevant skills from resumes and job descriptions.
Match Score: Calculates a match score based on common skills between the resume and job description.
Email Notification: Sends an email notification to candidates who are shortlisted based on the match score.
Database Integration: Stores candidate details, including match scores and relevant skills, in a local SQLite database for tracking.

-Technologies Used
Backend: Python, Flask

-Libraries: PyPDF2, Pandas, re (for regular expressions), SQLite, smtplib

-Database: SQLite

-Email: SMTP (Gmail)

Installation
Clone this repository:

git clone [https://github.com/Enhancing/smart-recruiter.git](https://github.com/Thoufiq26/Enhancing-Job-Screening-with-AI-and-Data-Intelligence/tree/main)
cd smart-recruiter
Install the required dependencies:

pip install -r requirements.txt
Set up the database:

python app.py
Ensure that your email configuration (SMTP settings) is set up correctly in the app.py file.

Usage
Run the Flask app:

python app.py
Upload a resume (CV) and a job description (JD) via the app.py.

Access the web app at http://127.0.0.1:5000.

run the command - curl -X POST http://127.0.0.1:5000/upload -F "cv=@C:/AI-Agent/backend/uploads/C1061.pdf" -F "jd=@C:/AI-Agent/backend/uploads/job_description.csv"

View the match score and the list of matching skills between the resume and job description.

The system will automatically send an email to candidates whose match score is above a specified threshold (e.g., 80%).

File Structure
app.py: Main Flask application logic

uploads/: Folder for storing uploaded files (CV and JD)

recruitment.db: SQLite database for storing candidate information

requirements.txt: List of Python dependencies

Contributing
If you'd like to contribute to this project, feel free to fork the repository and create a pull request. Please ensure that any code changes adhere to the existing code style and include relevant tests.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgements
Flask for the backend framework.

PyPDF2 for extracting text from PDFs.

Pandas for processing CSV files.

SQLite for local database storage.
