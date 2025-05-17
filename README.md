# AI Resume Optimization Tool

An intelligent resume optimization system that generates ATS-friendly resumes tailored to specific job descriptions, with seamless integration into Overleaf LaTeX templates.

## Features

- AI-powered resume optimization using modern LLMs
- ATS (Applicant Tracking System) compatibility analysis
- Job description keyword extraction and matching
- Professional resume formatting in LaTeX templates
- Overleaf integration for seamless document management
- Automated keyword optimization and content generation

## Project Structure

```
.
├── src/              # Source code
│   ├── core/         # Main optimization logic
│   ├── models/       # AI model integration
│   ├── utils/        # Utility functions
│   └── templates/    # LaTeX template configurations
├── tests/            # Test files
├── requirements.txt  # Project dependencies
└── setup.py         # Package configuration
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up OpenAI API key:
Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python -m src.main
```

## Usage

1. Input your current resume (in PDF or Word format)
2. Paste the target job description
3. Select your preferred LaTeX template
4. The tool will:
   - Analyze the job description for key requirements
   - Extract relevant keywords and skills
   - Generate optimized content
   - Format the resume in your chosen LaTeX template
   - Upload to Overleaf for final review

## Development

The project follows PEP 8 style guidelines. Use `black` for formatting and `flake8` for linting.

## License

MIT License
