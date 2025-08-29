# reports/views.py
from django.http import HttpResponse
from django.views import View
from django.db.models import Count, Q
from mentorship.models import AssignedCompetence, MenteeGrade, MentorGrade
from clinical.models import Disease, Competence
from locations.models import Site
from django.shortcuts import render


class CompetenceSummaryReportView(View):
    template_name = "reports/summary/competence/competence_summary_report.html"

    def get(self, request):
        # ----- Filters -----
        disease_id = request.GET.get("disease", "all")
        site_id = request.GET.get("site", "all")
        user_filter = request.GET.get("user_filter", "all")

        # Safe conversion
        if disease_id not in ["all", ""]:
            try:
                disease_id = int(disease_id)
            except ValueError:
                disease_id = "all"
        if site_id not in ["all", ""]:
            try:
                site_id = int(site_id)
            except ValueError:
                site_id = "all"

        # ----- Queryset with filters -----
        qs = AssignedCompetence.objects.all()
        if disease_id != "all":
            qs = qs.filter(competence__disease_id=disease_id)
        if site_id != "all":
            qs = qs.filter(visit_day__visit__site_id=site_id)
        if user_filter == "mentor":
            qs = qs.exclude(mentor_grade__isnull=True)
        elif user_filter == "mentee":
            qs = qs.exclude(mentee_grade__isnull=True)

        # ----- Competence Summary -----
        competence_counts = qs.values("competence").annotate(count=Count("id"))
        counts_dict = {row["competence"]: row["count"] for row in competence_counts}
        total_assignments = sum(counts_dict.values())

        all_competences = Competence.objects.all()
        if disease_id != "all":
            all_competences = all_competences.filter(disease_id=disease_id)

        competence_summary = []
        for comp in all_competences.order_by("name"):
            count = counts_dict.get(comp.id, 0)
            competence_summary.append({
                "competence_name": comp.name,
                "competence_description": comp.description or "-",  # Add description
                "count": count,
                "percentage": round((count / total_assignments) * 100, 2) if total_assignments else 0
            })

        context = {
            "competence_summary": competence_summary,
            "total_assignments": total_assignments,
            "diseases": Disease.objects.all(),
            "sites": Site.objects.all(),
            "selected_disease": disease_id,
            "selected_site": site_id,
            "user_filter": user_filter,
        }
        return render(request, self.template_name, context)
