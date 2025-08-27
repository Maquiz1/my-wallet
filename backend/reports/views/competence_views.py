from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Avg, Count
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from clinical.models import Disease
from mentorship.models import AssignedCompetence


# ----- Competence Reports CBV -----
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg, Count

from clinical.models import Disease
from mentorship.models import AssignedCompetence, MentorGrade, MenteeGrade

class CompetenceReportView(View):
    template_name = "reports/competence_reports.html"

    def get(self, request, *args, **kwargs):
        disease_id = request.GET.get("disease")
        grade_type = request.GET.get("grade", "all")  # default all

        qs = AssignedCompetence.objects.all()
        if disease_id:
            qs = qs.filter(competence__disease_id=disease_id)

        # Table data
        if grade_type == "mentor":
            avg_grade_per_disease = qs.values("competence__disease__name").annotate(
                avg_mentor_grade=Avg("mentor_grade__score")
            )
        elif grade_type == "mentee":
            avg_grade_per_disease = qs.values("competence__disease__name").annotate(
                avg_mentee_grade=Avg("mentee_grade__score")
            )
        else:  # all
            avg_grade_per_disease = qs.values("competence__disease__name").annotate(
                avg_mentor_grade=Avg("mentor_grade__score"),
                avg_mentee_grade=Avg("mentee_grade__score")
            )

        # Prepare chart data
        def get_grade_labels_and_data(grade_field):
            labels = list(qs.values_list(f"{grade_field}__label", flat=True).distinct())
            data = [qs.filter(**{f"{grade_field}__label": lbl}).count() for lbl in labels]
            return labels, data

        overall_labels, overall_data = get_grade_labels_and_data("mentor_grade")
        mentor_labels, mentor_data = get_grade_labels_and_data("mentor_grade")
        mentee_labels, mentee_data = get_grade_labels_and_data("mentee_grade")

        data = {
            "avg_grade_per_disease": list(avg_grade_per_disease),
            "disease_name": Disease.objects.filter(id=disease_id).first().name if disease_id else "All Diseases",
            "overall_grade_labels": overall_labels,
            "overall_grade_data": overall_data,
            "mentor_grade_labels": mentor_labels,
            "mentor_grade_data": mentor_data,
            "mentee_grade_labels": mentee_labels,
            "mentee_grade_data": mentee_data,
        }

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(data)

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

        if grade_type == "mentor":
            data = qs.values("competence__disease__name", "competence__name", "mentor_grade", "mentee__username")
            df = pd.DataFrame(list(data)).rename(columns={"mentor_grade": "Mentor Grade"})
        elif grade_type == "mentee":
            data = qs.values("competence__disease__name", "competence__name", "mentee_grade", "mentee__username")
            df = pd.DataFrame(list(data)).rename(columns={"mentee_grade": "Mentee Grade"})
        else:
            data = qs.values("competence__disease__name", "competence__name", "mentor_grade", "mentee_grade", "mentee__username")
            df = pd.DataFrame(list(data)).rename(columns={"mentor_grade": "Mentor Grade", "mentee_grade": "Mentee Grade"})

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="competence_report_{grade_type}.xlsx"'
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

        if grade_type == "mentor":
            data = qs.values("competence__disease__name", "competence__name", "mentor_grade", "mentee__username")
        elif grade_type == "mentee":
            data = qs.values("competence__disease__name", "competence__name", "mentee_grade", "mentee__username")
        else:
            data = qs.values("competence__disease__name", "competence__name", "mentor_grade", "mentee_grade", "mentee__username")

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="competence_report_{grade_type}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 800, "Competence Report")

        y = 760
        p.setFont("Helvetica", 12)
        for row in data:
            if grade_type == "all":
                grade_text = f"Mentor: {row['mentor_grade']} | Mentee: {row['mentee_grade']}"
            elif grade_type == "mentor":
                grade_text = str(row["mentor_grade"])
            else:
                grade_text = str(row["mentee_grade"])

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
