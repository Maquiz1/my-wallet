from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.db.models import Count, Avg
from mentorship.models import AssignedCompetence, Visit
from locations.models import Site
from clinical.models import Disease
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder

User = get_user_model()


class GeneralVisualizationReportView(View):
    template_name = "reports/general_visualization_report.html"

    def get(self, request, *args, **kwargs):
        # --- Filters ---
        disease_id = request.GET.get("disease", "all")
        user_filter = request.GET.get("user_filter", "all")
        site_id = request.GET.get("site", "all")
        mentor_id = request.GET.get("mentor", "all")
        mentee_id = request.GET.get("mentee", "all")

        # --- Competence per Disease ---
        comp_qs = AssignedCompetence.objects.all()
        if disease_id != "all":
            comp_qs = comp_qs.filter(competence__disease_id=disease_id)

        if user_filter == "mentor":
            comp_per_disease = comp_qs.values("competence__disease__name").annotate(avg_grade=Avg("mentor_grade"))
        elif user_filter == "mentee":
            comp_per_disease = comp_qs.values("competence__disease__name").annotate(avg_grade=Avg("mentee_grade"))
        else:
            comp_per_disease = comp_qs.values("competence__disease__name").annotate(
                avg_mentor=Avg("mentor_grade"),
                avg_mentee=Avg("mentee_grade"),
            )

        # --- Users Data ---
        users_data = []
        for user in User.objects.filter(groups__name__in=["Mentor", "Mentee"]).distinct():
            mentee_qs = AssignedCompetence.objects.filter(mentee=user)
            mentor_qs = AssignedCompetence.objects.filter(assigned_by=user)
            users_data.append({
                "username": user.username,
                "avg_mentor_grade": float(mentor_qs.aggregate(avg=Avg("mentor_grade"))["avg"] or 0),
                "avg_mentee_grade": float(mentee_qs.aggregate(avg=Avg("mentee_grade"))["avg"] or 0),
            })

        # --- Visits per Site ---
        visits_per_site = list(Visit.objects.values("site__name").annotate(total=Count("id")))

        # --- Sites per Country ---
        sites_per_country = list(Visit.objects.values("site__district__region__country__name").annotate(total_sites=Count("site")))

        # --- Visits per Location ---
        visits_per_location = list(Visit.objects.values("site__name").annotate(total_visits=Count("id")))

        # --- Top 5 Competences ---
        top_comp_qs = AssignedCompetence.objects.all()
        if disease_id != "all":
            top_comp_qs = top_comp_qs.filter(competence__disease_id=disease_id)
        if site_id != "all":
            top_comp_qs = top_comp_qs.filter(visit_day__visit__site_id=site_id)
        if mentor_id != "all":
            top_comp_qs = top_comp_qs.filter(assigned_by_id=mentor_id)
        if mentee_id != "all":
            top_comp_qs = top_comp_qs.filter(mentee_id=mentee_id)

        top_competences = list(top_comp_qs.values(
            "competence__name", "competence__disease__name"
        ).annotate(total_assigned=Count("id")).order_by("-total_assigned")[:5])

        # --- AJAX JSON response ---
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "competence_per_disease": list(comp_per_disease),
                "users_data": users_data,
                "visits_per_site": visits_per_site,
                "sites_per_country": sites_per_country,
                "visits_per_location": visits_per_location,
                "top_competences": top_competences,
            }, encoder=DjangoJSONEncoder)

        # --- Render template ---
        context = {
            "diseases": Disease.objects.all(),
            "mentors": User.objects.filter(groups__name="Mentor"),
            "mentees": User.objects.filter(groups__name="Mentee"),
            "sites": Site.objects.all(),
            "selected_disease": int(disease_id) if disease_id != "all" else None,
            "selected_site": int(site_id) if site_id != "all" else None,
            "selected_mentor": int(mentor_id) if mentor_id != "all" else None,
            "selected_mentee": int(mentee_id) if mentee_id != "all" else None,
            "user_filter": user_filter,
        }
        return render(request, self.template_name, context)
