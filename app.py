import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename

from config import Config
from database import (
    init_db, save_resume, get_resume, get_all_resumes, update_resume_parsed_data,
    save_analysis, get_analysis, get_all_analyses, delete_analysis, clear_all_analyses,
    save_enhancement, get_enhancements_by_resume, get_dashboard_stats
)
from resume_parser import parse_resume, extract_skills_from_text
from ats_analyzer import analyze_ats
from job_matcher import compare_resume_with_job
from ai_enhancer import (
    enhance_summary_ai, enhance_experience_ai, enhance_projects_ai,
    full_resume_enhancement, get_genai_client
)
from pdf_generator import generate_resume_pdf


app = Flask(__name__)
app.config.from_object(Config)

# Initialize database schema on startup
with app.app_context():
    init_db()


def allowed_file(filename):
    """Check if uploaded file has an allowed extension (.pdf or .docx)."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@app.context_processor
def inject_global_data():
    """Inject configuration flags and global variables into all Jinja2 templates."""
    has_api_key = bool(Config.GEMINI_API_KEY)
    ai_status = "Gemini AI Active" if has_api_key else "Intelligent Rule-Based Mode"
    return {
        "app_name": Config.APP_NAME,
        "app_version": Config.VERSION,
        "gemini_active": has_api_key,
        "ai_status_label": ai_status,
        "gemini_model": Config.GEMINI_MODEL
    }


# -------------------------------------------------------------
# 1. LANDING & DASHBOARD ROUTES
# -------------------------------------------------------------

@app.route("/")
def index():
    """Home / Landing page."""
    return render_template("index.html", active_page="home")


@app.route("/dashboard")
def dashboard():
    """Main dashboard displaying analytics, recent analyses, and quick tools."""
    stats = get_dashboard_stats()
    recent_resumes = get_all_resumes(limit=5)
    recent_analyses = get_all_analyses(limit=5)
    return render_template(
        "dashboard.html",
        active_page="dashboard",
        stats=stats,
        recent_resumes=recent_resumes,
        recent_analyses=recent_analyses
    )


# -------------------------------------------------------------
# 2. RESUME UPLOAD ROUTES
# -------------------------------------------------------------

@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Handle resume upload (PDF or DOCX), text extraction, and storage."""
    if request.method == "POST":
        if "resume_file" not in request.files:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "error": "No file part in the request."}), 400
            flash("No file selected.", "danger")
            return redirect(request.url)

        file = request.files["resume_file"]
        if file.filename == "":
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "error": "No file selected for upload."}), 400
            flash("No file selected.", "danger")
            return redirect(request.url)

        if not allowed_file(file.filename):
            error_msg = "Invalid file type. Only .PDF and .DOCX files are supported."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "error": error_msg}), 400
            flash(error_msg, "danger")
            return redirect(request.url)

        try:
            orig_filename = secure_filename(file.filename)
            ext = orig_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"resume_{os.urandom(6).hex()}.{ext}"
            saved_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
            file.save(saved_path)

            file_size = os.path.getsize(saved_path)

            # Parse resume text and structure
            raw_text, parsed_data = parse_resume(saved_path)

            if not raw_text.strip():
                if os.path.exists(saved_path):
                    os.remove(saved_path)
                error_msg = "The uploaded document contains no readable text. Scanned image-only PDFs are not supported."
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return jsonify({"success": False, "error": error_msg}), 400
                flash(error_msg, "warning")
                return redirect(request.url)

            # Save record in SQLite
            resume_id = save_resume(
                filename=unique_filename,
                original_filename=orig_filename,
                file_type=ext,
                file_size=file_size,
                raw_text=raw_text,
                parsed_data=parsed_data
            )

            # Compute initial ATS score and save analysis record
            ats_result = analyze_ats(parsed_data, raw_text)
            save_analysis(
                resume_id=resume_id,
                ats_score=ats_result["overall_score"],
                improved_score=ats_result["improved_score"],
                section_scores=ats_result["sections_breakdown"],
                suggestions=ats_result["suggestions"]
            )

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({
                    "success": True,
                    "resume_id": resume_id,
                    "redirect_url": url_for("analysis", resume_id=resume_id)
                })

            flash(f"Resume '{orig_filename}' uploaded and parsed successfully!", "success")
            return redirect(url_for("analysis", resume_id=resume_id))

        except Exception as e:
            error_msg = f"Error processing resume: {str(e)}"
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "error": error_msg}), 500
            flash(error_msg, "danger")
            return redirect(request.url)

    # GET request
    recent_resumes = get_all_resumes(limit=8)
    return render_template("upload.html", active_page="upload", recent_resumes=recent_resumes)


# -------------------------------------------------------------
# 3. ATS RESUME ANALYSIS ROUTE
# -------------------------------------------------------------

@app.route("/analysis")
@app.route("/analysis/<int:resume_id>")
def analysis(resume_id=None):
    """Display in-depth ATS compatibility analysis, circular score gauge, and breakdown."""
    all_resumes = get_all_resumes()
    
    if not resume_id:
        if all_resumes:
            return redirect(url_for("analysis", resume_id=all_resumes[0]["id"]))
        else:
            flash("Please upload a resume first to view ATS analysis.", "info")
            return redirect(url_for("upload"))

    resume = get_resume(resume_id)
    if not resume:
        flash("Resume record not found.", "warning")
        return redirect(url_for("upload"))

    parsed_data = resume.get("parsed_data", {})
    raw_text = resume.get("raw_text", "")
    ats_result = analyze_ats(parsed_data, raw_text)

    return render_template(
        "analysis.html",
        active_page="analysis",
        resume=resume,
        all_resumes=all_resumes,
        ats=ats_result
    )


# -------------------------------------------------------------
# 4. JOB DESCRIPTION MATCHING ROUTE
# -------------------------------------------------------------

@app.route("/job-match", methods=["GET", "POST"])
@app.route("/job-match/<int:resume_id>", methods=["GET", "POST"])
def job_match(resume_id=None):
    """Compare resume against a target job description to identify matched & missing keywords."""
    all_resumes = get_all_resumes()
    
    if not resume_id:
        if all_resumes:
            return redirect(url_for("job_match", resume_id=all_resumes[0]["id"]))
        else:
            flash("Please upload a resume first before matching against job descriptions.", "info")
            return redirect(url_for("upload"))

    resume = get_resume(resume_id)
    if not resume:
        flash("Resume record not found.", "warning")
        return redirect(url_for("upload"))

    match_result = None
    target_role = ""
    job_desc = ""

    if request.method == "POST":
        target_role = request.form.get("target_role", "").strip()
        job_desc = request.form.get("job_description", "").strip()

        if not job_desc:
            flash("Please enter or paste a job description.", "warning")
        else:
            parsed_data = resume.get("parsed_data", {})
            raw_text = resume.get("raw_text", "")
            match_result = compare_resume_with_job(parsed_data, raw_text, job_desc)

            # Also update/save to SQLite analysis history
            ats_result = analyze_ats(parsed_data, raw_text)
            save_analysis(
                resume_id=resume_id,
                ats_score=ats_result["overall_score"],
                improved_score=ats_result["improved_score"],
                match_percentage=match_result["match_percentage"],
                target_role=target_role,
                job_description=job_desc,
                matched_keywords=match_result["matched_keywords"],
                missing_keywords=match_result["missing_keywords"],
                suggestions=[r.get("advice") for r in match_result["recommendations"]]
            )
            flash("Job matching completed successfully!", "success")

    return render_template(
        "job_match.html",
        active_page="job_match",
        resume=resume,
        all_resumes=all_resumes,
        match=match_result,
        target_role=target_role,
        job_desc=job_desc
    )


# -------------------------------------------------------------
# 5. AI RESUME ENHANCER ROUTE
# -------------------------------------------------------------

@app.route("/enhance", methods=["GET", "POST"])
@app.route("/enhance/<int:resume_id>", methods=["GET", "POST"])
def enhance(resume_id=None):
    """AI-powered resume rewrite: Summary, Experience, and Projects with before/after comparison."""
    all_resumes = get_all_resumes()
    
    if not resume_id:
        if all_resumes:
            return redirect(url_for("enhance", resume_id=all_resumes[0]["id"]))
        else:
            flash("Please upload a resume first to use the AI Enhancer.", "info")
            return redirect(url_for("upload"))

    resume = get_resume(resume_id)
    if not resume:
        flash("Resume record not found.", "warning")
        return redirect(url_for("upload"))

    parsed_data = resume.get("parsed_data", {})
    raw_text = resume.get("raw_text", "")
    initial_ats = analyze_ats(parsed_data, raw_text)

    enhancement_result = None
    target_role = request.form.get("target_role", "Software Engineer").strip()
    job_desc = request.form.get("job_description", "").strip()

    if request.method == "POST":
        enhancement_result = full_resume_enhancement(parsed_data, target_role, job_desc)
        
        # Save enhancement record to SQLite
        save_enhancement(
            resume_id=resume_id,
            section_type="full",
            original_text=parsed_data.get("summary", ""),
            enhanced_text=enhancement_result["summary"].get("enhanced_text", ""),
            improvements=enhancement_result["summary"].get("notes", [])
        )
        flash("Resume enhancement generated successfully!", "success")

    return render_template(
        "enhancement.html",
        active_page="enhance",
        resume=resume,
        all_resumes=all_resumes,
        enhancement=enhancement_result,
        initial_ats=initial_ats,
        target_role=target_role,
        job_desc=job_desc
    )


# -------------------------------------------------------------
# 6. RESUME BUILDER & PDF GENERATION
# -------------------------------------------------------------

@app.route("/builder", methods=["GET", "POST"])
@app.route("/builder/<int:resume_id>", methods=["GET", "POST"])
def builder(resume_id=None):
    """Resume builder: interactive editing, 3 templates, live preview, and PDF export."""
    all_resumes = get_all_resumes()
    
    if not resume_id:
        if all_resumes:
            return redirect(url_for("builder", resume_id=all_resumes[0]["id"]))
        else:
            flash("Please upload a resume first to edit and build.", "info")
            return redirect(url_for("upload"))

    resume = get_resume(resume_id)
    if not resume:
        flash("Resume record not found.", "warning")
        return redirect(url_for("upload"))

    parsed_data = resume.get("parsed_data", {})
    template_choice = request.args.get("template", "modern_blue")

    if request.method == "POST":
        # Save updated resume fields back to SQLite
        updated_contact = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "linkedin": request.form.get("linkedin", "").strip(),
            "github": request.form.get("github", "").strip(),
            "portfolio": request.form.get("portfolio", "").strip()
        }
        
        skills_raw = request.form.get("skills", "").strip()
        skills_list = [s.strip() for s in skills_raw.split(",") if s.strip()]

        parsed_data["contact"] = updated_contact
        parsed_data["summary"] = request.form.get("summary", "").strip()
        parsed_data["all_skills"] = skills_list
        parsed_data["experience"] = request.form.get("experience", "").strip()
        parsed_data["projects"] = request.form.get("projects", "").strip()
        parsed_data["education"] = request.form.get("education", "").strip()
        parsed_data["certifications"] = request.form.get("certifications", "").strip()

        update_resume_parsed_data(resume_id, parsed_data)
        flash("Resume changes saved successfully!", "success")
        return redirect(url_for("builder", resume_id=resume_id, template=template_choice))

    return render_template(
        "builder.html",
        active_page="builder",
        resume=resume,
        all_resumes=all_resumes,
        parsed=parsed_data,
        selected_template=template_choice
    )


@app.route("/download-pdf/<int:resume_id>")
@app.route("/download-pdf/<int:resume_id>/<template_name>")
def download_pdf(resume_id, template_name="modern_blue"):
    """Generate and deliver downloadable PDF resume."""
    resume = get_resume(resume_id)
    if not resume:
        flash("Resume not found.", "danger")
        return redirect(url_for("dashboard"))

    parsed = resume.get("parsed_data", {})
    candidate_name = parsed.get("contact", {}).get("name", "Candidate")
    safe_name = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '_', '-')).strip() or "Resume"
    download_filename = f"{safe_name.replace(' ', '_')}_{template_name}.pdf"

    # Assemble structured payload for PDF engine
    resume_payload = {
        "contact": parsed.get("contact", {}),
        "title": parsed.get("target_role") or "Software Engineering Professional",
        "summary": parsed.get("summary", ""),
        "skills": parsed.get("all_skills", []),
        "experience": parsed.get("experience_bullets") or parsed.get("experience", ""),
        "projects": parsed.get("project_bullets") or parsed.get("projects", ""),
        "education": parsed.get("education", ""),
        "certifications": parsed.get("certifications", "")
    }

    try:
        pdf_path, _ = generate_resume_pdf(resume_payload, template_name=template_name, output_filename=download_filename)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype="application/pdf"
        )
    except Exception as e:
        flash(f"Error generating PDF: {str(e)}", "danger")
        return redirect(url_for("builder", resume_id=resume_id))


# -------------------------------------------------------------
# 7. ANALYSIS HISTORY ROUTES
# -------------------------------------------------------------

@app.route("/history")
def history():
    """Display previous resume analyses, scores, and timestamps stored in SQLite."""
    analyses_list = get_all_analyses(limit=50)
    return render_template("history.html", active_page="history", analyses=analyses_list)


@app.route("/history/delete/<int:analysis_id>", methods=["POST"])
def delete_history_item(analysis_id):
    """Delete a single analysis history record."""
    delete_analysis(analysis_id)
    flash("Analysis record deleted successfully.", "info")
    return redirect(url_for("history"))


@app.route("/history/clear", methods=["POST"])
def clear_all_history():
    """Clear all analysis history records."""
    clear_all_analyses()
    flash("All analysis history has been cleared.", "info")
    return redirect(url_for("history"))


# -------------------------------------------------------------
# 8. ABOUT PROJECT ROUTE
# -------------------------------------------------------------

@app.route("/about")
def about():
    """Display comprehensive project architecture, ATS scoring methodology, and features."""
    return render_template("about.html", active_page="about")


# -------------------------------------------------------------
# 9. ASYNC API ENDPOINTS (For instant UI interactions)
# -------------------------------------------------------------

@app.route("/api/enhance-section", methods=["POST"])
def api_enhance_section():
    """AJAX endpoint to enhance a specific section (summary, experience, projects)."""
    data = request.get_json() or {}
    section_type = data.get("section_type", "summary")
    content = data.get("content", "")
    target_role = data.get("target_role", "Software Engineer")
    job_desc = data.get("job_description", "")
    skills = data.get("skills", [])

    if section_type == "summary":
        res = enhance_summary_ai(content, target_role, skills, job_desc)
    elif section_type == "experience":
        res = enhance_experience_ai(content, target_role, job_desc)
    elif section_type == "projects":
        res = enhance_projects_ai(content, skills)
    else:
        return jsonify({"success": False, "error": "Invalid section type"}), 400

    return jsonify({"success": True, "result": res})


@app.route("/health")
def health():
    """Health check probe for Vercel, Render, and Docker."""
    return jsonify({
        "status": "healthy",
        "service": Config.APP_NAME,
        "version": Config.VERSION
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
