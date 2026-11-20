# AI Resume Enhancer & ATS Analyzer

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-API%20Enabled-orange.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![ReportLab](https://img.shields.io/badge/ReportLab-PDF%20Generation-red.svg)](https://www.reportlab.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, full-stack AI web application designed to help job seekers audit ATS compatibility, match resumes against job descriptions, enhance bullet points using the STAR methodology with Google Gemini AI, and generate downloadable ATS-compliant PDF resumes across multiple professional templates.

---

## 🌟 Key Features

### 1. 📄 Multi-Format Resume Upload & Parsing
- Drag-and-drop file upload supporting **PDF** (`PyMuPDF`) and **Word** (`python-docx`).
- Automated segmentation of Contact Information, Professional Summary, Work Experience, Technical Skills, Projects, Education, and Certifications.
- File type validation and 16 MB size guardrails.

### 2. 🎯 Algorithmic ATS Compatibility Analyzer
- Multi-criteria ATS scoring engine evaluating:
  - **Section Completeness (20%)**: Contact, Summary, Experience, Education, Skills.
  - **Skills & Keyword Variety (25%)**: Breadth across Languages, Frameworks, Cloud, Databases, and Tools.
  - **Experience Quality & Metrics (25%)**: Action verb density, STAR formatting, and quantified results (%, $, metrics).
  - **Formatting & Readability (20%)**: Word count balance (350–950 words) and structured bullet points.
  - **Online Presence (10%)**: Email, phone, LinkedIn, and GitHub / portfolio link validation.
- Interactive **SVG circular progress gauge** displaying score out of 100.
- Clear disclaimers indicating algorithmic estimation.

### 3. 🎯 Job Description Matching & Keyword Gap Analysis
- Paste target job postings to automatically extract technical requirements.
- Side-by-side comparison displaying **Matched Keywords** (green tags) and **Missing Keywords** (red tags).
- Estimated **Job Match Percentage** gauge.
- **Evidence-Backed Skill Bridging**: Suggests transferable skills grounded strictly in the candidate's actual experience without fabricating false claims.

### 4. 🤖 Fact-Preserving AI Resume Enhancer (Google Gemini)
- Powered by the Google Gemini API (`gemini-2.5-flash` / `gemini-1.5-flash`).
- **Professional Summary Rewrite**: Punchy, ATS-optimized, high-impact career statements.
- **STAR Accomplishment Elevation**: Transforms passive phrasing ("responsible for", "worked on") into active engineering accomplishments ("Architected", "Spearheaded", "Streamlined").
- **Strict Anti-Hallucination Policy**: Preserves candidate's authentic facts, employers, degrees, and technologies.
- **Offline Rule-Based Fallback**: Seamlessly switches to a rule-based optimization engine if the Gemini API key is unset or rate-limited.

### 5. 📊 Resume Improvement Dashboard
- Before-and-after comparison view for Summary, Experience, and Projects.
- Side-by-side original score vs. projected improved score (+15–20 point boost).
- One-click copy-to-clipboard buttons for easy transfer.

### 6. 🛠️ Resume Builder & PDF Studio
- Real-time live resume preview updating dynamically as you edit.
- **Three Professional ATS Templates**:
  1. **Modern Blue**: Clean primary blue accent headers and crisp divider rules.
  2. **Executive Slate**: Sophisticated dark slate centered header with double borders.
  3. **Minimalist Tech**: High-contrast monochrome layout with clean monospace accents.
- High-resolution downloadable PDF output built directly with **ReportLab**.

### 7. 🗄️ SQLite History & Persistence
- Automatically logs past analyses, scores, target job titles, and timestamps in SQLite.
- Review past improvements or delete records on demand.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.11+, Flask, Werkzeug, python-dotenv |
| **Document Processing** | PyMuPDF (`pymupdf`), python-docx |
| **AI Integration** | Google Gemini API (`google-genai` SDK) |
| **PDF Generation** | ReportLab 4.2+ |
| **Database** | SQLite3 |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Bootstrap 5.3, Bootstrap Icons |

---

## 📂 Project Structure

```text
AI-Resume-Enhancer/
│
├── app.py                  # Main Flask application & route controllers
├── config.py               # Application configuration & environment settings
├── database.py             # SQLite database operations & schema initialization
├── resume_parser.py        # PDF & DOCX extraction and section segmentation
├── ats_analyzer.py         # Multi-criteria ATS scoring engine
├── job_matcher.py          # Job description parsing & keyword comparison
├── ai_enhancer.py          # Gemini API integration & rule-based fallback
├── pdf_generator.py        # ReportLab PDF generator (3 templates)
├── test_app.py             # Comprehensive automated test suite
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Master layout with responsive sidebar & navbar
│   ├── index.html          # Modern SaaS landing page
│   ├── dashboard.html      # Central operations & metrics dashboard
│   ├── upload.html         # Drag-and-drop resume upload interface
│   ├── analysis.html       # ATS score circular gauge & category breakdown
│   ├── job_match.html      # Job description matcher & keyword gap analysis
│   ├── enhancement.html    # AI before-and-after comparison studio
│   ├── builder.html        # Live resume editor with template switcher
│   ├── history.html        # SQLite analysis history & management
│   └── about.html          # Architecture overview & ATS scoring guide
│
├── static/
│   ├── css/
│   │   └── style.css       # Deep navy & royal blue custom design system
│   ├── js/
│   │   └── script.js       # Drag-and-drop, real-time builder sync, copy helpers
│   └── images/             # Static brand graphics
│
├── uploads/                # User uploaded resumes (PDF / DOCX)
├── generated_resumes/      # Downloadable ReportLab PDFs
│
├── requirements.txt        # Python dependency manifest
├── .env                    # Active local environment variables
├── .env.example            # Environment template
├── .gitignore              # Ignored files (virtualenvs, db, caches)
└── README.md               # Complete project documentation
```

---

## 🚀 Installation & Execution (Windows CMD)

Follow these exact steps to set up and run the project locally on Windows:

### Step 1: Open Windows Command Prompt
Open `cmd.exe` and navigate to the project directory:
```cmd
cd "D:\cloudand devopsproject\AI-Resume-Enhancer"
```

### Step 2: Create a Virtual Environment
```cmd
python -m venv venv
```

### Step 3: Activate the Virtual Environment
```cmd
venv\Scripts\activate
```

### Step 4: Install Dependencies
```cmd
pip install -r requirements.txt
```

### Step 5: Configure Your Gemini API Key
Create or edit `.env` in the project root:
```cmd
copy .env.example .env
```
Open `.env` in Notepad or VS Code and add your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
PORT=5000
SECRET_KEY=dev-secret-key-ai-resume-enhancer-2026
```
*(Note: If no API key is provided, the application runs seamlessly in **Intelligent Rule-Based Mode**).*

### Step 6: Run the Flask Application
```cmd
python app.py
```

### Step 7: Open in Your Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests

To run the complete automated test suite (verifying PDF parsing, DOCX extraction, ATS analysis, job matching, AI enhancement, ReportLab PDF generation, and all Flask routes):

```cmd
python test_app.py
```

Expected output:
```text
Ran 7 tests in 0.49s

OK
✓ PDF parsing passed successfully.
✓ DOCX parsing passed successfully.
✓ ATS Analysis passed. Calculated score: 92/100
✓ Job Matching passed. Match percentage: 75%
✓ AI & Rule-based Enhancement passed.
✓ PDF generation for template 'modern_blue' verified.
✓ PDF generation for template 'executive_slate' verified.
✓ PDF generation for template 'minimalist_tech' verified.
✓ All 10 Flask routes tested successfully with status code 200!
```

---

## 🔒 Security & Privacy

- **Strict File Type Enforcement**: Only `.pdf` and `.docx` extensions allowed.
- **Secure File Sanitization**: Filenames are sanitized via `werkzeug.utils.secure_filename` and assigned randomized UUID prefixes to prevent directory traversal.
- **Local Isolation**: All files, extracted text, and analysis records remain local to your machine within SQLite.
- **Protected Credentials**: API keys are loaded via `python-dotenv` and never exposed to the client or version control.

---

## 🔮 Future Enhancements

- [ ] Multi-language resume parsing (Spanish, German, French).
- [ ] Cover letter generator tailored to matched job descriptions.
- [ ] LinkedIn profile PDF import integration.
- [ ] Direct export to Google Drive / OneDrive.

---

## 📄 License

This project is licensed under the MIT License. Built with passion for software engineering portfolios and job seekers worldwide.
