import io
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.shortcuts import render
from django.db.models import Count, Avg
import pandas as pd
from mentorship.models import AssignedCompetence, Visit
from locations.models import Site
from clinical.models import Disease
from django.contrib.auth import get_user_model
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

User = get_user_model()

# ----- Dashboard View -----
from django.shortcuts import render
from django.views import View
from django.db.models import Count, Avg
from mentorship.models import AssignedCompetence, Visit
from locations.models import Site
from clinical.models import Disease
from django.contrib.auth import get_user_model

User = get_user_model()


from django.views import View
from django.shortcuts import render
from django.db.models import Count, Avg, Q
from clinical.models import Disease
from mentorship.models import AssignedCompetence, Visit
from django.contrib.auth import get_user_model

User = get_user_model()

class GeneralReportView(View):
    template_name = "reports/general_report.html"

    def get(self, request, *args, **kwargs):
        # Filters
        disease_id = request.GET.get("disease", "all")
        user_filter = request.GET.get("user_filter", "all")
        site_id = request.GET.get("site", "all")
        mentor_id = request.GET.get("mentor", "all")
        mentee_id = request.GET.get("mentee", "all")

        # ---- Competence per Disease ----
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

        # ---- Users Data ----
        users_data = []
        for user in User.objects.filter(groups__name__in=["Mentor", "Mentee"]).distinct():
            groups = user.groups.values_list("name", flat=True)
            mentee_qs = AssignedCompetence.objects.filter(mentee=user)
            mentor_qs = AssignedCompetence.objects.filter(assigned_by=user)
            users_data.append({
                "username": user.username,
                "groups": list(groups),
                "mentee_count": mentee_qs.count(),
                "mentor_count": mentor_qs.count(),
                "avg_mentee_grade": mentee_qs.aggregate(Avg("mentee_grade"))["mentee_grade__avg"],
                "avg_mentor_grade": mentor_qs.aggregate(Avg("mentor_grade"))["mentor_grade__avg"],
                "visits_conducted": Visit.objects.filter(mentor=user).count(),
                "visits_attended": Visit.objects.filter(attendees=user).count() if hasattr(Visit, "attendees") else 0,
            })

        # ---- Visits per Site ----
        visits_per_site = Visit.objects.values("site__name").annotate(total=Count("id"))

        # ---- Sites per Country ----
        sites_per_country = Visit.objects.values("site__district__region__country__name").annotate(total_sites=Count("site"))

        # ---- Visits per Location ----
        visits_per_location = Visit.objects.values("site__name").annotate(total_visits=Count("id"))

        # ---- Top 5 Competences ----
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

        context = {
            "competence_per_disease": comp_per_disease,
            "users_data": users_data,
            "visits_per_site": visits_per_site,
            "sites_per_country": sites_per_country,
            "visits_per_location": visits_per_location,
            "top_competences": top_competences,
            "diseases": Disease.objects.all(),
            "mentors": User.objects.filter(groups__name="Mentor"),
            "mentees": User.objects.filter(groups__name="Mentee"),
            "sites": Site.objects.all(),
            "selected_disease": int(disease_id) if disease_id != "all" else "all",
            "user_filter": user_filter,
        }

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # Only return top_competences for AJAX
            return JsonResponse({"top_competences": top_competences})

        return render(request, self.template_name, context)


# ----- Dashboard Export Excel -----
class DashboardExportExcelView(View):
    def get(self, request, *args, **kwargs):
        disease_id = request.GET.get("disease")
        user_filter = request.GET.get("user_filter")  # mentor, mentee

        comp_qs = AssignedCompetence.objects.all()
        if disease_id and disease_id != "all":
            comp_qs = comp_qs.filter(competence__disease_id=disease_id)
        if user_filter == "mentor":
            comp_qs = comp_qs.filter(assigned_by__groups__name="Mentor")
        elif user_filter == "mentee":
            comp_qs = comp_qs.filter(mentee__groups__name="Mentee")

        competence_data = comp_qs.values(
            "competence__disease__name",
            "competence__name",
            "mentee__username",
            "mentee_grade",
            "mentor_grade"
        )

        users_list = []
        for user in User.objects.filter(groups__name__in=["Mentor", "Mentee"]):
            groups = user.groups.values_list("name", flat=True)
            mentee_count = AssignedCompetence.objects.filter(mentee=user).count()
            mentor_count = AssignedCompetence.objects.filter(assigned_by=user).count()
            avg_mentee_grade = AssignedCompetence.objects.filter(mentee=user).aggregate(avg=Avg("mentee_grade"))["avg"]
            avg_mentor_grade = AssignedCompetence.objects.filter(assigned_by=user).aggregate(avg=Avg("mentor_grade"))["avg"]
            visits_conducted = Visit.objects.filter(mentor=user).count()
            visits_attended = Visit.objects.filter(attendees=user).count() if hasattr(Visit, "attendees") else 0
            users_list.append({
                "username": user.username,
                "groups": ", ".join(groups),
                "mentee_count": mentee_count,
                "mentor_count": mentor_count,
                "avg_mentee_grade": avg_mentee_grade,
                "avg_mentor_grade": avg_mentor_grade,
                "mentorship_conducted": visits_conducted,
                "mentorship_attended": visits_attended,
            })

        visits_per_site = Visit.objects.values("site__name").annotate(total=Count("id"))
        sites_per_country = Site.objects.values("district__region__country__name").annotate(total_sites=Count("id"))

        # Write Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame(list(competence_data)).to_excel(writer, sheet_name="Competence", index=False)
            pd.DataFrame(users_list).to_excel(writer, sheet_name="Users", index=False)
            pd.DataFrame(list(visits_per_site)).to_excel(writer, sheet_name="VisitsPerSite", index=False)
            pd.DataFrame(list(sites_per_country)).to_excel(writer, sheet_name="SitesPerCountry", index=False)
            writer.save()

        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="dashboard_report.xlsx"'
        return response

    
class DashboardExportPDFView(View):
    def get(self, request, *args, **kwargs):
        disease_id = request.GET.get("disease")
        user_filter = request.GET.get("user_filter")  # mentor, mentee, all

        comp_qs = AssignedCompetence.objects.all()
        if disease_id and disease_id != "all":
            comp_qs = comp_qs.filter(competence__disease_id=disease_id)
        if user_filter == "mentor":
            comp_qs = comp_qs.filter(assigned_by__groups__name="Mentor")
        elif user_filter == "mentee":
            comp_qs = comp_qs.filter(mentee__groups__name="Mentee")

        competence_data = comp_qs.values(
            "competence__disease__name",
            "competence__name",
            "mentee__username",
            "mentee_grade",
            "mentor_grade"
        )

        users_list = []
        for user in User.objects.all():
            groups = user.groups.values_list("name", flat=True)
            mentee_count = AssignedCompetence.objects.filter(mentee=user).count()
            mentor_count = AssignedCompetence.objects.filter(assigned_by=user).count()
            avg_mentee_grade = AssignedCompetence.objects.filter(mentee=user).aggregate(avg=Avg("mentee_grade"))["avg"]
            avg_mentor_grade = AssignedCompetence.objects.filter(assigned_by=user).aggregate(avg=Avg("mentor_grade"))["avg"]
            visits_conducted = Visit.objects.filter(mentor=user).count()
            visits_attended = Visit.objects.filter(attendees=user).count() if hasattr(Visit, "attendees") else 0
            users_list.append({
                "username": user.username,
                "groups": ", ".join(groups),
                "mentee_count": mentee_count,
                "mentor_count": mentor_count,
                "avg_mentee_grade": avg_mentee_grade,
                "avg_mentor_grade": avg_mentor_grade,
                "visits_conducted": visits_conducted,
                "visits_attended": visits_attended,
            })

        visits_per_site = Visit.objects.values("site__name").annotate(total=Count("id"))
        sites_per_country = Site.objects.values("country__name").annotate(total_sites=Count("id"))

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="dashboard_report.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 800, "Dashboard Report")

        y = 770
        p.setFont("Helvetica", 12)
        p.drawString(50, y, "Competence Report:")
        y -= 20
        for row in competence_data:
            line = f"Disease: {row['competence__disease__name']} | Competence: {row['competence__name']} | Mentee: {row['mentee__username']} | Mentee Grade: {row['mentee_grade']} | Mentor Grade: {row['mentor_grade']}"
            p.drawString(50, y, line[:90])
            y -= 15
            if y < 50:
                p.showPage()
                y = 800

        p.drawString(50, y, "Users Report:")
        y -= 20
        for u in users_list:
            line = f"{u['username']} ({u['groups']}): Mentee {u['mentee_count']}, Mentor {u['mentor_count']}, Avg Mentee Grade {u['avg_mentee_grade']}, Avg Mentor Grade {u['avg_mentor_grade']}, Mentorship Conducted {u['visits_conducted']}, Mentorship Attended {u['visits_attended']}"
            p.drawString(50, y, line[:90])
            y -= 15
            if y < 50:
                p.showPage()
                y = 800

        p.drawString(50, y, "Visits per Site:")
        y -= 20
        for row in visits_per_site:
            line = f"Site: {row['site__name']} | Total Visits: {row['total']}"
            p.drawString(50, y, line)
            y -= 15
            if y < 50:
                p.showPage()
                y = 800

        p.drawString(50, y, "Sites per Country:")
        y -= 20
        for row in sites_per_country:
            line = f"Country: {row['country__name']} | Total Sites: {row['total_sites']}"
            p.drawString(50, y, line)
            y -= 15
            if y < 50:
                p.showPage()
                y = 800

        p.showPage()
        p.save()
        return response
