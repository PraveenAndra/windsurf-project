import os
from typing import Dict, List, Tuple
import spacy
import nltk
from nltk.tokenize import word_tokenize
import pandas as pd
from dotenv import load_dotenv
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

nlp = spacy.load("en_core_web_sm")

class ResumeOptimizer:
    def __init__(self):
        self.nlp = nlp
        self.keywords = []

    def extract_keywords(self, job_description: str) -> List[str]:
        """Extract relevant keywords from job description."""
        doc = self.nlp(job_description)
        keywords = []
        
        # Extract nouns and proper nouns
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN']:
                keywords.append(token.text.lower())
                
        # Extract skills and technologies
        skills = self._extract_skills(job_description)
        keywords.extend(skills)
        
        return list(set(keywords))

    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills and technologies."""
        common_tech_terms = [
            "python", "java", "javascript", "sql", "aws", "azure", "docker",
            "kubernetes", "machine learning", "data science", "devops"
        ]
        
        tokens = word_tokenize(text.lower())
        skills = [term for term in tokens if term in common_tech_terms]
        return skills

    def optimize_content(self, resume_text: str, job_description: str) -> str:
        """Optimize resume content based on job description."""
        keywords = self.extract_keywords(job_description)
        
        # Generate optimized content using OpenAI
        prompt = f"""
        Optimize the following resume content for the given job description:
        
        Resume: {resume_text}
        Job Description: {job_description}
        
        Focus on these keywords: {', '.join(keywords)}
        
        Requirements:
        1. Make the content ATS-friendly
        2. Highlight relevant skills and experience
        3. Use professional language
        4. Maintain chronological order
        5. Keep formatting clean and readable
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume optimizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content

    def analyze_ats_compatibility(self, resume_text: str) -> Dict[str, float]:
        """Analyze resume for ATS compatibility."""
        analysis = {
            "readability": 0.0,
            "keyword_density": 0.0,
            "formatting_score": 0.0
        }
        
        # Basic analysis
        doc = self.nlp(resume_text)
        analysis["readability"] = self._calculate_readability(doc)
        analysis["keyword_density"] = self._calculate_keyword_density(resume_text)
        analysis["formatting_score"] = self._analyze_formatting(resume_text)
        
        return analysis

    def _calculate_readability(self, doc) -> float:
        """Calculate Flesch reading ease score."""
        total_words = len(doc)
        total_sentences = len(list(doc.sents))
        total_syllables = sum(len(word) for word in doc)
        
        if total_sentences == 0:
            return 0.0
            
        score = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
        return min(max(score, 0), 100)

    def _calculate_keyword_density(self, text: str) -> float:
        """Calculate keyword density."""
        words = word_tokenize(text.lower())
        total_words = len(words)
        keyword_count = sum(1 for word in words if word in self.keywords)
        
        if total_words == 0:
            return 0.0
            
        return (keyword_count / total_words) * 100

    def _analyze_formatting(self, text: str) -> float:
        """Analyze formatting consistency."""
        # Basic analysis - more sophisticated analysis can be added
        if "\n\n" in text:  # Check for proper section breaks
            return 0.8
        return 0.5

    def generate_latex_template(self, optimized_content: str) -> str:
        """Generate LaTeX template with optimized content."""
        template = """
\documentclass[letterpaper,11pt]{article}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{geometry}
\geometry{left=1.0in,right=1.0in,top=0.75in,bottom=0.75in}

\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}
\setlength{\parskip}{0.5em}

\begin{document}

% Paste optimized content here
{content}

\end{document}
"""
        return template.format(content=optimized_content)
