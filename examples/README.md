# AI Resume Optimizer Examples

This directory contains example files to demonstrate how to use the AI Resume Optimization Tool.

## Sample Files

- `sample_resume.txt`: A sample resume text file
- `sample_job_description.txt`: A sample job description

## How to Use

### Basic Usage

To optimize a resume for a specific job description:

```bash
python -m src.main --resume examples/sample_resume.txt --job-description examples/sample_job_description.txt
```

This will:
1. Analyze the original resume for ATS compatibility
2. Extract keywords from the job description
3. Optimize the resume content using AI
4. Generate a LaTeX document using the default professional template
5. Save the result as `optimized_resume.tex`
6. Upload to Overleaf (if OVERLEAF_TOKEN is set in your .env file)

### Advanced Options

The tool supports several command-line options:

```bash
python -m src.main \
  --resume examples/sample_resume.txt \
  --job-description examples/sample_job_description.txt \
  --template professional \
  --output my_resume.tex \
  --project-name "My Optimized Resume" \
  --analyze-only \
  --no-overleaf
```

Option explanations:
- `--template`: LaTeX template to use (default: professional)
- `--output`: Output file name (default: optimized_resume.tex)
- `--project-name`: Name for Overleaf project (default: Optimized Resume)
- `--analyze-only`: Only analyze the resume without optimization (flag)
- `--no-overleaf`: Skip Overleaf upload (flag)

## Example Output

Running the optimizer will produce a LaTeX file that can be compiled into a professional-looking PDF. The tool will also provide an ATS compatibility analysis and improvement suggestions for your resume.

## Notes

- For optimal results, save the job description you're targeting as a text file
- If you don't have a PDF or DOCX resume, you can use a text file as in this example
- Set your OpenAI API key in the `.env` file for AI-powered optimization
- Set your Overleaf API token in the `.env` file for Overleaf integration
