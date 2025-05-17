from core.resume_optimizer import ResumeOptimizer
from core.template_manager import TemplateManager
from core.overleaf_connector import OverleafConnector
from core.ats_analyzer import ATSAnalyzer
from utils.file_handler import FileHandler
import argparse
import os
import sys
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Optional
from pathlib import Path

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description='AI Resume Optimization Tool')
    parser.add_argument('--resume', required=True, help='Path to your resume file (PDF or DOCX)')
    parser.add_argument('--job-description', required=True, help='Path to job description file or paste the text')
    parser.add_argument('--output', default='optimized_resume.tex', help='Output LaTeX file name')
    parser.add_argument('--project-name', default='Optimized Resume', help='Overleaf project name')
    parser.add_argument('--template', default='professional', help='LaTeX template to use (filename without .tex)')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze resume without optimization')
    parser.add_argument('--no-overleaf', action='store_true', help='Skip Overleaf upload')
    
    args = parser.parse_args()
    
    # Initialize components
    optimizer = ResumeOptimizer()
    file_handler = FileHandler()
    template_manager = TemplateManager()
    ats_analyzer = ATSAnalyzer()
    
    try:
        # Check if template exists
        available_templates = template_manager.get_available_templates()
        if args.template not in available_templates:
            print(f"Template '{args.template}' not found. Available templates: {', '.join(available_templates)}")
            print(f"Using default template 'professional' instead.")
            args.template = 'professional'
            
        # Read resume content
        resume_content = None
        if args.resume.lower().endswith('.pdf'):
            print(f"Reading PDF resume from: {args.resume}")
            resume_content = file_handler.read_pdf(args.resume)
        elif args.resume.lower().endswith('.docx'):
            print(f"Reading DOCX resume from: {args.resume}")
            resume_content = file_handler.read_docx(args.resume)
        else:
            raise ValueError("Unsupported resume format. Please use PDF or DOCX.")
            
        # Read job description
        job_description = args.job_description
        if os.path.exists(args.job_description):
            print(f"Reading job description from file: {args.job_description}")
            with open(args.job_description, 'r') as f:
                job_description = f.read()
        else:
            print("Using provided job description text")
            
        # First, analyze the original resume
        print("\n=== Original Resume Analysis ===")
        original_analysis = ats_analyzer.analyze_resume(resume_content, job_description)
        
        print(f"Overall ATS Compatibility Score: {original_analysis['overall_score']*100:.1f}%")
        print("\nAreas to improve:")
        for suggestion in original_analysis['improvement_suggestions']:
            print(f" • {suggestion}")
            
        if args.analyze_only:
            print("\nAnalysis completed. Exiting as requested.")
            return
            
        # Extract keywords from job description
        print("\n=== Extracting Keywords from Job Description ===")
        keywords = optimizer.extract_keywords(job_description)
        print(f"Found {len(keywords)} relevant keywords:")
        print(", ".join(keywords[:15]) + ("..." if len(keywords) > 15 else ""))
        
        # Optimize resume content
        print("\n=== Optimizing Resume Content ===")
        optimized_content = optimizer.optimize_content(resume_content, job_description)
        
        # Analyze optimized content
        print("\n=== Optimized Resume Analysis ===")
        optimized_analysis = ats_analyzer.analyze_resume(optimized_content, job_description)
        
        print(f"New ATS Compatibility Score: {optimized_analysis['overall_score']*100:.1f}%")
        print(f"Improvement: {(optimized_analysis['overall_score'] - original_analysis['overall_score'])*100:.1f}%")
        
        if optimized_analysis['improvement_suggestions']:
            print("\nRemaining suggestions:")
            for suggestion in optimized_analysis['improvement_suggestions']:
                print(f" • {suggestion}")
        else:
            print("\nNo further suggestions! Your resume is well-optimized.")
            
        # Parse the optimized content into sections
        print("\n=== Generating LaTeX Resume ===")
        sections = template_manager.parse_resume_sections(optimized_content)
        
        # Generate LaTeX document
        latex_document = template_manager.generate_latex_resume(args.template, sections)
        
        # Save LaTeX file
        output_path = args.output
        print(f"Saving optimized resume to {output_path}")
        file_handler.write_latex_to_file(latex_document, output_path)
        
        # Upload to Overleaf if not disabled
        if not args.no_overleaf:
            try:
                print("\n=== Uploading to Overleaf ===")
                # Check for Overleaf token
                if not os.getenv("OVERLEAF_TOKEN"):
                    print("Warning: OVERLEAF_TOKEN not found in environment. Skipping upload.")
                    print(f"Set your Overleaf API token in the .env file to enable this feature.")
                else:
                    overleaf = OverleafConnector()
                    success, result = overleaf.create_resume_project(latex_document, args.project_name)
                    
                    if success:
                        print(f"Success! Your optimized resume is available on Overleaf at:\n{result}")
                    else:
                        print(f"Warning: Failed to upload to Overleaf: {result}")
                        print(f"Your optimized LaTeX file is still saved as {output_path}")
            except Exception as e:
                print(f"Overleaf upload error: {str(e)}")
                print(f"Your optimized LaTeX file is still saved as {output_path}")
                
        print("\n=== Process Complete ===")
        print(f"LaTeX resume saved to: {os.path.abspath(output_path)}")
        print("To compile the LaTeX file to PDF, run: pdflatex " + output_path)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
