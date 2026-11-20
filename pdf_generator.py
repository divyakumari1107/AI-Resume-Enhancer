import os
import xml.sax.saxutils as saxutils
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.units import inch
from config import Config


def escape_xml(text):
    """Safely escape text for ReportLab XML/HTML Paragraph parsing."""
    if not text:
        return ""
    return saxutils.escape(str(text))


def generate_resume_pdf(resume_data, template_name="modern_blue", output_filename=None):
    """
    Generate a professional, downloadable PDF resume from structured resume data
    using one of three distinct ATS-compliant ReportLab templates:
    1. modern_blue - Sleek modern blue accents, high-impact header
    2. executive_slate - Sophisticated dark slate styling with double borders
    3. minimalist_tech - Clean, high-contrast monochrome ATS tech layout
    """
    if not output_filename:
        output_filename = f"resume_{template_name}_{os.urandom(4).hex()}.pdf"
    
    file_path = os.path.join(Config.GENERATED_FOLDER, output_filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch
    )

    styles = getSampleStyleSheet()
    story = []

    # Extract candidate data with safe fallbacks
    contact = resume_data.get("contact", {})
    name = contact.get("name") or "Professional Candidate"
    title = resume_data.get("title") or "Software Engineering Professional"
    email = contact.get("email") or ""
    phone = contact.get("phone") or ""
    linkedin = contact.get("linkedin") or ""
    github = contact.get("github") or ""
    portfolio = contact.get("portfolio") or ""

    summary = resume_data.get("summary") or ""
    skills = resume_data.get("skills") or []
    experience = resume_data.get("experience") or []
    education = resume_data.get("education") or []
    projects = resume_data.get("projects") or []
    certifications = resume_data.get("certifications") or []

    # Contact line assembly
    contact_parts = []
    if email:
        contact_parts.append(email)
    if phone:
        contact_parts.append(phone)
    if linkedin:
        contact_parts.append(linkedin.replace("https://", "").replace("http://", "").replace("www.", ""))
    if github:
        contact_parts.append(github.replace("https://", "").replace("http://", "").replace("www.", ""))
    if portfolio:
        contact_parts.append(portfolio.replace("https://", "").replace("http://", ""))
    contact_str = "  |  ".join(contact_parts)

    # -------------------------------------------------------------
    # TEMPLATE 1: MODERN BLUE
    # -------------------------------------------------------------
    if template_name == "modern_blue":
        primary_color = colors.HexColor("#0D6EFD")
        dark_color = colors.HexColor("#0B192C")
        subtle_color = colors.HexColor("#495057")

        # Name Style
        name_style = ParagraphStyle(
            'ModernName',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=primary_color,
            alignment=0
        )
        # Title Style
        title_style = ParagraphStyle(
            'ModernTitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=15,
            textColor=dark_color,
            alignment=0
        )
        # Contact Style
        contact_style = ParagraphStyle(
            'ModernContact',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=subtle_color,
            alignment=0
        )
        # Section Heading Style
        sec_style = ParagraphStyle(
            'ModernSecHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=15,
            textColor=primary_color,
            spaceAfter=4,
            spaceBefore=10
        )
        # Body Style
        body_style = ParagraphStyle(
            'ModernBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=dark_color,
            alignment=4  # Justify
        )
        # Bullet Style
        bullet_style = ParagraphStyle(
            'ModernBullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=dark_color,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=3
        )

        # Header Block
        story.append(Paragraph(escape_xml(name), name_style))
        story.append(Paragraph(escape_xml(title), title_style))
        story.append(Spacer(1, 3))
        story.append(Paragraph(escape_xml(contact_str), contact_style))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=8))

        # Professional Summary
        if summary:
            story.append(Paragraph("PROFESSIONAL SUMMARY", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=5))
            story.append(Paragraph(escape_xml(summary), body_style))
            story.append(Spacer(1, 6))

        # Technical Skills
        if skills:
            story.append(Paragraph("TECHNICAL SKILLS & CORE COMPETENCIES", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=5))
            if isinstance(skills, list):
                skills_text = " • ".join(skills)
            elif isinstance(skills, dict):
                skills_text = " | ".join([f"<b>{k.replace('_', ' ').title()}:</b> {', '.join(v)}" for k, v in skills.items() if v])
            else:
                skills_text = str(skills)
            story.append(Paragraph(escape_xml(skills_text), body_style))
            story.append(Spacer(1, 6))

        # Experience
        if experience:
            story.append(Paragraph("PROFESSIONAL EXPERIENCE", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=5))
            if isinstance(experience, list):
                for item in experience:
                    story.append(Paragraph(f"• {escape_xml(item)}", bullet_style))
            else:
                for line in str(experience).split("\n"):
                    if line.strip():
                        story.append(Paragraph(f"• {escape_xml(line.strip())}", bullet_style))
            story.append(Spacer(1, 6))

        # Projects
        if projects:
            story.append(Paragraph("KEY PROJECTS & TECHNICAL CONTRIBUTIONS", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=5))
            if isinstance(projects, list):
                for item in projects:
                    story.append(Paragraph(f"• {escape_xml(item)}", bullet_style))
            else:
                for line in str(projects).split("\n"):
                    if line.strip():
                        story.append(Paragraph(f"• {escape_xml(line.strip())}", bullet_style))
            story.append(Spacer(1, 6))

        # Education
        if education:
            story.append(Paragraph("EDUCATION", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=5))
            if isinstance(education, list):
                for item in education:
                    story.append(Paragraph(f"• {escape_xml(item)}", bullet_style))
            else:
                story.append(Paragraph(escape_xml(str(education)), body_style))
            story.append(Spacer(1, 6))

        # Certifications
        if certifications:
            story.append(Paragraph("CERTIFICATIONS & AWARDS", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=5))
            if isinstance(certifications, list):
                for item in certifications:
                    story.append(Paragraph(f"• {escape_xml(item)}", bullet_style))
            else:
                story.append(Paragraph(escape_xml(str(certifications)), body_style))

    # -------------------------------------------------------------
    # TEMPLATE 2: EXECUTIVE SLATE
    # -------------------------------------------------------------
    elif template_name == "executive_slate":
        slate_color = colors.HexColor("#1E293B")
        accent_color = colors.HexColor("#475569")
        dark_charcoal = colors.HexColor("#0F172A")

        name_style = ParagraphStyle(
            'ExecName',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=slate_color,
            alignment=1  # Centered
        )
        title_style = ParagraphStyle(
            'ExecTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=10.5,
            leading=14,
            textColor=accent_color,
            alignment=1  # Centered
        )
        contact_style = ParagraphStyle(
            'ExecContact',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12,
            textColor=accent_color,
            alignment=1  # Centered
        )
        sec_style = ParagraphStyle(
            'ExecSecHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=15,
            textColor=slate_color,
            spaceAfter=3,
            spaceBefore=10
        )
        body_style = ParagraphStyle(
            'ExecBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=dark_charcoal,
            alignment=4
        )
        bullet_style = ParagraphStyle(
            'ExecBullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=dark_charcoal,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=3
        )

        # Centered Executive Header
        story.append(Paragraph(escape_xml(name.upper()), name_style))
        story.append(Paragraph(escape_xml(title), title_style))
        story.append(Spacer(1, 3))
        story.append(Paragraph(escape_xml(contact_str), contact_style))
        story.append(Spacer(1, 5))
        story.append(HRFlowable(width="100%", thickness=2, color=slate_color, spaceAfter=8))

        if summary:
            story.append(Paragraph("EXECUTIVE PROFILE", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#94A3B8"), spaceAfter=5))
            story.append(Paragraph(escape_xml(summary), body_style))
            story.append(Spacer(1, 6))

        if skills:
            story.append(Paragraph("CORE COMPETENCIES & TECHNICAL PROFICIENCIES", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#94A3B8"), spaceAfter=5))
            if isinstance(skills, list):
                skills_text = " • ".join(skills)
            elif isinstance(skills, dict):
                skills_text = " | ".join([f"<b>{k.replace('_', ' ').title()}:</b> {', '.join(v)}" for k, v in skills.items() if v])
            else:
                skills_text = str(skills)
            story.append(Paragraph(escape_xml(skills_text), body_style))
            story.append(Spacer(1, 6))

        if experience:
            story.append(Paragraph("PROFESSIONAL WORK HISTORY", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#94A3B8"), spaceAfter=5))
            if isinstance(experience, list):
                for item in experience:
                    story.append(Paragraph(f"• {escape_xml(item)}", bullet_style))
            else:
                for line in str(experience).split("\n"):
                    if line.strip():
                        story.append(Paragraph(f"• {escape_xml(line.strip())}", bullet_style))
            story.append(Spacer(1, 6))

        if projects:
            story.append(Paragraph("KEY INITIATIVES & DELIVERABLES", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#94A3B8"), spaceAfter=5))
            if isinstance(projects, list):
                for item in projects:
                    story.append(Paragraph(f"• {escape_xml(item)}", bullet_style))
            else:
                for line in str(projects).split("\n"):
                    if line.strip():
                        story.append(Paragraph(f"• {escape_xml(line.strip())}", bullet_style))
            story.append(Spacer(1, 6))

        if education:
            story.append(Paragraph("EDUCATION & CREDENTIALS", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#94A3B8"), spaceAfter=5))
            if isinstance(education, list):
                for item in education:
                    story.append(Paragraph(f"• {escape_xml(item)}", bullet_style))
            else:
                story.append(Paragraph(escape_xml(str(education)), body_style))
            story.append(Spacer(1, 6))

        if certifications:
            story.append(Paragraph("CERTIFICATIONS", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#94A3B8"), spaceAfter=5))
            if isinstance(certifications, list):
                for item in certifications:
                    story.append(Paragraph(f"• {escape_xml(item)}", bullet_style))
            else:
                story.append(Paragraph(escape_xml(str(certifications)), body_style))

    # -------------------------------------------------------------
    # TEMPLATE 3: MINIMALIST TECH
    # -------------------------------------------------------------
    else:  # minimalist_tech
        tech_black = colors.HexColor("#111827")
        gray_muted = colors.HexColor("#6B7280")
        line_gray = colors.HexColor("#D1D5DB")

        name_style = ParagraphStyle(
            'TechName',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=21,
            leading=25,
            textColor=tech_black
        )
        title_style = ParagraphStyle(
            'TechTitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=gray_muted
        )
        contact_style = ParagraphStyle(
            'TechContact',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12,
            textColor=gray_muted
        )
        sec_style = ParagraphStyle(
            'TechSecHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=14,
            textColor=tech_black,
            spaceAfter=4,
            spaceBefore=10
        )
        body_style = ParagraphStyle(
            'TechBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=tech_black,
            alignment=4
        )
        bullet_style = ParagraphStyle(
            'TechBullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=tech_black,
            leftIndent=14,
            firstLineIndent=-10,
            spaceAfter=2.5
        )

        story.append(Paragraph(escape_xml(name), name_style))
        story.append(Paragraph(escape_xml(title), title_style))
        story.append(Spacer(1, 2))
        story.append(Paragraph(escape_xml(contact_str), contact_style))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1, color=tech_black, spaceAfter=8))

        if summary:
            story.append(Paragraph("SUMMARY", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=line_gray, spaceAfter=4))
            story.append(Paragraph(escape_xml(summary), body_style))
            story.append(Spacer(1, 6))

        if skills:
            story.append(Paragraph("SKILLS & TECHNOLOGIES", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=line_gray, spaceAfter=4))
            if isinstance(skills, list):
                skills_text = " • ".join(skills)
            elif isinstance(skills, dict):
                skills_text = " | ".join([f"<b>{k.replace('_', ' ').title()}:</b> {', '.join(v)}" for k, v in skills.items() if v])
            else:
                skills_text = str(skills)
            story.append(Paragraph(escape_xml(skills_text), body_style))
            story.append(Spacer(1, 6))

        if experience:
            story.append(Paragraph("EXPERIENCE", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=line_gray, spaceAfter=4))
            if isinstance(experience, list):
                for item in experience:
                    story.append(Paragraph(f"• {escape_xml(item)}", bullet_style))
            else:
                for line in str(experience).split("\n"):
                    if line.strip():
                        story.append(Paragraph(f"• {escape_xml(line.strip())}", bullet_style))
            story.append(Spacer(1, 6))

        if projects:
            story.append(Paragraph("PROJECTS", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=line_gray, spaceAfter=4))
            if isinstance(projects, list):
                for item in projects:
                    story.append(Paragraph(f"• {escape_xml(item)}", bullet_style))
            else:
                for line in str(projects).split("\n"):
                    if line.strip():
                        story.append(Paragraph(f"• {escape_xml(line.strip())}", bullet_style))
            story.append(Spacer(1, 6))

        if education:
            story.append(Paragraph("EDUCATION", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=line_gray, spaceAfter=4))
            if isinstance(education, list):
                for item in education:
                    story.append(Paragraph(f"• {escape_xml(item)}", bullet_style))
            else:
                story.append(Paragraph(escape_xml(str(education)), body_style))
            story.append(Spacer(1, 6))

        if certifications:
            story.append(Paragraph("CERTIFICATIONS", sec_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=line_gray, spaceAfter=4))
            if isinstance(certifications, list):
                for item in certifications:
                    story.append(Paragraph(f"• {escape_xml(item)}", bullet_style))
            else:
                story.append(Paragraph(escape_xml(str(certifications)), body_style))

    # Build the PDF document
    doc.build(story)
    return file_path, output_filename
