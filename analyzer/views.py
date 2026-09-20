from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from PyPDF2 import PdfReader
from PIL import Image, ImageOps
import pytesseract
import re

from .models import ResumeAnalysis


# =========================================================
# TESSERACT OCR
# =========================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================================================
# FIELD-SPECIFIC SKILLS
# =========================================================

FIELD_SKILLS = {

    "BCA / Computer Science": [
        "Python",
        "Java",
        "C",
        "C++",
        "JavaScript",
        "HTML",
        "CSS",
        "Django",
        "React",
        "SQL",
        "MySQL",
        "PostgreSQL",
        "Git",
        "GitHub",
        "REST API",
        "Machine Learning",
        "Data Science",
    ],

    "BBA / Business Administration": [
        "Marketing",
        "Sales",
        "Business Analysis",
        "Business Development",
        "Communication",
        "Leadership",
        "Management",
        "Teamwork",
        "Team Collaboration",
        "MS Excel",
        "Microsoft Excel",
        "Digital Marketing",
        "Market Research",
        "Customer Service",
        "Customer Relationship",
        "Financial Analysis",
        "Project Management",
        "Operations",
        "Reporting",
        "Coordination",
        "Problem Solving",
        "Time Management",
    ],

    "B.Com / Commerce": [
        "Accounting",
        "Tally",
        "GST",
        "Taxation",
        "Auditing",
        "MS Excel",
        "Microsoft Excel",
        "Financial Analysis",
        "Bookkeeping",
        "SAP",
        "Payroll",
        "Bank Reconciliation",
        "Budgeting",
        "Microsoft Office",
        "Commerce",
        "Accounts Payable",
        "Accounts Receivable",
    ],

    "B.Tech / Engineering": [
        "Python",
        "Java",
        "C",
        "C++",
        "JavaScript",
        "SQL",
        "HTML",
        "CSS",
        "Git",
        "GitHub",
        "Machine Learning",
        "Data Science",
        "Engineering",
        "Problem Solving",
        "AutoCAD",
        "MATLAB",
        "Project Management",
    ],

    "MBA / Management": [
        "Management",
        "Leadership",
        "Marketing",
        "Sales",
        "Business Analysis",
        "Business Development",
        "Finance",
        "Human Resources",
        "Communication",
        "Project Management",
        "MS Excel",
        "Microsoft Excel",
        "Digital Marketing",
        "Market Research",
        "Strategic Planning",
        "Operations",
        "Customer Service",
    ],

    "Finance & Accounting": [
        "Accounting",
        "Financial Analysis",
        "Financial Planning",
        "Taxation",
        "GST",
        "Auditing",
        "Tally",
        "MS Excel",
        "Microsoft Excel",
        "SAP",
        "Bookkeeping",
        "Budgeting",
        "Payroll",
        "Investment",
        "Banking",
        "Risk Management",
    ],

    "Marketing": [
        "Digital Marketing",
        "Marketing",
        "SEO",
        "Social Media Marketing",
        "Content Marketing",
        "Market Research",
        "Brand Management",
        "Google Ads",
        "Communication",
        "Sales",
        "Customer Relationship",
        "Advertising",
        "Email Marketing",
        "Analytics",
    ],

    "Human Resources": [
        "Human Resources",
        "Recruitment",
        "Talent Acquisition",
        "Employee Relations",
        "Communication",
        "Leadership",
        "Training",
        "Payroll",
        "Performance Management",
        "HR Management",
        "Interviewing",
        "Teamwork",
        "Conflict Resolution",
    ],

    "Design": [
        "Graphic Design",
        "UI Design",
        "UX Design",
        "Figma",
        "Adobe Photoshop",
        "Adobe Illustrator",
        "Canva",
        "Adobe XD",
        "Typography",
        "Branding",
        "Wireframing",
        "Prototyping",
        "Visual Design",
        "Creativity",
    ],

    "Arts & Humanities": [
        "Communication",
        "Writing",
        "Research",
        "Public Speaking",
        "Content Writing",
        "Creative Writing",
        "Teamwork",
        "Leadership",
        "Presentation",
        "Social Media",
        "Event Management",
        "Critical Thinking",
    ],

    "Science": [
        "Research",
        "Data Analysis",
        "Statistics",
        "Laboratory",
        "Microsoft Excel",
        "Scientific Research",
        "Communication",
        "Problem Solving",
        "Python",
        "SQL",
        "Data Science",
        "Documentation",
    ],

    "Other": [
        "Communication",
        "Leadership",
        "Teamwork",
        "Problem Solving",
        "Time Management",
        "MS Excel",
        "Microsoft Excel",
        "Microsoft Office",
        "Research",
        "Presentation",
        "Project Management",
    ],
}


# =========================================================
# GET SKILLS FOR SELECTED FIELD
# =========================================================

def get_skills_for_field(field):
    return FIELD_SKILLS.get(
        field,
        FIELD_SKILLS["Other"]
    )


# =========================================================
# CHECK SKILL
# =========================================================

def skill_exists(text, skill):
    pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"
    return re.search(pattern, text.lower()) is not None


# =========================================================
# ANALYZE RESUME
# =========================================================

def analyze_resume(text, field):

    text_lower = text.lower()

    skills_list = get_skills_for_field(field)

    found_skills = []

    # -----------------------------------------------------
    # DETECT SKILLS
    # -----------------------------------------------------

    for skill in skills_list:

        if skill_exists(text, skill):
            found_skills.append(skill)

    # Remove duplicates
    found_skills = list(dict.fromkeys(found_skills))

    # -----------------------------------------------------
    # SKILL SCORE
    # -----------------------------------------------------

    skill_score = min(
        len(found_skills) * 3,
        25
    )

    # -----------------------------------------------------
    # RESUME SECTIONS
    # -----------------------------------------------------

    sections = {

        "Education": [
            "education",
            "academic",
            "degree",
            "bachelor",
            "master",
            "bca",
            "bba",
            "b.com",
            "bcom",
            "b.tech",
            "puc",
            "sslc",
        ],

        "Experience": [
            "experience",
            "work experience",
            "employment",
            "internship",
            "worked",
        ],

        "Projects": [
            "projects",
            "project",
        ],

        "Achievements": [
            "achievement",
            "achievements",
            "award",
            "awards",
            "certification",
            "certifications",
        ],
    }

    found_sections = []

    section_score = 0

    for section, keywords in sections.items():

        if any(
            keyword in text_lower
            for keyword in keywords
        ):

            found_sections.append(section)

            section_score += 10

    # -----------------------------------------------------
    # CONTACT DETECTION
    # -----------------------------------------------------

    email_pattern = (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    phone_pattern = (
        r"(?<!\d)"
        r"(?:\+91[\s-]?)?"
        r"[6-9]\d{9}"
        r"(?!\d)"
    )

    email_found = re.search(
        email_pattern,
        text
    )

    phone_found = re.search(
        phone_pattern,
        text
    )

    linkedin_found = (
        "linkedin.com" in text_lower
        or "linkedin" in text_lower
    )

    contact_found = (
        email_found
        or phone_found
        or linkedin_found
        or "contact" in text_lower
        or "gmail" in text_lower
        or "phone" in text_lower
        or "mobile" in text_lower
        or "ph no" in text_lower
    )

    if contact_found:

        found_sections.append("Contact")

        section_score += 10

    # -----------------------------------------------------
    # FINAL SCORE
    # -----------------------------------------------------

    total_score = min(
        skill_score + section_score + 15,
        100
    )

    # -----------------------------------------------------
    # SUGGESTIONS
    # -----------------------------------------------------

    suggestions = []

    # Education
    if "Education" not in found_sections:

        suggestions.append(
            "Add a clear Education section with your "
            "degree, college and graduation year."
        )

    # Experience
    if "Experience" not in found_sections:

        suggestions.append(
            "Add internship, work experience or relevant "
            "volunteer experience if available."
        )

    # Projects
    if "Projects" not in found_sections:

        suggestions.append(
            "Add academic or personal projects to "
            "demonstrate your practical abilities."
        )

    # Achievements
    if "Achievements" not in found_sections:

        suggestions.append(
            "Add certifications, awards, achievements or "
            "extracurricular activities if applicable."
        )

    # Contact
    if not email_found:

        suggestions.append(
            "Add a professional email address."
        )

    if not phone_found:

        suggestions.append(
            "Add a phone number so recruiters can contact you."
        )

    if not linkedin_found:

        suggestions.append(
            "Consider adding your LinkedIn profile."
        )

    # Skills
    if len(found_skills) < 5:

        suggestions.append(
            "Add more relevant skills related to your field."
        )

    # Experience-specific suggestion
    if "Experience" in found_sections:

        suggestions.append(
            "Add measurable achievements to your work "
            "experience, such as numbers, percentages "
            "or results where accurate."
        )

    if not suggestions:

        suggestions.append(
            "Your resume contains the major sections. "
            "Keep improving it with measurable achievements."
        )

    return (
        found_skills,
        found_sections,
        total_score,
        suggestions
    )


# =========================================================
# JOB MATCHING
# =========================================================

def match_job(
    resume_text,
    job_description,
    field
):

    skills_list = get_skills_for_field(field)

    matched_skills = []

    missing_skills = []

    for skill in skills_list:

        if skill_exists(job_description, skill):

            if skill_exists(resume_text, skill):

                matched_skills.append(skill)

            else:

                missing_skills.append(skill)

    total_required = (
        len(matched_skills)
        + len(missing_skills)
    )

    if total_required > 0:

        match_score = int(
            (
                len(matched_skills)
                / total_required
            ) * 100
        )

    else:

        match_score = None

    return (
        matched_skills,
        missing_skills,
        match_score
    )


# =========================================================
# EXTRACT TEXT FROM PDF OR IMAGE
# =========================================================

def extract_text_from_resume(resume):

    file_name = resume.name.lower()

    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    if file_name.endswith(".pdf"):

        reader = PdfReader(resume)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

        return text

    # -----------------------------------------------------
    # IMAGE
    # -----------------------------------------------------

    if file_name.endswith(
        (".jpg", ".jpeg", ".png")
    ):

        image = Image.open(resume)

        # Correct rotated phone images
        image = ImageOps.exif_transpose(image)

        text = pytesseract.image_to_string(
            image
        )

        return text

    return None


# =========================================================
# HOME
# =========================================================

@login_required
def home(request):

    error = ""

    if request.method == "POST":

        resume = request.FILES.get("resume")

        field = request.POST.get(
            "field",
            ""
        )

        job_description = request.POST.get(
            "job_description",
            ""
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not field:

            error = "Please select your field."

        elif not resume:

            error = "Please select a resume."

        else:

            allowed_files = (
                ".pdf",
                ".jpg",
                ".jpeg",
                ".png"
            )

            if not resume.name.lower().endswith(
                allowed_files
            ):

                error = (
                    "Supported formats are "
                    "PDF, JPG, JPEG and PNG."
                )

            else:

                try:

                    # -------------------------------------
                    # EXTRACT TEXT
                    # -------------------------------------

                    text = extract_text_from_resume(
                        resume
                    )

                    if not text or not text.strip():

                        error = (
                            "Could not extract text from "
                            "this file. Please upload a "
                            "clear resume."
                        )

                    else:

                        # ---------------------------------
                        # ANALYZE
                        # ---------------------------------

                        (
                            skills,
                            sections,
                            score,
                            suggestions
                        ) = analyze_resume(
                            text,
                            field
                        )

                        # ---------------------------------
                        # JOB MATCHING
                        # ---------------------------------

                        matched_skills = []

                        missing_skills = []

                        match_score = None

                        if job_description.strip():

                            (
                                matched_skills,
                                missing_skills,
                                match_score
                            ) = match_job(
                                text,
                                job_description,
                                field
                            )

                        # ---------------------------------
                        # SAVE DATABASE
                        # ---------------------------------

                        analysis = ResumeAnalysis.objects.create(

                            user=request.user,

                            resume_name=resume.name,

                            field=field,

                            score=score,

                            match_score=match_score,

                            skills=", ".join(skills)

)

                        # ---------------------------------
                        # SHOW RESULT
                        # ---------------------------------

                        return render(

                            request,

                            "analyzer/result.html",

                            {
                                "analysis": analysis,
                                "field": field,
                                "score": score,
                                "skills": skills,
                                "sections": sections,
                                "suggestions": suggestions,
                                "job_description": job_description,
                                "matched_skills": matched_skills,
                                "missing_skills": missing_skills,
                                "match_score": match_score,
                            }

                        )

                except Exception as e:

                    print(
                        "Resume processing error:",
                        e
                    )

                    error = (
                        "Could not process this file. "
                        "Please make sure it is a valid "
                        "PDF or image."
                    )

    return render(

        request,

        "analyzer/home.html",

        {
            "error": error
        }

    )


# =========================================================
# HISTORY
# =========================================================

@login_required
def history(request):

    analyses = ResumeAnalysis.objects.filter(
        user=request.user
         ).order_by(
        "-created_at"
        )

    return render(

        request,

        "analyzer/history.html",

        {
            "analyses": analyses
        }

    )


# =========================================================
# DELETE ONE ANALYSIS
# =========================================================

def delete_analysis(
    request,
    analysis_id
):

    analysis = get_object_or_404(
        ResumeAnalysis,
        id=analysis_id,
        user=request.user
    )

    if request.method == "POST":

        analysis.delete()

    return redirect("history")