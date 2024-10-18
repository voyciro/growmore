import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import openai  # Use OpenAI's Python client
import PyPDF2 as pdf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

# Flask app setup
app = Flask(__name__)

# Initialize CORS
CORS(app)  # Allow all domains to access this Flask app

# Input prompt template for ChatGPT
input_prompt = '''
As an ATS specialist, I meticulously evaluate resumes in tech, software, and data science for a fierce job market. Provide a percentage match, identify keywords, and offer top-tier guidance.

1. **Contact Information:**
   - Full name
   - Phone number (with country code)
   - Email address
   - LinkedIn profile
   - Location (City, State, ZIP code)

2. **Resume Format:**
   - Compatible formats (.docx, .pdf)
   - Proper naming convention

... (the rest of your input prompt follows)

*Resume:*
{text}

*Job Description:*
{jd}
'''

# Function to get response from OpenAI's ChatGPT API
def get_chatgpt_response(resume_text, jd):
    prompt = input_prompt.format(text=resume_text, jd=jd)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if available
        messages=[{"role": "system", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# Function to extract text from PDF
def text_in_uploaded_pdf(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ''
    for page in range(len(reader.pages)):
        page_text = reader.pages[page].extract_text()
        text += f"Page {page + 1}:\n{page_text}\n\n"
    return text

# Route to handle resume analysis request
@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    try:
        # Expecting resume file and job description in the request
        resume_file = request.files.get('resume')
        job_description = request.form.get('jd')

        if not resume_file or not job_description:
            return jsonify({'error': 'Missing resume or job description'}), 400

        # Check if the file is a valid PDF
        if not allowed_file(resume_file.filename):
            return jsonify({'error': 'Invalid file type. Only PDFs are allowed.'}), 400

        # Extract text from the uploaded resume PDF
        resume_text = text_in_uploaded_pdf(resume_file)

        # Get analysis from OpenAI ChatGPT
        analysis_result = get_chatgpt_response(resume_text, job_description)

        # Return the result as a JSON response
        return jsonify({'result': analysis_result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

if __name__ == "__main__":
    app.run(debug=True)
