import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
from typing import Dict, List, Tuple, Set
import spacy
import pandas as pd
import os

# Download required NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

class ATSAnalyzer:
    """Analyzes resumes for ATS (Applicant Tracking System) compatibility."""
    
    def __init__(self):
        """Initialize the ATS analyzer."""
        # Load spaCy model for NLP analysis
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If the model is not installed, download it
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
            
        self.stop_words = set(stopwords.words('english'))
        
        # Common ATS-rejected formatting issues
        self.formatting_issues = {
            "tables": r"<table|<tr|<td",
            "text_boxes": r"<textbox",
            "headers_footers": r"<header|<footer",
            "images": r"<img|<image|\\includegraphics",
            "exotic_fonts": r"\\font|\\newfont|\\fontfamily",
            "complicated_macros": r"\\newcommand|\\renewcommand"
        }
        
        # Common section headers expected in a resume
        self.expected_sections = [
            "education", "experience", "work experience", "employment", 
            "skills", "technical skills", "professional summary", "summary", 
            "objective", "projects", "certifications", "publications"
        ]
        
    def analyze_resume(self, resume_text: str, job_description: str = None) -> Dict[str, object]:
        """Perform a comprehensive ATS compatibility analysis.
        
        Args:
            resume_text: The resume text to analyze
            job_description: Optional job description to compare against
            
        Returns:
            Dictionary of analysis results
        """
        results = {
            "overall_score": 0.0,
            "readability": self._analyze_readability(resume_text),
            "formatting": self._analyze_formatting(resume_text),
            "content_analysis": self._analyze_content(resume_text),
            "section_analysis": self._analyze_sections(resume_text),
            "improvement_suggestions": []
        }
        
        # If job description is provided, analyze keyword matching
        if job_description:
            results["keyword_analysis"] = self._analyze_keywords(resume_text, job_description)
            
        # Calculate overall score (weighted average of subscores)
        subscores = [
            (results["readability"]["score"], 0.2),
            (results["formatting"]["score"], 0.2),
            (results["content_analysis"]["content_score"], 0.3)
        ]
        
        if job_description:
            subscores.append((results["keyword_analysis"]["match_score"], 0.3))
        else:
            # Adjust weights if no job description
            subscores = [(score, weight * (1/0.7)) for score, weight in subscores]
            
        results["overall_score"] = sum(score * weight for score, weight in subscores)
        
        # Generate improvement suggestions
        results["improvement_suggestions"] = self._generate_suggestions(results)
        
        return results
        
    def _analyze_readability(self, text: str) -> Dict[str, object]:
        """Analyze the readability of resume text.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary of readability metrics
        """
        doc = self.nlp(text)
        
        # Count sentences, words, syllables
        sentences = list(doc.sents)
        sentence_count = len(sentences)
        word_count = len([token for token in doc if not token.is_punct])
        
        # Calculate syllables (simple approximation)
        syllable_count = 0
        for token in doc:
            if token.is_alpha:
                word = token.text.lower()
                if len(word) <= 3:
                    syllable_count += 1
                else:
                    syllable_count += len(re.findall(r'[aeiouy]+', word))
        
        # Calculate average words per sentence
        avg_words_per_sentence = word_count / max(1, sentence_count)
        
        # Calculate Flesch Reading Ease
        if word_count == 0 or sentence_count == 0:
            flesch_score = 0
        else:
            flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * (syllable_count / word_count))
            flesch_score = max(0, min(100, flesch_score))  # Clamp to 0-100
            
        # Calculate ATS-friendliness score
        readability_score = 0.0
        
        # Ideal range for resumes: 40-60 (professional but not overly complex)
        if 40 <= flesch_score <= 60:
            readability_score = 10.0
        elif 30 <= flesch_score < 40 or 60 < flesch_score <= 70:
            readability_score = 8.0
        elif 20 <= flesch_score < 30 or 70 < flesch_score <= 80:
            readability_score = 6.0
        else:
            readability_score = 4.0
            
        # Analyze sentence length
        long_sentences = [s for s in sentences if len(s.text.split()) > 25]
        percent_long_sentences = len(long_sentences) / max(1, sentence_count)
        
        if percent_long_sentences > 0.3:
            readability_score -= 2.0
            
        return {
            "score": readability_score / 10.0,  # Normalize to 0-1
            "flesch_reading_ease": flesch_score,
            "avg_words_per_sentence": avg_words_per_sentence,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "percent_long_sentences": percent_long_sentences
        }
        
    def _analyze_formatting(self, text: str) -> Dict[str, object]:
        """Analyze the formatting of resume text for ATS compatibility.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary of formatting analysis
        """
        issues_found = {}
        
        # Check for formatting issues
        for issue_name, pattern in self.formatting_issues.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            issues_found[issue_name] = len(matches) > 0
            
        # Check for other formatting issues
        excessive_bullets = len(re.findall(r'•|\\item', text)) > 50
        excessive_whitespace = len(re.findall(r'\n\s*\n\s*\n', text)) > 10
        
        # Calculate formatting score
        base_score = 10.0
        for issue in issues_found.values():
            if issue:
                base_score -= 1.5
                
        if excessive_bullets:
            base_score -= 1.0
            
        if excessive_whitespace:
            base_score -= 1.0
            
        return {
            "score": max(0, base_score) / 10.0,  # Normalize to 0-1
            "issues_found": issues_found,
            "excessive_bullets": excessive_bullets,
            "excessive_whitespace": excessive_whitespace
        }
        
    def _analyze_content(self, text: str) -> Dict[str, object]:
        """Analyze resume content for quality and ATS compatibility.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary of content analysis
        """
        # Check for common resume issues
        has_objective = bool(re.search(r'\b(objective|goal|aim)\b', text, re.IGNORECASE))
        has_references = bool(re.search(r'\b(references|referees)\b', text, re.IGNORECASE))
        has_personal_pronouns = bool(re.search(r'\b(I|me|my|mine|myself)\b', text, re.IGNORECASE))
        
        # Check for action verbs at the beginning of bullet points
        lines = text.split('\n')
        bullet_lines = [line for line in lines if line.strip().startswith('•') or line.strip().startswith('-')]
        
        action_verbs = [
            'achieved', 'implemented', 'developed', 'created', 'managed', 'led', 'designed', 
            'improved', 'increased', 'reduced', 'negotiated', 'analyzed', 'organized', 
            'coordinated', 'built', 'delivered', 'launched', 'resolved', 'streamlined'
        ]
        
        action_verb_count = 0
        for line in bullet_lines:
            words = word_tokenize(line)
            if len(words) > 1:
                first_word = words[1].lower() if words[0] in ['•', '-'] else words[0].lower()
                if first_word in action_verbs:
                    action_verb_count += 1
                    
        action_verb_ratio = action_verb_count / max(1, len(bullet_lines))
        
        # Check for dates in experience/education
        has_dates = bool(re.search(r'\b\d{4}\b', text))
        
        # Calculate content score
        content_score = 8.0  # Start with a decent score
        
        if has_personal_pronouns:
            content_score -= 1.5
            
        if has_references:
            content_score -= 1.0
            
        if action_verb_ratio < 0.5:
            content_score -= 2.0
        elif action_verb_ratio < 0.7:
            content_score -= 1.0
            
        if not has_dates:
            content_score -= 1.5
            
        return {
            "content_score": max(0, content_score) / 10.0,  # Normalize to 0-1
            "has_objective": has_objective,
            "has_references": has_references,
            "has_personal_pronouns": has_personal_pronouns,
            "action_verb_ratio": action_verb_ratio,
            "has_dates": has_dates
        }
        
    def _analyze_sections(self, text: str) -> Dict[str, object]:
        """Analyze resume sections for completeness.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary of section analysis
        """
        # Identify sections in the resume
        lines = text.split('\n')
        potential_headers = [line.strip().lower() for line in lines if line.strip() and len(line.strip()) < 30]
        
        found_sections = []
        for header in potential_headers:
            clean_header = re.sub(r'[^\w\s]', '', header)
            for expected in self.expected_sections:
                if expected in clean_header:
                    found_sections.append(expected)
                    break
                    
        # Essential sections that should be present
        essential_sections = ["education", "experience", "skills"]
        missing_essential = [section for section in essential_sections 
                            if not any(section in found for found in found_sections)]
        
        section_score = 10.0
        section_score -= len(missing_essential) * 3.0
        
        return {
            "score": max(0, section_score) / 10.0,  # Normalize to 0-1
            "found_sections": found_sections,
            "missing_essential": missing_essential
        }
        
    def _analyze_keywords(self, resume_text: str, job_description: str) -> Dict[str, object]:
        """Analyze keyword matching between resume and job description.
        
        Args:
            resume_text: Resume text
            job_description: Job description
            
        Returns:
            Dictionary of keyword analysis
        """
        # Extract important keywords from job description
        job_doc = self.nlp(job_description)
        
        # Get nouns, proper nouns, and technical terms
        keywords = []
        for token in job_doc:
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
                keywords.append(token.text.lower())
                
        # Add noun phrases
        for chunk in job_doc.noun_chunks:
            kw = chunk.text.lower()
            if len(kw.split()) > 1:  # Multi-word terms
                keywords.append(kw)
                
        # Remove duplicates and single-character keywords
        keywords = [kw for kw in set(keywords) if len(kw) > 1]
        
        # Remove common stopwords from keywords
        keywords = [kw for kw in keywords if kw not in self.stop_words]
        
        # Weight keywords by frequency in job description
        keyword_freq = {}
        for kw in keywords:
            count = job_description.lower().count(kw)
            keyword_freq[kw] = count
            
        # Sort keywords by frequency
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 20 keywords
        top_keywords = {k: v for k, v in sorted_keywords[:min(20, len(sorted_keywords))]}
        
        # Check for keyword presence in resume
        keyword_matches = {}
        for keyword, freq in top_keywords.items():
            count = resume_text.lower().count(keyword)
            keyword_matches[keyword] = {
                "frequency_in_job": freq,
                "found_in_resume": count > 0,
                "count_in_resume": count
            }
            
        # Calculate match score
        matched_count = sum(1 for km in keyword_matches.values() if km["found_in_resume"])
        keyword_match_ratio = matched_count / max(1, len(keyword_matches))
        
        # Calculate weighted score considering keyword importance
        weighted_match = 0
        total_weight = sum(data["frequency_in_job"] for data in keyword_matches.values())
        
        if total_weight > 0:
            for keyword, data in keyword_matches.items():
                weight = data["frequency_in_job"] / total_weight
                weighted_match += weight * (1 if data["found_in_resume"] else 0)
        
        # Final keyword match score
        match_score = 0.7 * keyword_match_ratio + 0.3 * weighted_match
        
        return {
            "match_score": match_score,
            "keyword_match_ratio": keyword_match_ratio,
            "weighted_match": weighted_match,
            "keyword_matches": keyword_matches,
            "missing_keywords": [kw for kw, data in keyword_matches.items() if not data["found_in_resume"]]
        }
        
    def _generate_suggestions(self, analysis_results: Dict) -> List[str]:
        """Generate improvement suggestions based on analysis.
        
        Args:
            analysis_results: Analysis results from analyze_resume
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Readability suggestions
        readability = analysis_results["readability"]
        if readability["score"] < 0.7:
            if readability["flesch_reading_ease"] < 30:
                suggestions.append("Simplify language for better readability")
            elif readability["flesch_reading_ease"] > 70:
                suggestions.append("Use more professional language")
                
            if readability["percent_long_sentences"] > 0.3:
                suggestions.append("Break down long sentences into shorter, clearer statements")
                
        # Formatting suggestions
        formatting = analysis_results["formatting"]
        if formatting["score"] < 0.8:
            for issue, found in formatting["issues_found"].items():
                if found:
                    suggestions.append(f"Remove {issue.replace('_', ' ')} for better ATS compatibility")
                    
            if formatting["excessive_bullets"]:
                suggestions.append("Reduce the number of bullet points")
                
            if formatting["excessive_whitespace"]:
                suggestions.append("Reduce excess whitespace")
                
        # Content suggestions
        content = analysis_results["content_analysis"]
        if content["has_personal_pronouns"]:
            suggestions.append("Remove personal pronouns (I, me, my)")
            
        if content["has_references"]:
            suggestions.append("Remove references section to save space (provide upon request)")
            
        if content["action_verb_ratio"] < 0.7:
            suggestions.append("Start more bullet points with strong action verbs")
            
        if not content["has_dates"]:
            suggestions.append("Add dates to work experience and education")
            
        # Section suggestions
        if analysis_results["section_analysis"]["missing_essential"]:
            for section in analysis_results["section_analysis"]["missing_essential"]:
                suggestions.append(f"Add missing {section} section")
                
        # Keyword suggestions
        if "keyword_analysis" in analysis_results:
            keyword_analysis = analysis_results["keyword_analysis"]
            
            if keyword_analysis["match_score"] < 0.6:
                top_missing = keyword_analysis["missing_keywords"][:5]
                if top_missing:
                    suggestions.append(f"Add missing keywords: {', '.join(top_missing)}")
                    
            if keyword_analysis["match_score"] < 0.4:
                suggestions.append("Rework resume to better match job description requirements")
                
        return suggestions
