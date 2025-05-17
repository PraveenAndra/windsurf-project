import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class TemplateManager:
    """Manages LaTeX templates for resume generation."""
    
    def __init__(self, templates_dir: str = None):
        """Initialize the template manager.
        
        Args:
            templates_dir: Directory containing LaTeX templates
        """
        if templates_dir is None:
            # Default to the templates directory in the package
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.templates_dir = os.path.join(os.path.dirname(current_dir), "templates")
        else:
            self.templates_dir = templates_dir
            
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, str]:
        """Load all available templates from the templates directory."""
        templates = {}
        template_files = [f for f in os.listdir(self.templates_dir) if f.endswith('.tex')]
        
        for template_file in template_files:
            template_name = os.path.splitext(template_file)[0]
            template_path = os.path.join(self.templates_dir, template_file)
            
            with open(template_path, 'r', encoding='utf-8') as f:
                templates[template_name] = f.read()
                
        return templates
        
    def get_available_templates(self) -> List[str]:
        """Get a list of available template names."""
        return list(self.templates.keys())
        
    def get_template_content(self, template_name: str) -> Optional[str]:
        """Get the content of a specific template.
        
        Args:
            template_name: Name of the template to retrieve
            
        Returns:
            Template content as string or None if not found
        """
        return self.templates.get(template_name)
        
    def parse_resume_sections(self, resume_text: str) -> Dict[str, str]:
        """Parse a resume text into sections for template insertion.
        
        Args:
            resume_text: The resume text to parse
            
        Returns:
            Dictionary of section name to content
        """
        # Basic section detection - this can be enhanced with NLP
        sections = {
            "CONTACT_INFO": "",
            "PROFESSIONAL_SUMMARY": "",
            "EXPERIENCE": "",
            "EDUCATION": "",
            "SKILLS": "",
            "PROJECTS": "",
            "CERTIFICATIONS": ""
        }
        
        # Very simple section detection - in practice, use more sophisticated NLP
        lines = resume_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            lower_line = line.lower()
            if "summary" in lower_line or "objective" in lower_line or "profile" in lower_line:
                current_section = "PROFESSIONAL_SUMMARY"
                continue
            elif "experience" in lower_line or "employment" in lower_line or "work history" in lower_line:
                current_section = "EXPERIENCE"
                continue
            elif "education" in lower_line or "academic" in lower_line:
                current_section = "EDUCATION"
                continue
            elif "skill" in lower_line or "technical" in lower_line or "technologies" in lower_line:
                current_section = "SKILLS"
                continue
            elif "project" in lower_line:
                current_section = "PROJECTS"
                continue
            elif "certification" in lower_line or "certificate" in lower_line:
                current_section = "CERTIFICATIONS"
                continue
            elif any(contact in lower_line for contact in ["email", "phone", "contact", "address"]):
                if not sections["CONTACT_INFO"]:  # Only grab first contact info
                    sections["CONTACT_INFO"] = line
                continue
                
            # Add content to current section
            if current_section and current_section in sections:
                sections[current_section] += line + "\n"
                
        return sections
        
    def generate_latex_resume(self, template_name: str, sections: Dict[str, str]) -> str:
        """Generate a LaTeX resume by filling a template with section content.
        
        Args:
            template_name: Name of template to use
            sections: Dictionary of section content
            
        Returns:
            Complete LaTeX document
        """
        template = self.get_template_content(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
            
        # Replace template placeholders with content
        for section_name, section_content in sections.items():
            placeholder = f"{{{{{{ section_name }}}}}}"
            template = template.replace(placeholder, section_content)
            
        return template
        
    def format_contact_info(self, name: str, email: str, phone: str) -> str:
        """Format contact information for LaTeX template.
        
        Args:
            name: Full name
            email: Email address
            phone: Phone number
            
        Returns:
            Formatted contact info for LaTeX
        """
        return f"\\contactInfo{{{name}}}{{{email}}}{{{phone}}}"
        
    def format_experience_entry(self, company: str, position: str, location: str, 
                               dates: str, description: str) -> str:
        """Format a single experience entry for LaTeX template.
        
        Args:
            company: Company name
            position: Job title
            location: Job location
            dates: Employment dates
            description: Job description bullet points
            
        Returns:
            Formatted experience entry for LaTeX
        """
        # Split description into bullet points
        bullets = description.strip().split('\n')
        formatted_bullets = ""
        
        for bullet in bullets:
            if bullet.strip():
                formatted_bullets += f"\\resumeItem{{{bullet.strip()}}}\n"
                
        return f"""\\resumeSubheading{{{company}}}{{{dates}}}
{{{position}}}{{{location}}}
\\begin{{itemize}}
{formatted_bullets}
\\end{{itemize}}
"""
