# from django.shortcuts import render
# from django.db.models import Count
# from django.utils.dateparse import parse_date
# from django.http import HttpResponse
# import pandas as pd
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas

# from mentorship.models import Visit
# from locations.models import Site


# from django.contrib.auth import get_user_model

# User = get_user_model()


# def index(request):
#     return render(request, "reports/index.html")

# def visits_reports(request):
#     start_date = request.GET.get("start_date")
#     end_date = request.GET.get("end_date")
#     site_id = request.GET.get("site")

#     visits = Visit.objects.all()

#     # Filter by start_date/end_date
#     if start_date and end_date:
#         visits = visits.filter(start_date__range=[parse_date(start_date), parse_date(end_date)])
#     if site_id:
#         visits = visits.filter(site_id=site_id)

#     # Aggregations
#     visits_per_site = visits.values("site__name").annotate(total=Count("id"))
#     visits_over_time = visits.values("start_date").annotate(total=Count("id")).order_by("start_date")

#     context = {
#         "visits_per_site": list(visits_per_site),
#         "visits_over_time": list(visits_over_time),
#         "sites": Site.objects.all(),
#         "start_date": start_date or "",
#         "end_date": end_date or "",
#         "selected_site": int(site_id) if site_id else None,
#     }
#     return render(request, "reports/visits_reports.html", context)


# # ----- EXPORT EXCEL -----
# def export_excel(request):
#     start_date = request.GET.get("start_date")
#     end_date = request.GET.get("end_date")
#     site_id = request.GET.get("site")

#     visits = Visit.objects.all()
#     if start_date and end_date:
#         visits = visits.filter(start_date__range=[parse_date(start_date), parse_date(end_date)])
#     if site_id:
#         visits = visits.filter(site_id=site_id)

#     data = visits.values("site__name", "start_date", "end_date", "mentor__username")
#     df = pd.DataFrame(list(data))

#     response = HttpResponse(
#         content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )
#     response["Content-Disposition"] = 'attachment; filename="visits_report.xlsx"'
#     df.to_excel(response, index=False)
#     return response


# # ----- EXPORT PDF -----
# def export_pdf(request):
#     start_date = request.GET.get("start_date")
#     end_date = request.GET.get("end_date")
#     site_id = request.GET.get("site")

#     visits = Visit.objects.all()
#     if start_date and end_date:
#         visits = visits.filter(start_date__range=[parse_date(start_date), parse_date(end_date)])
#     if site_id:
#         visits = visits.filter(site_id=site_id)

#     data = visits.values("site__name", "start_date", "end_date", "mentor__username")

#     response = HttpResponse(content_type="application/pdf")
#     response["Content-Disposition"] = 'attachment; filename="visits_report.pdf"'

#     p = canvas.Canvas(response, pagesize=A4)
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(100, 800, "Visits Report")

#     y = 760
#     p.setFont("Helvetica", 12)
#     for row in data:
#         p.drawString(
#             50,
#             y,
#             f"Site: {row['site__name']} | Start: {row['start_date']} | End: {row['end_date']} | Mentor: {row['mentor__username']}"
#         )
#         y -= 20
#         if y < 50:
#             p.showPage()
#             y = 800

#     p.showPage()
#     p.save()
#     return response


# # def visits_reports(request):
# #     visits_per_site = Visit.objects.values("site__name").annotate(total=Count("id"))
# #     visits_over_time = Visit.objects.values("date").annotate(total=Count("id")).order_by("date")
# #     return render(request, "reports/visits_reports.html", {
# #         "visits_per_site": list(visits_per_site),
# #         "visits_over_time": list(visits_over_time),
# #     })

# def competence_reports(request):
#     avg_grade_per_disease = AssignedCompetence.objects.values(
#         "competence__disease__name"
#     ).annotate(avg_grade=Avg("grade"))
#     return render(request, "reports/competence_reports.html", {
#         "avg_grade_per_disease": list(avg_grade_per_disease),
#     })

# def users_reports(request):
#     total_users = User.objects.count()
#     staff_users = User.objects.filter(is_staff=True).count()
#     mentees = User.objects.filter(groups__name="Mentee").count()
#     mentors = User.objects.filter(groups__name="Mentor").count()
#     return render(request, "reports/users_reports.html", {
#         "total_users": total_users,
#         "staff_users": staff_users,
#         "mentees": mentees,
#         "mentors": mentors,
#     })

# def locations_reports(request):
#     sites_per_country = Site.objects.values("country__name").annotate(total=Count("id"))
#     return render(request, "reports/locations_reports.html", {
#         "sites_per_country": list(sites_per_country),
#     })
    
# # def index(request):
# #     return render(request, "reports/index.html")

# def dashboard_report(request):
#     return render(request, "reports/index.html")

# # def users_reports(request):
# #     return render(request, "reports/index.html")

# # def locations_reports(request):
# #     return render(request, "reports/index.html")

# # def visits_reports(request):
# #     start_date = request.GET.get("start_date")
# #     end_date = request.GET.get("end_date")
# #     site_id = request.GET.get("site")

# #     visits = Visit.objects.all()

# #     if start_date and end_date:
# #         visits = visits.filter(date__range=[parse_date(start_date), parse_date(end_date)])
# #     if site_id:
# #         visits = visits.filter(site_id=site_id)

# #     visits_per_site = visits.values("site__name").annotate(total=Count("id"))
# #     visits_over_time = visits.values("date").annotate(total=Count("id")).order_by("date")

# #     context = {
# #         "visits_per_site": list(visits_per_site),
# #         "visits_over_time": list(visits_over_time),
# #         "sites": Site.objects.all(),   # for dropdown
# #         "start_date": start_date or "",
# #         "end_date": end_date or "",
# #         "selected_site": int(site_id) if site_id else None,
# #     }
# #     return render(request, "reports/visits_reports.html", context)


# # def competence_reports(request):
# #     disease_id = request.GET.get("disease")

# #     qs = AssignedCompetence.objects.all()
# #     if disease_id:
# #         qs = qs.filter(competence__disease_id=disease_id)

# #     avg_grade_per_disease = qs.values("competence__disease__name").annotate(avg_grade=Avg("grade"))

# #     return render(request, "reports/competence_reports.html", {
# #         "avg_grade_per_disease": list(avg_grade_per_disease),
# #         "diseases": Disease.objects.all(),
# #         "selected_disease": int(disease_id) if disease_id else None,
# #     })


# # def export_excel(request):
# #     # Example queryset (replace with your filtered data)
# #     data = [
# #         {"site": "Dar es Salaam", "visits": 120},
# #         {"site": "Morogoro", "visits": 95},
# #     ]
# #     df = pd.DataFrame(data)

# #     # Create response
# #     response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
# #     response["Content-Disposition"] = 'attachment; filename="report.xlsx"'

# #     # Save Excel to response
# #     df.to_excel(response, index=False)
# #     return response



# # def export_pdf(request):
# #     response = HttpResponse(content_type="application/pdf")
# #     response["Content-Disposition"] = 'attachment; filename="report.pdf"'

# #     p = canvas.Canvas(response, pagesize=A4)
# #     p.drawString(100, 800, "Report Example")
# #     p.drawString(100, 780, "Site: Dar es Salaam, Visits: 120")
# #     p.drawString(100, 760, "Site: Morogoro, Visits: 95")
# #     p.showPage()
# #     p.save()

# #     return response

# # reports/views.py
# # from django.shortcuts import render
# # from .services import get_dashboard_context


# # def dashboard_report(request):
# #     context = get_dashboard_context()
# #     return render(request, 'reports/index.html', context)




# # from django.shortcuts import render
# # from mentorship.models import Visit, VisitDay, AssignedCompetence
# # from django.db.models import Count, Q
# # import json
# # from django.db.models import Case, When, BooleanField, Value


# # def dashboard_report(request):
# #     # Visits per Site
# #     visits_qs = Visit.objects.values('site__name').annotate(total=Count('id'))
# #     visits_per_site = {v['site__name']: v['total'] for v in visits_qs}

# #     # Mentorship Progress Over Time (monthly)
# #     progress_qs = VisitDay.objects.values('date__month').annotate(total=Count('id')).order_by('date__month')
# #     progress_labels = [v['date__month'] for v in progress_qs]
# #     progress_data = [v['total'] for v in progress_qs]

# #     # Competence Completion Status
# #     # status_qs = AssignedCompetence.objects.aggregate(
# #     #     completed=Count('id', filter=Q(is_completed=True)),
# #     #     pending=Count('id', filter=Q(is_completed=False, is_self_assessed=True)),
# #     #     in_progress=Count('id', filter=Q(is_self_assessed=False))
# #     # )
    
# #     status_qs = AssignedCompetence.objects.annotate(
# #         is_self_assessed=Case(
# #             When(mentee_grade__isnull=False, then=Value(True)),
# #             default=Value(False),
# #             output_field=BooleanField(),
# #         )
# #     ).aggregate(
# #         completed=Count('id', filter=Q(is_completed=True)),
# #         pending=Count('id', filter=Q(is_completed=False, is_self_assessed=True)),
# #         in_progress=Count('id', filter=Q(is_self_assessed=False))
# #     )
    
# #     competence_status = {
# #         'Completed': status_qs['completed'],
# #         'Pending': status_qs['pending'],
# #         'In Progress': status_qs['in_progress']
# #     }

# #     # Competence per Visit
# #     comp_visit_qs = AssignedCompetence.objects.values('visit_day__visit__id', 'visit_day__visit__site__name').annotate(total=Count('id'))
# #     comp_per_visit_labels = [f"{v['visit_day__visit__site__name']} (Visit {v['visit_day__visit__id']})" for v in comp_visit_qs]
# #     comp_per_visit_data = [v['total'] for v in comp_visit_qs]

# #     # Competence per Disease
# #     comp_disease_qs = AssignedCompetence.objects.values('disease__name').annotate(total=Count('id'))
# #     comp_per_disease_labels = [v['disease__name'] for v in comp_disease_qs]
# #     comp_per_disease_data = [v['total'] for v in comp_disease_qs]

# #     # Competence per Mentee
# #     comp_mentee_qs = AssignedCompetence.objects.values('mentee__username').annotate(total=Count('id'))
# #     comp_per_mentee_labels = [v['mentee__username'] for v in comp_mentee_qs]
# #     comp_per_mentee_data = [v['total'] for v in comp_mentee_qs]

# #     context = {
# #         'visits_labels': json.dumps(list(visits_per_site.keys())),
# #         'visits_data': json.dumps(list(visits_per_site.values())),
# #         'progress_labels': json.dumps(progress_labels),
# #         'progress_data': json.dumps(progress_data),
# #         'status_labels': json.dumps(list(competence_status.keys())),
# #         'status_data': json.dumps(list(competence_status.values())),
# #         'comp_visit_labels': json.dumps(comp_per_visit_labels),
# #         'comp_visit_data': json.dumps(comp_per_visit_data),
# #         'comp_disease_labels': json.dumps(comp_per_disease_labels),
# #         'comp_disease_data': json.dumps(comp_per_disease_data),
# #         'comp_mentee_labels': json.dumps(comp_per_mentee_labels),
# #         'comp_mentee_data': json.dumps(comp_per_mentee_data),
# #     }

# #     return render(request, 'reports/index.html', context)
