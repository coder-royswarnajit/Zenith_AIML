import os
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import nltk
from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)
nltk.download('punkt')
jobs_df = pd.read_csv('jobs.csv')

def extract_text_from_txt(file):
    return file.read().decode('windows-1252', errors='ignore')

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    resume_text = ""
    for page in pdf_reader.pages:
        resume_text += page.extract_text()
    return resume_text

def extract_text_from_docx(file):
    doc = Document(file)
    resume_text = ""
    for para in doc.paragraphs:
        resume_text += para.text + "\n"
    return resume_text

def extract_skills(resume_text):
    skills = ["python", "java", "sql", "javascript", "machine learning", "data science", "html", "css", "c++"]
    resume_skills = [skill for skill in skills if skill.lower() in resume_text.lower()]
    return resume_skills

@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        resume_file = request.files['resume']

        if resume_file.filename.endswith('.txt'):
            resume_text = extract_text_from_txt(resume_file)
        elif resume_file.filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(resume_file)
        elif resume_file.filename.endswith('.docx'):
            resume_text = extract_text_from_docx(resume_file)
        else:
            return "Unsupported file format!", 400

        skills = extract_skills(resume_text)
        
    
        print(f"Strengths present in the resume: {name}: {skills}")

        matched_jobs = jobs_df[jobs_df['skills_desc'].str.contains('|'.join(skills), case=False, na=False)]

        return render_template('results.html', name=name, skills=skills, jobs=matched_jobs.to_dict(orient='records'))

    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get('message')
    response = generate_chatbot_response(user_message)
    return {'response': response}, 200

def generate_chatbot_response(message):
    responses = {
        "hello": "Hi there! How can I assist you today?",
        "help": "I can help you upload your resume, find jobs, and answer questions about the platform.",
        "jobs": "You can upload your resume to see the jobs that match your skills.",
        "bye": "Goodbye! Have a great day!"
    }
    message = message.lower()
    return responses.get(message, "I'm sorry, I didn't understand that. Could you please rephrase?")


if __name__ == '__main__':
    app.run(debug=True)