import os
from typing import Optional, Tuple
import PyPDF2
from docx import Document
from dotenv import load_dotenv
import requests

load_dotenv()

class FileHandler:
    @staticmethod
    def read_pdf(file_path: str) -> str:
        """Read text from PDF file with improved structure preservation."""
        text = ""
        section_breaks = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Process each page
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    
                    # Add page break marker if not the first page
                    if i > 0:
                        text += "\n\n" + "-" * 20 + f" Page {i+1} " + "-" * 20 + "\n\n"
                    
                    # Process the text to better preserve sections
                    lines = page_text.split('\n')
                    for line in lines:
                        # Identify potential section headers (all caps, short lines)
                        stripped = line.strip()
                        if stripped and stripped.isupper() and len(stripped) < 30:
                            section_breaks.append(stripped)
                            text += f"\n\n{stripped}\n" + "-" * len(stripped) + "\n"
                        else:
                            text += line + "\n"
            
            # Clean up multiple newlines
            text = "\n".join([line for line in text.split('\n') if line.strip()])
            
            # Re-format with consistent newlines between sections
            for section in section_breaks:
                text = text.replace(f"{section}\n{'-' * len(section)}", f"\n\n{section}\n{'-' * len(section)}\n")
                
            return text
        
        except Exception as e:
            print(f"Warning: Error reading PDF file: {e}")
            # Fall back to basic extraction if enhanced extraction fails
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text

    @staticmethod
    def read_docx(file_path: str) -> str:
        """Read text from DOCX file."""
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    @staticmethod
    def write_latex_to_file(content: str, output_path: str) -> None:
        """Write LaTeX content to file."""
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def convert_to_pdf(latex_file: str, output_pdf: str) -> None:
        """Convert LaTeX to PDF using pdflatex."""
        os.system(f"pdflatex -interaction=nonstopmode {latex_file}")
        os.system(f"mv {os.path.splitext(latex_file)[0]}.pdf {output_pdf}")
        
        # Clean up temporary files
        temp_files = [
            os.path.splitext(latex_file)[0] + ext
            for ext in ['.aux', '.log', '.out']
        ]
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)

    @staticmethod
    def upload_to_overleaf(latex_content: str, project_name: str) -> Tuple[bool, Optional[str]]:
        """Upload LaTeX content to Overleaf."""
        overleaf_token = os.getenv("OVERLEAF_TOKEN")
        if not overleaf_token:
            return False, "Overleaf token not found"

        try:
            # Create new project
            response = requests.post(
                "https://api.overleaf.com/project",
                headers={
                    "Authorization": f"Bearer {overleaf_token}",
                    "Content-Type": "application/json"
                },
                json={"name": project_name}
            )
            response.raise_for_status()
            project_id = response.json()["id"]

            # Upload LaTeX content
            response = requests.put(
                f"https://api.overleaf.com/project/{project_id}/content/main.tex",
                headers={
                    "Authorization": f"Bearer {overleaf_token}",
                    "Content-Type": "text/plain"
                },
                data=latex_content
            )
            response.raise_for_status()

            return True, f"https://www.overleaf.com/project/{project_id}"
        except requests.exceptions.RequestException as e:
            return False, str(e)
