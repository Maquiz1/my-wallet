# reports/views.py
import io
from django.http import HttpResponse
from django.views import View
from django.db.models import Count, Q
from openpyxl import Workbook
from mentorship.models import AssignedCompetence,MenteeGrade,MentorGrade
from clinical.models import Disease
from django.contrib.auth import get_user_model
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.shortcuts import render
from locations.models import Site

User = get_user_model()
class GradeSummaryReportView(View):
    template_name = "reports/summary/grade.html"

    def get(self, request):
        # ----- Filters -----
        disease_id = request.GET.get("disease", "all")
        site_id = request.GET.get("site", "all")
        user_filter = request.GET.get("user_filter", "all")

        try:
            disease_id_int = int(disease_id)
        except (ValueError, TypeError):
            disease_id_int = None

        try:
            site_id_int = int(site_id)
        except (ValueError, TypeError):
            site_id_int = None

        # ----- Base QuerySet -----
        qs = AssignedCompetence.objects.all()
        if disease_id_int:
            qs = qs.filter(competence__disease_id=disease_id_int)
        if site_id_int:
            qs = qs.filter(visit_day__visit__site_id=site_id_int)

        if user_filter == "mentor":
            qs = qs.exclude(mentor_grade__isnull=True)
        elif user_filter == "mentee":
            qs = qs.exclude(mentee_grade__isnull=True)

        # ----- Mentor Grades -----
        mentor_counts = qs.values("mentor_grade").annotate(count=Count("id"))
        mentor_total = sum(row["count"] for row in mentor_counts)
        mentor_summary = []

        all_mentor_grades = MentorGrade.objects.all()
        for grade in all_mentor_grades:
            count = next((row["count"] for row in mentor_counts if row["mentor_grade"] == grade.id), 0)
            percentage = round((count / mentor_total) * 100, 2) if mentor_total else 0
            mentor_summary.append({
                "grade": grade.label,
                "count": count,
                "percentage": percentage
            })

        # ----- Mentee Grades -----
        mentee_counts = qs.values("mentee_grade").annotate(count=Count("id"))
        mentee_total = sum(row["count"] for row in mentee_counts)
        mentee_summary = []

        all_mentee_grades = MenteeGrade.objects.all()
        for grade in all_mentee_grades:
            count = next((row["count"] for row in mentee_counts if row["mentee_grade"] == grade.id), 0)
            percentage = round((count / mentee_total) * 100, 2) if mentee_total else 0
            mentee_summary.append({
                "grade": grade.label,
                "count": count,
                "percentage": percentage
            })

        # ----- Context -----
        context = {
            "mentor_summary": mentor_summary,
            "mentee_summary": mentee_summary,
            "mentor_total": mentor_total,
            "mentee_total": mentee_total,
            "diseases": Disease.objects.all(),
            "sites": Site.objects.all(),
            "selected_disease": disease_id,
            "selected_site": site_id,
            "user_filter": user_filter,
        }

        return render(request, self.template_name, context)
    
class GradeSummaryExportExcelView(View):
    def get(self, request):
        # --- Filters ---
        disease_id = request.GET.get("disease", "")
        site_id = request.GET.get("site", "")
        user_filter = request.GET.get("user_filter", "all")

        # Safe conversion to int
        try:
            selected_disease = int(disease_id) if disease_id and disease_id != "all" else None
        except ValueError:
            selected_disease = None

        try:
            selected_site = int(site_id) if site_id and site_id != "all" else None
        except ValueError:
            selected_site = None

        # --- Build filters ---
        filters = Q()
        if selected_disease:
            filters &= Q(competence__disease_id=selected_disease)
        if selected_site:
            filters &= Q(visit_day__visit__site_id=selected_site)

        # --- Mentor Grades ---
        mentor_grades_qs = AssignedCompetence.objects.filter(filters).values("mentor_grade").annotate(count=Count("id"))
        mentor_total = sum(row["count"] for row in mentor_grades_qs)
        mentor_summary = [
            {
                "Grade": row["mentor_grade"] or "Not Graded",
                "Count": row["count"],
                "Percentage": round((row["count"] / mentor_total) * 100, 2) if mentor_total else 0
            }
            for row in mentor_grades_qs
        ]

        # --- Mentee Grades ---
        mentee_grades_qs = AssignedCompetence.objects.filter(filters).values("mentee_grade").annotate(count=Count("id"))
        mentee_total = sum(row["count"] for row in mentee_grades_qs)
        mentee_summary = [
            {
                "Grade": row["mentee_grade"] or "Not Graded",
                "Count": row["count"],
                "Percentage": round((row["count"] / mentee_total) * 100, 2) if mentee_total else 0
            }
            for row in mentee_grades_qs
        ]

        # --- Create Excel ---
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            pd.DataFrame(mentor_summary).to_excel(writer, sheet_name="Mentor Grades", index=False)
            pd.DataFrame(mentee_summary).to_excel(writer, sheet_name="Mentee Grades", index=False)
            writer.save()

        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="grade_summary.xlsx"'
        return response


class GradeSummaryExportPDFView(View):
    def get(self, request):
        # --- Filters ---
        disease_id = request.GET.get("disease", "")
        site_id = request.GET.get("site", "")
        user_filter = request.GET.get("user_filter", "all")

        # Safe conversion
        try:
            selected_disease = int(disease_id) if disease_id and disease_id != "all" else None
        except ValueError:
            selected_disease = None

        try:
            selected_site = int(site_id) if site_id and site_id != "all" else None
        except ValueError:
            selected_site = None

        # --- Build filters ---
        filters = Q()
        if selected_disease:
            filters &= Q(competence__disease_id=selected_disease)
        if selected_site:
            filters &= Q(visit_day__visit__site_id=selected_site)

        # --- Mentor Grades ---
        mentor_grades_qs = AssignedCompetence.objects.filter(filters).values("mentor_grade").annotate(count=Count("id"))
        mentor_total = sum(row["count"] for row in mentor_grades_qs)
        mentor_summary = [
            {
                "grade": row["mentor_grade"] or "Not Graded",
                "count": row["count"],
                "percentage": round((row["count"] / mentor_total) * 100, 2) if mentor_total else 0
            }
            for row in mentor_grades_qs
        ]

        # --- Mentee Grades ---
        mentee_grades_qs = AssignedCompetence.objects.filter(filters).values("mentee_grade").annotate(count=Count("id"))
        mentee_total = sum(row["count"] for row in mentee_grades_qs)
        mentee_summary = [
            {
                "grade": row["mentee_grade"] or "Not Graded",
                "count": row["count"],
                "percentage": round((row["count"] / mentee_total) * 100, 2) if mentee_total else 0
            }
            for row in mentee_grades_qs
        ]

        # --- Generate PDF ---
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="grade_summary.pdf"'
        p = canvas.Canvas(response, pagesize=A4)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 800, "Grade Summary Report")

        y = 780
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Mentor Grades:")
        y -= 20
        p.setFont("Helvetica", 12)
        for row in mentor_summary:
            line = f"{row['grade']}: {row['count']} ({row['percentage']}%)"
            p.drawString(60, y, line)
            y -= 15
            if y < 50:
                p.showPage()
                y = 800

        y -= 10
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Mentee Grades:")
        y -= 20
        p.setFont("Helvetica", 12)
        for row in mentee_summary:
            line = f"{row['grade']}: {row['count']} ({row['percentage']}%)"
            p.drawString(60, y, line)
            y -= 15
            if y < 50:
                p.showPage()
                y = 800

        p.showPage()
        p.save()
        return response