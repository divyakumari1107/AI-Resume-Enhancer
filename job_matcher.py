import re
from resume_parser import extract_skills_from_text, COMMON_SKILLS_DB


# Mappings of related skills for realistic recommendations
RELATED_SKILLS_MAP = {
    "Docker": ["Kubernetes", "Containerization", "Microservices", "CI/CD"],
    "Kubernetes": ["Docker", "Helm", "Cloud Deployment", "Microservices"],
    "Python": ["FastAPI", "Flask", "Django", "Data Processing", "PyTest"],
    "Flask": ["FastAPI", "Django", "REST APIs", "Python"],
    "Django": ["Flask", "FastAPI", "PostgreSQL", "REST APIs"],
    "JavaScript": ["TypeScript", "Node.js", "React", "Frontend Development"],
    "TypeScript": ["JavaScript", "Node.js", "React", "Next.js"],
    "React": ["Next.js", "Redux", "TypeScript", "Frontend Architecture"],
    "SQL": ["PostgreSQL", "MySQL", "Database Design", "Performance Optimization"],
    "PostgreSQL": ["MySQL", "SQL", "Database Optimization", "Redis"],
    "AWS": ["CloudFormation", "Terraform", "Serverless", "S3", "EC2", "Lambda"],
    "Git": ["GitHub Actions", "CI/CD", "Version Control", "GitLab CI"],
    "Linux": ["Bash", "Shell Scripting", "DevOps", "System Administration"]
}


def extract_job_keywords(job_description):
    """
    Extract technical skills, methodologies, frameworks, and qualifications
    from a job description text.
    """
    job_skills_data = extract_skills_from_text(job_description)
    job_skills = job_skills_data["all_skills"]

    # Also detect common industry qualifications and keywords
    lower_jd = job_description.lower()
    additional_keywords = []

    domain_patterns = [
        (r'\b(bachelor\'?s?|master\'?s?|degree|computer science|engineering)\b', "CS Degree / Equivalent"),
        (r'\b(ci\/cd|continuous integration|deployment pipeline)\b', "CI/CD"),
        (r'\b(rest|restful|api design)\b', "REST APIs"),
        (r'\b(microservices|distributed systems)\b', "Microservices"),
        (r'\b(agile|scrum|sprint)\b', "Agile / Scrum"),
        (r'\b(unit testing|tdd|test driven)\b', "Unit Testing"),
        (r'\b(cloud native|scalable architecture)\b', "Scalable Architecture"),
        (r'\b(performance optimization|caching)\b', "Performance Optimization")
    ]

    for pattern, label in domain_patterns:
        if re.search(pattern, lower_jd) and label not in job_skills:
            additional_keywords.append(label)

    # Detect minimum years of experience if mentioned
    exp_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience', lower_jd)
    required_exp_years = int(exp_match.group(1)) if exp_match else None

    all_target_keywords = sorted(list(set(job_skills + additional_keywords)))
    return {
        "skills": job_skills,
        "additional_requirements": additional_keywords,
        "all_target_keywords": all_target_keywords,
        "required_exp_years": required_exp_years
    }


def compare_resume_with_job(resume_parsed, raw_resume_text, job_description):
    """
    Compare parsed resume content with a job description.
    Returns matched keywords, missing keywords, match percentage, and
    evidence-backed recommendations.
    """
    job_data = extract_job_keywords(job_description)
    target_keywords = job_data["all_target_keywords"]
    
    if not target_keywords:
        return {
            "match_percentage": 0,
            "matched_keywords": [],
            "missing_keywords": [],
            "job_keywords_count": 0,
            "recommendations": ["The job description does not contain recognizable technical keywords. Please provide a more detailed job posting."],
            "summary": "Unable to calculate match score due to insufficient job description content."
        }

    resume_skills = set(resume_parsed.get("all_skills", []))
    lower_resume_text = " " + raw_resume_text.lower() + " "

    matched = []
    missing = []

    for kw in target_keywords:
        # Check if skill is in parsed skills or raw text
        escaped_kw = re.escape(kw.lower())
        pattern = rf'(?<![a-zA-Z0-9_]){escaped_kw}(?![a-zA-Z0-9_])'
        if kw in resume_skills or re.search(pattern, lower_resume_text):
            matched.append(kw)
        else:
            missing.append(kw)

    total_target = len(target_keywords)
    match_count = len(matched)
    
    # Calculate match percentage (base ratio with slight curve for realism)
    if total_target > 0:
        base_ratio = match_count / total_target
        match_percentage = min(98, max(15, round(base_ratio * 100)))
    else:
        match_percentage = 0

    # Categorize missing keywords
    missing_by_priority = {
        "critical": [],
        "tools_methodologies": [],
        "secondary": []
    }

    for item in missing:
        item_lower = item.lower()
        if any(item_lower in COMMON_SKILLS_DB[k] for k in ["languages", "frameworks", "cloud_devops", "databases"]):
            missing_by_priority["critical"].append(item)
        elif any(item_lower in COMMON_SKILLS_DB[k] for k in ["tools_technologies", "soft_skills"]):
            missing_by_priority["tools_methodologies"].append(item)
        else:
            missing_by_priority["secondary"].append(item)

    # Formulate truthful, evidence-backed skill recommendations
    recommendations = []
    candidate_skills_list = list(resume_skills)

    for cand_skill in candidate_skills_list:
        if cand_skill in RELATED_SKILLS_MAP:
            for related in RELATED_SKILLS_MAP[cand_skill]:
                if related in missing and related not in [r.get("skill") for r in recommendations]:
                    recommendations.append({
                        "skill": related,
                        "bridge_from": cand_skill,
                        "advice": f"The job seeks '{related}'. Since you have experience with '{cand_skill}', highlight any related exposure, coursework, or integration projects involving {related} without overstating your mastery."
                    })

    if not recommendations and missing:
        for m in missing[:3]:
            recommendations.append({
                "skill": m,
                "bridge_from": "General Experience",
                "advice": f"Review whether you have worked with '{m}' in prior projects or coursework. If yes, add it to your skills and describe the project outcome."
            })

    # Summary analysis text
    if match_percentage >= 75:
        match_summary = f"Strong alignment! Your resume matches {match_count} of {total_target} targeted competencies in this job posting."
    elif match_percentage >= 50:
        match_summary = f"Moderate alignment. You match {match_count} of {total_target} requirements, but key skills like {', '.join(missing[:3])} are missing."
    else:
        match_summary = f"Low direct keyword alignment ({match_count}/{total_target}). Submitting without tailoring your resume may lead to early ATS filtering."

    return {
        "match_percentage": match_percentage,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "missing_categorized": missing_by_priority,
        "job_keywords_count": total_target,
        "matched_count": match_count,
        "missing_count": len(missing),
        "recommendations": recommendations[:5],
        "match_summary": match_summary,
        "required_exp_years": job_data["required_exp_years"]
    }
