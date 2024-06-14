import os

import docx2txt
import PyPDF2
from flask import Flask, render_template, request

app= Flask(__name__)
app.config['UPLOAD_FOLDER']= 'uploads/'

#functions
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path,'rb') as file:
        reader=PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
        return text

def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)

def extract_text_from_txt(file_path):
    with open(file_path,'r', encoding='utf-8') as file:
        return file.read()

def extract_text(file_path):
    if file_path.endwith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endwith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.endwith(".txt"):
        return extract_text_from_txt(file_path)
    else:
        return ""

@app.route("/")
def matchresume():
    return render_template('index.html')

@app.route("/matcher", methods=['GET','POST'])
def analyze():
    if request.method == 'POST':
        job_desc=request.form.get('jobDescription')
        resume_files=request.form.getlist('resumes')

        resumes = []
        for resume_file in resume_files:
            if resume_file.filename:
                filename=os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
                resume_file.save(filename)
                resumes.append(extract_text(filename))

            
if __name__=="__main__":
    app.run(debug=True)
