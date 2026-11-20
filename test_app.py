import os
import sys
import unittest

# Ensure AI-Resume-Enhancer directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import Config
from database import init_db, get_db_connection, get_all_resumes, get_resume, get_all_analyses
from resume_parser import parse_resume, extract_contact_info, extract_skills_from_text
from ats_analyzer import analyze_ats
from job_matcher import compare_resume_with_job
from ai_enhancer import rule_based_enhance_summary, rule_based_enhance_experience, full_resume_enhancement
from pdf_generator import generate_resume_pdf
from app import app


class TestAIResumeEnhancer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()
        cls.pdf_sample = os.path.join(BASE_DIR, "uploads", "sample_resume.pdf")
        cls.docx_sample = os.path.join(BASE_DIR, "uploads", "sample_resume.docx")

    def test_01_parse_pdf_resume(self):
        self.assertTrue(os.path.exists(self.pdf_sample), "Sample PDF must exist")
        raw_text, parsed = parse_resume(self.pdf_sample)
        self.assertTrue(len(raw_text) > 100, "Extracted PDF text should not be empty")
        self.assertIn("Alex Morgan", parsed["contact"]["name"])
        self.assertIn("alex.morgan@email.com", parsed["contact"]["email"])
        self.assertTrue(len(parsed["all_skills"]) >= 5, "Should detect multiple technical skills")
        print("✓ PDF parsing passed successfully.")

    def test_02_parse_docx_resume(self):
        self.assertTrue(os.path.exists(self.docx_sample), "Sample DOCX must exist")
        raw_text, parsed = parse_resume(self.docx_sample)
        self.assertTrue(len(raw_text) > 100, "Extracted DOCX text should not be empty")
        self.assertIn("alex.morgan@email.com", parsed["contact"]["email"])
        print("✓ DOCX parsing passed successfully.")

    def test_03_ats_analyzer(self):
        raw_text, parsed = parse_resume(self.pdf_sample)
        ats_result = analyze_ats(parsed, raw_text)
        self.assertIn("overall_score", ats_result)
        self.assertTrue(0 <= ats_result["overall_score"] <= 100)
        self.assertTrue(ats_result["improved_score"] >= ats_result["overall_score"])
        self.assertEqual(len(ats_result["sections_breakdown"]), 5)
        self.assertTrue(len(ats_result["strengths"]) > 0)
        self.assertIn("disclaimer", ats_result)
        print(f"✓ ATS Analysis passed. Calculated score: {ats_result['overall_score']}/100")

    def test_04_job_matcher(self):
        raw_text, parsed = parse_resume(self.pdf_sample)
        sample_jd = """
        We are seeking a Senior Backend Engineer proficient in Python, Flask, Docker, Kubernetes,
        and PostgreSQL. Nice to have experience with AWS, CI/CD, Redis, and GraphQL.
        Must have 3+ years of experience with REST APIs and Agile development.
        """
        match = compare_resume_with_job(parsed, raw_text, sample_jd)
        self.assertIn("match_percentage", match)
        self.assertTrue(match["match_percentage"] > 40)
        self.assertTrue(len(match["matched_keywords"]) > 0)
        self.assertIn("Python", match["matched_keywords"])
        print(f"✓ Job Matching passed. Match percentage: {match['match_percentage']}%")

    def test_05_rule_based_enhancer(self):
        raw_text, parsed = parse_resume(self.pdf_sample)
        enhanced = full_resume_enhancement(parsed, target_role="Senior Full-Stack Engineer")
        self.assertTrue(len(enhanced["summary"]["enhanced_text"]) > 20)
        self.assertTrue(len(enhanced["experience"]["bullets"]) > 0)
        print("✓ AI & Rule-based Enhancement passed.")

    def test_06_pdf_generator_all_templates(self):
        raw_text, parsed = parse_resume(self.pdf_sample)
        sample_payload = {
            "contact": parsed["contact"],
            "title": "Senior Software Engineer",
            "summary": parsed["summary"],
            "skills": parsed["all_skills"],
            "experience": parsed["experience_bullets"],
            "projects": parsed["project_bullets"],
            "education": parsed["education"],
            "certifications": parsed["certifications"]
        }

        templates = ["modern_blue", "executive_slate", "minimalist_tech"]
        for tmpl in templates:
            out_file = f"test_{tmpl}.pdf"
            file_path, fname = generate_resume_pdf(sample_payload, template_name=tmpl, output_filename=out_file)
            self.assertTrue(os.path.exists(file_path))
            with open(file_path, "rb") as f:
                header = f.read(5)
                self.assertEqual(header, b"%PDF-")
            print(f"✓ PDF generation for template '{tmpl}' verified.")

    def test_07_flask_routes(self):
        # 1. Landing
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

        # 2. Dashboard
        resp = self.client.get("/dashboard")
        self.assertEqual(resp.status_code, 200)

        # 3. Upload GET
        resp = self.client.get("/upload")
        self.assertEqual(resp.status_code, 200)

        # 4. Upload POST
        with open(self.pdf_sample, "rb") as f:
            resp = self.client.post(
                "/upload",
                data={"resume_file": (f, "sample_resume.pdf")},
                content_type="multipart/form-data",
                follow_redirects=True
            )
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"ATS Compatibility Analysis", resp.data)

        # Get latest resume ID from DB
        resumes = get_all_resumes()
        self.assertTrue(len(resumes) > 0)
        test_id = resumes[0]["id"]

        # 5. Analysis page
        resp = self.client.get(f"/analysis/{test_id}")
        self.assertEqual(resp.status_code, 200)

        # 6. Job match GET & POST
        resp = self.client.get(f"/job-match/{test_id}")
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(
            f"/job-match/{test_id}",
            data={
                "target_role": "Python Backend Engineer",
                "job_description": "Looking for Python, Flask, Docker, and PostgreSQL developer."
            },
            follow_redirects=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Matched Keywords", resp.data)

        # 7. Enhance GET & POST
        resp = self.client.get(f"/enhance/{test_id}")
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(
            f"/enhance/{test_id}",
            data={"target_role": "Backend Architect"},
            follow_redirects=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Professional Summary Enhancement", resp.data)

        # 8. Builder GET & PDF download
        resp = self.client.get(f"/builder/{test_id}?template=modern_blue")
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f"/download-pdf/{test_id}/modern_blue")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["Content-Type"], "application/pdf")

        resp = self.client.get(f"/download-pdf/{test_id}/executive_slate")
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f"/download-pdf/{test_id}/minimalist_tech")
        self.assertEqual(resp.status_code, 200)

        # 9. History GET
        resp = self.client.get("/history")
        self.assertEqual(resp.status_code, 200)

        # 10. About GET
        resp = self.client.get("/about")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"About AI Resume Enhancer", resp.data)

        print("✓ All 10 Flask routes tested successfully with status code 200!")


if __name__ == "__main__":
    unittest.main()
