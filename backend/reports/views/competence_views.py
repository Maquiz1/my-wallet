from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Avg
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from clinical.models import Disease
from mentorship.models import AssignedCompetence


# ----- Competence Reports CBV -----
class CompetenceReportView(View):
    template_name = "reports/competence_reports.html"

    def get(self, request, *args, **kwargs):
        disease_id = request.GET.get("disease")
        grade_type = request.GET.get("grade", "all")  # all / mentor / mentee

        qs = AssignedCompetence.objects.all()
        if disease_id:
            qs = qs.filter(competence__disease_id=disease_id)

        # Determine grade field(s)
        if grade_type == "mentor":
            avg_grade_per_disease = qs.values("competence__disease__name").annotate(
                avg_grade=Avg("mentor_grade")
            )
        elif grade_type == "mentee":
            avg_grade_per_disease = qs.values("competence__disease__name").annotate(
                avg_grade=Avg("mentee_grade")
            )
        else:  # all
            avg_grade_per_disease = qs.values("competence__disease__name").annotate(
                avg_mentor_grade=Avg("mentor_grade"),
                avg_mentee_grade=Avg("mentee_grade")
            )

        context = {
            "avg_grade_per_disease": list(avg_grade_per_disease),
            "diseases": Disease.objects.all(),
            "selected_disease": int(disease_id) if disease_id else None,
            "selected_grade": grade_type,
        }
        return render(request, self.template_name, context)


# ----- Export Excel CBV -----
class CompetenceExportExcelView(View):
    def get(self, request, *args, **kwargs):
        disease_id = request.GET.get("disease")
        grade_type = request.GET.get("grade", "all")

        qs = AssignedCompetence.objects.all()
        if disease_id:
            qs = qs.filter(competence__disease_id=disease_id)

        # Determine which fields to include
        if grade_type == "mentor":
            grade_field = "mentor_grade"
            filename_suffix = "mentor"
            data = qs.values("competence__disease__name", "competence__name", grade_field, "mentee__username")
            df = pd.DataFrame(list(data)).rename(columns={grade_field: "grade"})
        elif grade_type == "mentee":
            grade_field = "mentee_grade"
            filename_suffix = "mentee"
            data = qs.values("competence__disease__name", "competence__name", grade_field, "mentee__username")
            df = pd.DataFrame(list(data)).rename(columns={grade_field: "grade"})
        else:  # all
            filename_suffix = "all"
            data = qs.values("competence__disease__name", "competence__name", "mentor_grade", "mentee_grade", "mentee__username")
            df = pd.DataFrame(list(data))

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="competence_report_{filename_suffix}.xlsx"'
        df.to_excel(response, index=False)
        return response


# ----- Export PDF CBV -----
class CompetenceExportPDFView(View):
    def get(self, request, *args, **kwargs):
        disease_id = request.GET.get("disease")
        grade_type = request.GET.get("grade", "all")

        qs = AssignedCompetence.objects.all()
        if disease_id:
            qs = qs.filter(competence__disease_id=disease_id)

        # Determine which fields to include
        if grade_type == "mentor":
            grade_field = "mentor_grade"
            filename_suffix = "mentor"
            data = qs.values("competence__disease__name", "competence__name", grade_field, "mentee__username")
        elif grade_type == "mentee":
            grade_field = "mentee_grade"
            filename_suffix = "mentee"
            data = qs.values("competence__disease__name", "competence__name", grade_field, "mentee__username")
        else:  # all
            filename_suffix = "all"
            data = qs.values("competence__disease__name", "competence__name", "mentor_grade", "mentee_grade", "mentee__username")

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="competence_report_{filename_suffix}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 800, "Competence Report")

        y = 760
        p.setFont("Helvetica", 12)
        for row in data:
            if grade_type == "all":
                grade_text = f"Mentor: {row['mentor_grade']} | Mentee: {row['mentee_grade']}"
            else:
                grade_text = str(row[grade_field])
            p.drawString(
                50,
                y,
                f"Disease: {row['competence__disease__name']} | "
                f"Competence: {row['competence__name']} | "
                f"Grade: {grade_text} | "
                f"Mentee: {row['mentee__username']}"
            )
            y -= 20
            if y < 50:
                p.showPage()
                y = 800

        p.showPage()
        p.save()
        return response
