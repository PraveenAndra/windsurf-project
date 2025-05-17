#!/usr/bin/env python3
"""
Command-line script for the AI Resume Optimization Tool.
This provides a simplified interface to the tool's functionality.
"""
import sys
import os
import argparse

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.main import main as optimizer_main
from src.utils.env_validator import EnvValidator

def parse_args():
    """Parse command line arguments with more user-friendly options."""
    parser = argparse.ArgumentParser(
        description="AI Resume Optimization Tool - Create ATS-friendly resumes optimized for specific job descriptions"
    )
    
    # Required arguments
    parser.add_argument(
        "--resume", "-r", 
        required=True, 
        help="Path to your resume file (PDF, DOCX, or TXT)"
    )
    
    # Job description - either as text or file
    job_description_group = parser.add_argument_group("Job Description (required)")
    jd_group = job_description_group.add_mutually_exclusive_group(required=True)
    jd_group.add_argument(
        "--job-description", "-j", 
        help="Job description text or file path"
    )
    jd_group.add_argument(
        "--job-description-file", "-jf", 
        help="File containing the job description"
    )
    
    # Optional arguments
    parser.add_argument(
        "--output", "-o", 
        default="optimized_resume.tex", 
        help="Output LaTeX file name (default: optimized_resume.tex)"
    )
    parser.add_argument(
        "--template", "-t", 
        default="professional", 
        help="LaTeX template to use (default: professional)"
    )
    parser.add_argument(
        "--project-name", "-p", 
        default="Optimized Resume", 
        help="Overleaf project name (default: 'Optimized Resume')"
    )
    parser.add_argument(
        "--analyze-only", "-a", 
        action="store_true", 
        help="Only analyze resume without optimization"
    )
    parser.add_argument(
        "--no-overleaf", "-n", 
        action="store_true", 
        help="Skip Overleaf upload"
    )
    
    return parser.parse_args()

def main():
    """Run the optimizer with command-line arguments."""
    print("\n=====================================")
    print("  AI Resume Optimization Tool")
    print("  Command Line Interface")
    print("=====================================\n")
    
    # Validate environment variables
    validator = EnvValidator()
    validator.print_config_summary()
    validator.validate_or_exit(suppress_warnings=True)
    
    args = parse_args()
    
    # Process job description from file if needed
    if args.job_description_file:
        if os.path.exists(args.job_description_file):
            with open(args.job_description_file, 'r') as f:
                args.job_description = f.read()
            print(f"Read job description from file: {args.job_description_file}")
        else:
            print(f"Error: Job description file not found: {args.job_description_file}")
            sys.exit(1)
    
    # Convert arguments to the format expected by the main module
    sys_args = [
        "--resume", args.resume,
        "--job-description", args.job_description,
        "--output", args.output,
        "--template", args.template,
        "--project-name", args.project_name
    ]
    
    if args.analyze_only:
        sys_args.append("--analyze-only")
    
    if args.no_overleaf:
        sys_args.append("--no-overleaf")
    
    # Replace sys.argv with our processed arguments
    sys.argv = [sys.argv[0]] + sys_args
    
    # Run the optimizer
    optimizer_main()

if __name__ == "__main__":
    main()
