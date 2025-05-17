# AI Resume Optimization Tool

An intelligent resume optimization system that generates ATS-friendly resumes tailored to specific job descriptions, with seamless integration into Overleaf LaTeX templates.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **AI-Powered Optimization**: Uses OpenAI to tailor resumes to specific job descriptions
- **ATS Compatibility Analysis**: Comprehensive scoring and suggestions for ATS-friendly formatting
- **Keyword Extraction & Matching**: Identifies important keywords from job descriptions
- **Multiple LaTeX Templates**: Professional, Modern, and Academic templates available
- **Overleaf Integration**: Seamless upload to Overleaf for online editing
- **Dual Interfaces**: Both web and command-line interfaces available
- **Before/After Comparison**: Visual comparison of original and optimized resumes
- **Detailed Improvement Suggestions**: Actionable feedback to enhance resume quality

## Project Structure

```
.
├── src/                # Source code
│   ├── core/           # Core optimization logic
│   │   ├── resume_optimizer.py    # Resume content optimization
│   │   ├── ats_analyzer.py        # ATS compatibility analysis
│   │   ├── template_manager.py    # LaTeX template management
│   │   └── overleaf_connector.py  # Overleaf API integration
│   ├── web/            # Web interface
│   │   ├── app.py                 # Flask application
│   │   └── templates/             # HTML templates
│   ├── utils/          # Utility functions
│   │   ├── file_handler.py        # File operations
│   │   └── env_validator.py       # Environment validation
│   └── templates/      # LaTeX templates
│       ├── professional.tex       # Professional template
│       ├── modern.tex             # Modern template
│       └── academic.tex           # Academic CV template
├── examples/           # Example files
├── requirements.txt    # Project dependencies
├── setup.py           # Package configuration
├── run_web_app.py     # Web application runner
├── optimize_resume.py # CLI application
├── Dockerfile         # Docker configuration
└── docker-compose.yml # Docker Compose configuration
```

## Setup

### Option 1: Standard Installation

1. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Download NLP models:**
```bash
python -m spacy download en_core_web_sm
```

4. **Set up environment variables:**
Create a `.env` file in the project root with:
```
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - for Overleaf integration
OVERLEAF_TOKEN=your_overleaf_token_here

# Optional - for customization
MODEL=gpt-4-turbo
MAX_TOKENS=2000
```

### Option 2: Docker Installation

1. **Set up environment variables:**
Create a `.env` file as described above.

2. **Build and run with Docker Compose:**
```bash
docker-compose up -d
```

This will start the web application on http://localhost:5000.

## Usage

### Web Interface

1. **Start the web application:**
```bash
python run_web_app.py
```

2. **Open your browser** and navigate to http://localhost:5000

3. **Upload your resume** (PDF, DOCX, or TXT format)

4. **Provide a job description** by pasting text or uploading a file

5. **Select a template** (Professional, Modern, or Academic)

6. **Click "Optimize Resume"** to start the process

7. **Review the results** showing:
   - ATS compatibility scores (before and after)
   - Keyword analysis
   - Content comparison
   - Improvement suggestions

8. **Download the LaTeX file** or open it directly in Overleaf

### Command Line Interface

**Basic usage:**
```bash
python optimize_resume.py --resume examples/sample_resume.txt --job-description examples/sample_job_description.txt
```

**Advanced options:**
```bash
python optimize_resume.py \
  --resume examples/sample_resume.txt \
  --job-description examples/sample_job_description.txt \
  --template modern \
  --output my_optimized_resume.tex \
  --project-name "My Optimized Resume" \
  --analyze-only \
  --no-overleaf
```

**Help information:**
```bash
python optimize_resume.py --help
```

## Templates

The system includes three LaTeX templates for different needs:

1. **Professional** (`professional.tex`): Traditional professional resume layout
2. **Modern** (`modern.tex`): Modern design with color accents and contemporary styling
3. **Academic** (`academic.tex`): Academic CV format with sections for publications, grants, etc.

You can preview these templates in the `src/templates/` directory.

## ATS Optimization

The tool analyzes and improves resumes for ATS compatibility in several ways:

- **Readability Analysis**: Ensures content is easily readable by both humans and machines
- **Formatting Checks**: Identifies formatting issues that might confuse ATS systems
- **Keyword Optimization**: Strategically incorporates keywords from job descriptions
- **Section Analysis**: Ensures all essential resume sections are present
- **Content Scoring**: Evaluates the quality and relevance of resume content

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development

The project follows PEP 8 style guidelines. Use `black` for formatting and `flake8` for linting.

```bash
# Install development dependencies
pip install black flake8 pytest

# Format code
black src/

# Lint code
flake8 src/
```

## License

MIT License

## Acknowledgments

- OpenAI for providing the AI models used in content optimization
- Overleaf for LaTeX integration capabilities
