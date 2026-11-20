import re
import os
import pymupdf  # PyMuPDF
import docx


COMMON_SKILLS_DB = {
    "languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "ruby", "go", "golang",
        "rust", "php", "swift", "kotlin", "scala", "r", "dart", "sql", "html", "html5", "css", "css3", "bash", "shell"
    ],
    "frameworks": [
        "flask", "django", "fastapi", "react", "react.js", "angular", "vue", "vue.js", "next.js",
        "express", "express.js", "node.js", "spring boot", "spring", "asp.net", "laravel", "ruby on rails",
        "tailwind", "bootstrap", "jquery", "redux", "graphql", "rest api", "restful apis"
    ],
    "cloud_devops": [
        "aws", "amazon web services", "azure", "google cloud", "gcp", "docker", "kubernetes", "k8s",
        "terraform", "ansible", "jenkins", "ci/cd", "github actions", "gitlab ci", "circleci",
        "linux", "nginx", "apache", "helm", "prometheus", "grafana", "microservices", "serverless", "cloudformation"
    ],
    "databases": [
        "postgresql", "postgres", "mysql", "mongodb", "sqlite", "redis", "oracle", "cassandra",
        "dynamodb", "elasticsearch", "mariadb", "firebase", "supabase", "mssql", "sql server"
    ],
    "tools_technologies": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "postman", "swagger",
        "unit testing", "pytest", "jest", "selenium", "agile", "scrum", "kanban", "vscode", "pycharm",
        "webpack", "vite", "npm", "yarn", "pnpm", "pip"
    ],
    "data_ai": [
        "machine learning", "deep learning", "artificial intelligence", "nlp", "computer vision",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "opencv", "llm", "genai",
        "gemini", "openai", "langchain", "hugging face", "data analysis", "data visualization", "tableau", "power bi"
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "collaboration", "problem solving",
        "critical thinking", "time management", "adaptability", "mentoring", "ownership",
        "cross-functional", "analytical thinking", "stakeholder management"
    ]
}


def extract_text_from_pdf(file_path):
    """Extract plain text from PDF using PyMuPDF (fitz)."""
    text_content = []
    try:
        doc = pymupdf.open(file_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text:
                text_content.append(text)
        doc.close()
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
    return "\n".join(text_content).strip()


def extract_text_from_docx(file_path):
    """Extract plain text from Word document (.docx) using python-docx."""
    text_content = []
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            if para.text.strip():
                text_content.append(para.text.strip())

        # Also extract text from any tables in the document
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    text_content.append(" | ".join(row_cells))
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
    return "\n".join(text_content).strip()


def extract_resume_text(file_path):
    """Extract text from file based on extension (.pdf or .docx)."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Only PDF and DOCX are allowed.")


def extract_contact_info(text):
    """Extract email, phone, links, and estimated name from resume text."""
    # Email extraction
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else ""

    # Phone extraction (support international & various formats)
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
    phones = re.findall(phone_pattern, text)
    # Filter valid looking phone numbers
    phone_matches = [p[0] for p in re.finditer(r'(\+?\d{1,3}[\s-]?)?\(?\d{3,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}', text)]
    phone = phone_matches[0].strip() if phone_matches else ""

    # LinkedIn extraction
    linkedin_match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|profile)\/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
    linkedin = linkedin_match.group(0) if linkedin_match else ""

    # GitHub extraction
    github_match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
    github = github_match.group(0) if github_match else ""

    # Portfolio / Website
    portfolio_match = re.search(r'(?:https?:\/\/)(?!.*(?:linkedin|github))[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+(?:\/[^\s]*)?', text, re.IGNORECASE)
    portfolio = portfolio_match.group(0) if portfolio_match else ""

    # Candidate Name (heuristic: first 1-3 non-empty lines that don't look like contact/headers)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    candidate_name = "Candidate"
    for line in lines[:5]:
        if len(line) < 50 and not re.search(r'(@|linkedin|github|phone|resume|curriculum|vitae|summary|\+?\d)', line, re.IGNORECASE):
            # Check if line looks like a proper name (letters and spaces)
            if re.match(r'^[A-Z][a-zA-Z\s\.\'-]+$', line) and len(line.split()) in [2, 3, 4]:
                candidate_name = line.strip()
                break
    if candidate_name == "Candidate" and lines:
        first_line = lines[0]
        if len(first_line) < 40 and not "@" in first_line:
            candidate_name = first_line

    return {
        "name": candidate_name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio
    }


def extract_skills_from_text(text):
    """Detect skills across known technical and professional categories."""
    lower_text = " " + text.lower() + " "
    detected_skills = {
        "languages": [],
        "frameworks": [],
        "cloud_devops": [],
        "databases": [],
        "tools_technologies": [],
        "data_ai": [],
        "soft_skills": []
    }
    all_found = set()

    for category, skill_list in COMMON_SKILLS_DB.items():
        for skill in skill_list:
            # Word boundary search
            escaped_skill = re.escape(skill)
            pattern = rf'(?<![a-zA-Z0-9_]){escaped_skill}(?![a-zA-Z0-9_])'
            if re.search(pattern, lower_text):
                clean_name = skill.title() if len(skill) > 3 else skill.upper()
                # Special cases capitalization
                special_cases = {
                    "aws": "AWS", "gcp": "GCP", "sql": "SQL", "html": "HTML", "html5": "HTML5",
                    "css": "CSS", "css3": "CSS3", "ci/cd": "CI/CD", "k8s": "K8s", "nlp": "NLP",
                    "llm": "LLM", "genai": "GenAI", "mongodb": "MongoDB", "postgresql": "PostgreSQL",
                    "mysql": "MySQL", "sqlite": "SQLite", "javascript": "JavaScript", "typescript": "TypeScript",
                    "graphql": "GraphQL", "rest api": "REST APIs", "restful apis": "RESTful APIs",
                    "github actions": "GitHub Actions", "docker": "Docker", "kubernetes": "Kubernetes",
                    "react": "React", "react.js": "React.js", "node.js": "Node.js", "express.js": "Express.js",
                    "vue.js": "Vue.js", "next.js": "Next.js"
                }
                display_name = special_cases.get(skill.lower(), clean_name)
                if display_name not in detected_skills[category]:
                    detected_skills[category].append(display_name)
                    all_found.add(display_name)

    return {
        "categories": detected_skills,
        "all_skills": sorted(list(all_found)),
        "total_count": len(all_found)
    }


def split_resume_into_sections(text):
    """Split resume text into standard resume sections."""
    section_patterns = {
        "summary": r'(?:professional\s+summary|executive\s+summary|summary|profile|about\s+me|objective)',
        "skills": r'(?:technical\s+skills|core\s+competencies|skills\s*(?:&|and)?\s*technologies|skills|technologies|tools)',
        "experience": r'(?:work\s+experience|professional\s+experience|experience|employment\s+history|career\s+history|work\s+history)',
        "education": r'(?:education|academic\s+background|qualifications|academic\s+credentials|academic\s+history)',
        "projects": r'(?:projects|technical\s+projects|personal\s+projects|key\s+projects|academic\s+projects)',
        "certifications": r'(?:certifications|certificates|licenses|achievements|awards|honors|publications)'
    }

    # Identify lines where headers occur
    lines = text.split("\n")
    header_indices = []

    for idx, line in enumerate(lines):
        clean_line = line.strip()
        if not clean_line or len(clean_line) > 50:
            continue
        # Check against each section pattern
        for sec_name, pattern in section_patterns.items():
            regex = rf'^{pattern}\s*:?$'
            if re.match(regex, clean_line, re.IGNORECASE):
                header_indices.append((idx, sec_name, clean_line))
                break

    # If no headers found, fallback to heuristic segmentation
    sections = {
        "summary": "",
        "skills": "",
        "experience": "",
        "education": "",
        "projects": "",
        "certifications": ""
    }

    if not header_indices:
        # Heuristic: First 25% is summary/contact, middle is experience, end is education
        total_len = len(lines)
        sections["summary"] = "\n".join(lines[:max(1, int(total_len * 0.2))]).strip()
        sections["experience"] = "\n".join(lines[int(total_len * 0.2):int(total_len * 0.7)]).strip()
        sections["education"] = "\n".join(lines[int(total_len * 0.7):]).strip()
        return sections

    # Segment text by detected header indices
    for i in range(len(header_indices)):
        start_idx, sec_name, _ = header_indices[i]
        end_idx = header_indices[i + 1][0] if i + 1 < len(header_indices) else len(lines)
        section_body = "\n".join(lines[start_idx + 1:end_idx]).strip()
        # If this section was already encountered, append
        if sections[sec_name]:
            sections[sec_name] += "\n" + section_body
        else:
            sections[sec_name] = section_body

    return sections


def parse_resume(file_path):
    """Full parsing pipeline: extracts text, contact info, sections, and skills."""
    raw_text = extract_resume_text(file_path)
    contact_info = extract_contact_info(raw_text)
    sections = split_resume_into_sections(raw_text)
    skills_data = extract_skills_from_text(raw_text)

    # Clean bullet points in experience and projects
    def clean_bullets(section_text):
        bullets = []
        for line in section_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            # Strip standard bullet characters
            cleaned = re.sub(r'^[•\-\*\>▪▫●]\s*', '', line)
            if cleaned:
                bullets.append(cleaned)
        return bullets

    experience_bullets = clean_bullets(sections["experience"])
    project_bullets = clean_bullets(sections["projects"])

    parsed = {
        "contact": contact_info,
        "summary": sections["summary"],
        "skills": skills_data["categories"],
        "all_skills": skills_data["all_skills"],
        "total_skills_count": skills_data["total_count"],
        "experience": sections["experience"],
        "experience_bullets": experience_bullets,
        "education": sections["education"],
        "projects": sections["projects"],
        "project_bullets": project_bullets,
        "certifications": sections["certifications"],
        "word_count": len(raw_text.split()),
        "character_count": len(raw_text)
    }

    return raw_text, parsed
