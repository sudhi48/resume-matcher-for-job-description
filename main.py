import os

import docx2txt
import PyPDF2
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config['UPLOAD_FOLDER']= 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


#functions
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path,'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
        return text

def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)

def extract_text_from_txt(file_path):
    with open(file_path,'r', encoding='utf-8') as file:
        return file.read()

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)
    else:
        return ""

@app.route("/")
def matchresume():
    return render_template('index.html')

@app.route("/matcher", methods=['GET','POST'])
def analyze():
    if request.method == 'POST':
        job_desc = request.form.get('jobDescription')
        resume_files = request.files.getlist('resumes')

        resumes = []
        for resume_file in resume_files:
            if resume_file.filename:
                filename = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
                resume_file.save(filename)
                resumes.append(extract_text(filename))

        if not resumes and not job_desc:
            return render_template('index.html', message="Please upload resumes and enter job description")
        
        #matching
        vectorizer = TfidfVectorizer().fit_transform([job_desc] + resumes)
        vectors = vectorizer.toarray()
        job_vector = vectors[0]
        resume_vector = vectors[1:]
        similarities = cosine_similarity([job_vector], resume_vector)[0] * 100
        
        # top resumes
        top_indices = similarities.argsort()[-3:][::-1]
        top_resumes = [resume_files[i].filename for i in top_indices]
        similarity_scores = [round(similarities[i]) for i in top_indices]

        return render_template('index.html', message="Top matching resumes:", top_resumes=top_resumes, similarity_scores=similarity_scores)
        
if __name__=="__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
