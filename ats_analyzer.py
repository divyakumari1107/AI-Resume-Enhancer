import re


STRONG_ACTION_VERBS = [
    "accelerated", "accomplished", "achieved", "administered", "advanced", "advised",
    "analyzed", "architected", "automated", "boosted", "built", "centralized",
    "collaborated", "configured", "consolidated", "constructed", "coordinated",
    "created", "debugged", "decreased", "delivered", "deployed", "designed",
    "developed", "devised", "directed", "documented", "drove", "eliminated",
    "enabled", "engineered", "enhanced", "established", "executed", "expanded",
    "expedited", "facilitated", "formulated", "generated", "guided", "implemented",
    "improved", "increased", "initiated", "innovated", "installed", "integrated",
    "launched", "lead", "led", "managed", "maximized", "mentored", "migrated",
    "minimized", "modernized", "negotiated", "optimized", "orchestrated", "organized",
    "overhauled", "pioneered", "planned", "produced", "programmed", "reduced",
    "refactored", "resolved", "restructured", "revamped", "scaled", "secured",
    "simplified", "solved", "spearheaded", "standardized", "streamlined", "strengthened",
    "supervised", "surpassed", "synthesized", "trained", "transformed", "upgraded"
]

WEAK_PHRASES = [
    "responsible for", "helped with", "worked on", "assisted in", "duties included",
    "handled", "participated in", "tasked with", "involved in", "tried to", "various tasks"
]


def analyze_ats(parsed_data, raw_text):
    """
    Perform a comprehensive multi-criteria ATS compatibility analysis on parsed resume data.
    Returns calculated score (0-100), breakdown by section, key strengths, actionable suggestions,
    and estimated improved score.
    """
    # 1. Section Completeness Analysis (Weight: 20%)
    section_score = 0
    section_feedback = []
    missing_sections = []

    contact = parsed_data.get("contact", {})
    if contact.get("email") and contact.get("phone"):
        section_score += 5
    elif contact.get("email") or contact.get("phone"):
        section_score += 3
        section_feedback.append("Include both a phone number and professional email address.")
    else:
        missing_sections.append("Contact Details (Email & Phone)")

    summary = parsed_data.get("summary", "")
    summary_words = len(summary.split())
    if summary_words >= 30:
        section_score += 4
    elif summary_words > 10:
        section_score += 2
        section_feedback.append("Expand your professional summary to 40-70 words highlighting your core value.")
    else:
        missing_sections.append("Professional Summary")

    experience = parsed_data.get("experience", "")
    if len(experience.split()) >= 80:
        section_score += 4
    elif len(experience.split()) >= 30:
        section_score += 2
        section_feedback.append("Flesh out your work experience with detailed accomplishments.")
    else:
        missing_sections.append("Work Experience")

    education = parsed_data.get("education", "")
    if len(education.split()) >= 10:
        section_score += 3
    else:
        missing_sections.append("Education Details")

    all_skills = parsed_data.get("all_skills", [])
    if len(all_skills) >= 6:
        section_score += 4
    elif len(all_skills) >= 2:
        section_score += 2
        section_feedback.append("Organize your skills in a dedicated, clearly labelled Skills section.")
    else:
        missing_sections.append("Dedicated Skills Section")

    # Normalized Section Completeness Score (0 - 100)
    section_comp_pct = min(100, int((section_score / 20) * 100))

    # 2. Skills & Keyword Variety Analysis (Weight: 25%)
    skills_score = 0
    skills_feedback = []
    total_skills = len(all_skills)

    if total_skills >= 15:
        skills_score = 100
    elif total_skills >= 10:
        skills_score = 85
    elif total_skills >= 6:
        skills_score = 65
        skills_feedback.append("Add more domain-specific technical keywords and industry-standard tools.")
    elif total_skills >= 3:
        skills_score = 45
        skills_feedback.append("Your resume has few detected skills. Add technical languages, frameworks, and methodologies.")
    else:
        skills_score = 25
        skills_feedback.append("Very few skills detected. Standard ATS systems rely heavily on keyword indexing.")

    # Check category distribution
    categories = parsed_data.get("skills", {})
    categories_present = sum(1 for cat, sk in categories.items() if len(sk) > 0)
    if categories_present < 3:
        skills_score = max(20, skills_score - 15)
        skills_feedback.append("Diversify skills into technical categories: Languages, Frameworks, Cloud, Databases, and Tools.")

    # 3. Experience Quality, Action Verbs & Metrics (Weight: 25%)
    exp_score = 0
    exp_feedback = []
    bullets = parsed_data.get("experience_bullets", []) + parsed_data.get("project_bullets", [])
    
    strong_verb_count = 0
    weak_phrase_count = 0
    metric_count = 0

    lower_text = raw_text.lower()
    for verb in STRONG_ACTION_VERBS:
        if re.search(rf'\b{verb}\b', lower_text):
            strong_verb_count += 1

    for phrase in WEAK_PHRASES:
        if phrase in lower_text:
            weak_phrase_count += 1

    # Detect metric numbers and percentages (e.g., 40%, $50K, 10x, 500+ users)
    metrics_matches = re.findall(r'(\b\d+[\%kKmM\+]?|\$\d+[\d,]*|\b\d+x\b)', raw_text)
    metric_count = len(metrics_matches)

    # Calculate action score
    if strong_verb_count >= 10:
        exp_score += 40
    elif strong_verb_count >= 5:
        exp_score += 28
    else:
        exp_score += 15
        exp_feedback.append(f"Found only {strong_verb_count} strong action verbs. Start each bullet with verbs like 'Spearheaded', 'Engineered', 'Optimized'.")

    # Calculate metric score
    if metric_count >= 6:
        exp_score += 40
    elif metric_count >= 3:
        exp_score += 26
    elif metric_count >= 1:
        exp_score += 18
        exp_feedback.append("Add more quantifiable achievements (e.g. 'improved latency by 35%', 'reduced costs by $12,000').")
    else:
        exp_score += 5
        exp_feedback.append("No quantifiable metrics detected. Quantifying results with numbers and percentages significantly boosts ATS ranking.")

    # Penalty for weak phrases
    if weak_phrase_count > 0:
        exp_score = max(20, exp_score - (weak_phrase_count * 5))
        exp_feedback.append(f"Replace passive phrases like 'responsible for' or 'helped with' with direct action verbs.")
    else:
        exp_score += 20

    experience_pct = min(100, exp_score)

    # 4. Formatting, Structure & Readability (Weight: 20%)
    format_score = 0
    format_feedback = []
    word_count = parsed_data.get("word_count", 0)

    # Ideal resume length: 350 - 950 words
    if 350 <= word_count <= 950:
        format_score += 40
    elif 250 <= word_count < 350:
        format_score += 25
        format_feedback.append(f"Resume is on the shorter side ({word_count} words). Aim for 400-800 words with richer descriptions.")
    elif 950 < word_count <= 1400:
        format_score += 28
        format_feedback.append(f"Resume is long ({word_count} words). Keep concise for quick ATS parsing.")
    else:
        format_score += 15
        format_feedback.append(f"Resume word count ({word_count}) is outside typical ATS standards (350 - 900 words).")

    # Structured bullets check
    total_bullets = len(bullets)
    if total_bullets >= 8:
        format_score += 35
    elif total_bullets >= 4:
        format_score += 25
    else:
        format_score += 10
        format_feedback.append("Convert paragraph text into distinct bullet points for better ATS readability.")

    # Standard headings check
    if len(missing_sections) == 0:
        format_score += 25
    else:
        format_score += max(5, 25 - (len(missing_sections) * 6))
        format_feedback.append(f"Add standard ATS section headings for: {', '.join(missing_sections)}.")

    format_pct = min(100, format_score)

    # 5. Contact & Professional Links (Weight: 10%)
    contact_score = 0
    contact_feedback = []
    if contact.get("email"):
        contact_score += 35
    else:
        contact_feedback.append("Missing email address.")

    if contact.get("phone"):
        contact_score += 25
    else:
        contact_feedback.append("Missing phone number.")

    if contact.get("linkedin"):
        contact_score += 20
    else:
        contact_feedback.append("Add a LinkedIn profile URL.")

    if contact.get("github") or contact.get("portfolio"):
        contact_score += 20
    else:
        contact_feedback.append("Include a GitHub or portfolio link to showcase actual work.")

    contact_pct = min(100, contact_score)

    # Overall Calculated Weighted Score
    overall_score = round(
        (section_comp_pct * 0.20) +
        (skills_score * 0.25) +
        (experience_pct * 0.25) +
        (format_pct * 0.20) +
        (contact_pct * 0.10)
    )
    overall_score = max(10, min(99, overall_score))  # realistic score range

    # Projected improved score with AI optimization
    improved_score = min(98, overall_score + 18)

    # Determine status labels
    def get_status(score):
        if score >= 80:
            return "Excellent", "success"
        elif score >= 65:
            return "Good", "primary"
        elif score >= 45:
            return "Needs Improvement", "warning"
        else:
            return "Critical", "danger"

    sections_breakdown = [
        {
            "name": "Section Completeness",
            "score": section_comp_pct,
            "weight": "20%",
            "status": get_status(section_comp_pct)[0],
            "badge_color": get_status(section_comp_pct)[1],
            "details": f"{5 - len(missing_sections)} of 5 standard resume sections properly identified.",
            "tips": section_feedback
        },
        {
            "name": "Skills & Technical Keywords",
            "score": skills_score,
            "weight": "25%",
            "status": get_status(skills_score)[0],
            "badge_color": get_status(skills_score)[1],
            "details": f"{total_skills} skills indexed across {categories_present} technical domains.",
            "tips": skills_feedback
        },
        {
            "name": "Experience Quality & Metrics",
            "score": experience_pct,
            "weight": "25%",
            "status": get_status(experience_pct)[0],
            "badge_color": get_status(experience_pct)[1],
            "details": f"{strong_verb_count} action verbs and {metric_count} quantified achievements detected.",
            "tips": exp_feedback
        },
        {
            "name": "Formatting & Readability",
            "score": format_pct,
            "weight": "20%",
            "status": get_status(format_pct)[0],
            "badge_color": get_status(format_pct)[1],
            "details": f"{word_count} total words organized into {total_bullets} bullet points.",
            "tips": format_feedback
        },
        {
            "name": "Contact & Online Presence",
            "score": contact_pct,
            "weight": "10%",
            "status": get_status(contact_pct)[0],
            "badge_color": get_status(contact_pct)[1],
            "details": f"Email, phone, and professional portfolio presence.",
            "tips": contact_feedback
        }
    ]

    # Strengths compilation
    strengths = []
    if section_comp_pct >= 75:
        strengths.append("Standard resume sections are well-structured and easy for automated parsers to traverse.")
    if total_skills >= 10:
        strengths.append(f"Strong technical vocabulary with {total_skills} recognized skills across multiple categories.")
    if strong_verb_count >= 7:
        strengths.append(f"Effective use of active voice with {strong_verb_count} strong action verbs.")
    if metric_count >= 3:
        strengths.append(f"Great focus on business results with {metric_count} quantifiable metrics.")
    if contact.get("linkedin") and (contact.get("github") or contact.get("portfolio")):
        strengths.append("Complete professional online presence with verified links.")
    if not strengths:
        strengths.append("Found clear, readable text format with recognizable contact details.")

    # Priority actionable suggestions
    suggestions = []
    for item in sections_breakdown:
        for tip in item["tips"]:
            if tip and tip not in suggestions:
                suggestions.append(tip)

    if not suggestions:
        suggestions.append("Tailor your resume specifically for each target job description to match exact required keywords.")

    return {
        "overall_score": overall_score,
        "improved_score": improved_score,
        "overall_status": get_status(overall_score)[0],
        "overall_badge": get_status(overall_score)[1],
        "sections_breakdown": sections_breakdown,
        "strengths": strengths,
        "suggestions": suggestions[:8],
        "missing_sections": missing_sections,
        "stats": {
            "total_skills": total_skills,
            "strong_verbs": strong_verb_count,
            "metrics_count": metric_count,
            "word_count": word_count,
            "bullet_count": total_bullets
        },
        "disclaimer": "This score is an automated estimation based on parsing heuristics, keyword frequency, and ATS industry standards. Actual employer ATS platforms (Workday, Taleo, Greenhouse, etc.) use custom proprietary scoring algorithms."
    }
