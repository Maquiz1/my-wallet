from django.views import View
from django.shortcuts import render
from django.db.models import Count, Avg
from mentorship.models import AssignedCompetence, Visit
from locations.models import Site, Country
from clinical.models import Disease
from django.contrib.auth import get_user_model

User = get_user_model()

class IndexView(View):
    template_name = "reports/index.html"

    def get(self, request, *args, **kwargs):
        # ----- Competence Data -----
        disease_id = request.GET.get("disease")
        user_filter = request.GET.get("user_filter")  # mentor, mentee, all
        comp_qs = AssignedCompetence.objects.all()

        if disease_id and disease_id != "all":
            comp_qs = comp_qs.filter(competence__disease_id=disease_id)
        if user_filter == "mentor":
            comp_qs = comp_qs.filter(assigned_by__groups__name="Mentor")
        elif user_filter == "mentee":
            comp_qs = comp_qs.filter(mentee__groups__name="Mentee")

        competence_per_disease = comp_qs.values("competence__disease__name").annotate(avg_grade=Avg("mentee_grade"))

        # ----- Users Data -----
        users_data = []
        for user in User.objects.all():
            groups = user.groups.values_list("name", flat=True)
            mentee_count = AssignedCompetence.objects.filter(mentee=user).count()
            mentor_count = AssignedCompetence.objects.filter(assigned_by=user).count()
            avg_mentee_grade = AssignedCompetence.objects.filter(mentee=user).aggregate(avg=Avg("mentee_grade"))["avg"]
            avg_mentor_grade = AssignedCompetence.objects.filter(assigned_by=user).aggregate(avg=Avg("mentor_grade"))["avg"]
            visits_conducted = Visit.objects.filter(mentor=user).count()
            visits_attended = Visit.objects.filter(attendees=user).count() if hasattr(Visit, "attendees") else 0
            users_data.append({
                "username": user.username,
                "groups": list(groups),
                "mentee_count": mentee_count,
                "mentor_count": mentor_count,
                "avg_mentee_grade": avg_mentee_grade,
                "avg_mentor_grade": avg_mentor_grade,
                "visits_conducted": visits_conducted,
                "visits_attended": visits_attended,
            })

        # ----- Visits Data -----
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        visits_qs = Visit.objects.all()
        if start_date and end_date:
            visits_qs = visits_qs.filter(start_date__range=[start_date, end_date])

        visits_per_site = visits_qs.values("site__name").annotate(total=Count("id"))

        # ----- Locations Data -----
        sites_per_country = Site.objects.values(
            "district__region__country__name"
        ).annotate(total_sites=Count("id"))
        visits_per_location = Visit.objects.values("site__name").annotate(total_visits=Count("id"))

        context = {
            "competence_per_disease": list(competence_per_disease),
            "users_data": users_data,
            "visits_per_site": list(visits_per_site),
            "sites_per_country": list(sites_per_country),
            "visits_per_location": list(visits_per_location),
            "diseases": Disease.objects.all(),
            "selected_disease": int(disease_id) if disease_id and disease_id != "all" else None,
            "user_filter": user_filter or "all",
        }
        return render(request, self.template_name, context)

