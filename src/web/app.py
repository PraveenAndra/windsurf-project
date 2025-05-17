import os
import uuid
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from werkzeug.utils import secure_filename
from datetime import datetime

from src.core.resume_optimizer import ResumeOptimizer
from src.core.template_manager import TemplateManager
from src.core.ats_analyzer import ATSAnalyzer
from src.core.overleaf_connector import OverleafConnector
from src.utils.file_handler import FileHandler

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())
app.config['UPLOAD_FOLDER'] = os.path.join(tempfile.gettempdir(), 'resume_optimizer_uploads')
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB max upload size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
optimizer = ResumeOptimizer()
template_manager = TemplateManager()
ats_analyzer = ATSAnalyzer()
file_handler = FileHandler()

def allowed_file(filename):
    """Check if file has an allowed extension."""
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    """Render the home page."""
    templates = template_manager.get_available_templates()
    return render_template('index.html', templates=templates)

@app.route('/optimize', methods=['POST'])
def optimize_resume():
    """Handle resume optimization request."""
    # Check if both files are provided
    if 'resume' not in request.files or not request.files['resume'].filename:
        flash('No resume file selected', 'error')
        return redirect(url_for('home'))
    
    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '').strip()
    
    # Check if job description is provided
    if not job_description and 'job_description_file' not in request.files:
        flash('Please provide a job description', 'error')
        return redirect(url_for('home'))
    
    # If job description file is uploaded, use that
    if 'job_description_file' in request.files and request.files['job_description_file'].filename:
        job_description_file = request.files['job_description_file']
        if allowed_file(job_description_file.filename):
            job_filename = f"{uuid.uuid4()}_{secure_filename(job_description_file.filename)}"
            job_path = os.path.join(app.config['UPLOAD_FOLDER'], job_filename)
            job_description_file.save(job_path)
            
            # Read job description from file
            with open(job_path, 'r') as f:
                job_description = f.read()
            
            # Clean up file
            os.remove(job_path)
    
    # Process the resume file
    if resume_file and allowed_file(resume_file.filename):
        # Generate a unique filename
        resume_filename = f"{uuid.uuid4()}_{secure_filename(resume_file.filename)}"
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        resume_file.save(resume_path)
        
        try:
            # Read resume content based on file type
            resume_content = None
            if resume_path.lower().endswith('.pdf'):
                resume_content = file_handler.read_pdf(resume_path)
            elif resume_path.lower().endswith('.docx'):
                resume_content = file_handler.read_docx(resume_path)
            elif resume_path.lower().endswith('.txt'):
                with open(resume_path, 'r') as f:
                    resume_content = f.read()
            else:
                flash('Unsupported file format', 'error')
                return redirect(url_for('home'))
            
            # Store in session for analysis page
            session['resume_content'] = resume_content
            session['job_description'] = job_description
            
            # Analyze original resume
            original_analysis = ats_analyzer.analyze_resume(resume_content, job_description)
            session['original_analysis'] = original_analysis
            
            # Extract keywords
            keywords = optimizer.extract_keywords(job_description)
            session['keywords'] = keywords
            
            # Optimize resume
            optimized_content = optimizer.optimize_content(resume_content, job_description)
            session['optimized_content'] = optimized_content
            
            # Analyze optimized resume
            optimized_analysis = ats_analyzer.analyze_resume(optimized_content, job_description)
            session['optimized_analysis'] = optimized_analysis
            
            # Generate LaTeX using selected template
            template_name = request.form.get('template', 'professional')
            sections = template_manager.parse_resume_sections(optimized_content)
            latex_document = template_manager.generate_latex_resume(template_name, sections)
            
            # Save LaTeX file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"optimized_resume_{timestamp}.tex"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(latex_document)
            
            session['latex_path'] = output_path
            session['latex_filename'] = output_filename
            
            # Check if Overleaf upload was requested
            if 'upload_to_overleaf' in request.form and os.getenv("OVERLEAF_TOKEN"):
                project_name = request.form.get('project_name', f"Optimized Resume - {timestamp}")
                overleaf = OverleafConnector()
                success, result = overleaf.create_resume_project(latex_document, project_name)
                
                if success:
                    session['overleaf_url'] = result
                else:
                    session['overleaf_error'] = result
            
            # Clean up original file
            os.remove(resume_path)
            
            return redirect(url_for('analysis'))
            
        except Exception as e:
            flash(f"Error during optimization: {str(e)}", 'error')
            return redirect(url_for('home'))
    
    else:
        flash('Invalid file type. Please upload PDF, DOCX, or TXT files.', 'error')
        return redirect(url_for('home'))
        
@app.route('/analysis', methods=['GET'])
def analysis():
    """Show the analysis results page."""
    if 'optimized_content' not in session:
        flash('No analysis data found. Please submit a resume first.', 'error')
        return redirect(url_for('home'))
    
    return render_template(
        'analysis.html',
        resume_content=session.get('resume_content'),
        job_description=session.get('job_description'),
        keywords=session.get('keywords'),
        original_analysis=session.get('original_analysis'),
        optimized_content=session.get('optimized_content'),
        optimized_analysis=session.get('optimized_analysis'),
        latex_filename=session.get('latex_filename'),
        overleaf_url=session.get('overleaf_url'),
        overleaf_error=session.get('overleaf_error')
    )

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download generated LaTeX file."""
    if 'latex_path' not in session:
        flash('No file available for download', 'error')
        return redirect(url_for('home'))
    
    return send_file(
        session.get('latex_path'),
        as_attachment=True,
        download_name=filename
    )

@app.route('/clear', methods=['GET'])
def clear_session():
    """Clear the session data."""
    # Remove temporary files
    if 'latex_path' in session and os.path.exists(session['latex_path']):
        try:
            os.remove(session['latex_path'])
        except:
            pass
    
    # Clear session
    session.clear()
    flash('Session cleared', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
