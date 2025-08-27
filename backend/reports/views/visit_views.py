from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
from django.utils.dateparse import parse_date
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import json

from mentorship.models import Visit
from locations.models import Site


# ----- Visits Reports HTML CBV -----
class VisitsReportView(View):
    template_name = "reports/visits_reports.html"

    def get(self, request, *args, **kwargs):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        site_id = request.GET.get("site")

        visits = Visit.objects.all()
        if start_date and end_date:
            visits = visits.filter(start_date__range=[parse_date(start_date), parse_date(end_date)])
        if site_id:
            visits = visits.filter(site_id=site_id)

        visits_per_site = visits.values("site__name").annotate(total=Count("id"))
        visits_over_time = visits.values("start_date").annotate(total=Count("id")).order_by("start_date")

        context = {
            "visits_per_site_labels": json.dumps([v['site__name'] for v in visits_per_site]),
            "visits_per_site_data": json.dumps([v['total'] for v in visits_per_site]),
            "visits_over_time_labels": json.dumps([str(v['start_date']) for v in visits_over_time]),
            "visits_over_time_data": json.dumps([v['total'] for v in visits_over_time]),
            "sites": Site.objects.all(),
            "start_date": start_date or "",
            "end_date": end_date or "",
            "selected_site": int(site_id) if site_id else None,
        }
        return render(request, self.template_name, context)


# ----- Visits Export Excel CBV -----
class VisitsExportExcelView(View):
    def get(self, request, *args, **kwargs):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        site_id = request.GET.get("site")

        visits = Visit.objects.all()
        if start_date and end_date:
            visits = visits.filter(start_date__range=[parse_date(start_date), parse_date(end_date)])
        if site_id:
            visits = visits.filter(site_id=site_id)

        data = visits.values("site__name", "start_date", "end_date", "mentor__username")
        df = pd.DataFrame(list(data))

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="visits_report.xlsx"'
        df.to_excel(response, index=False)
        return response


# ----- Visits Export PDF CBV -----
class VisitsExportPDFView(View):
    def get(self, request, *args, **kwargs):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        site_id = request.GET.get("site")

        visits = Visit.objects.all()
        if start_date and end_date:
            visits = visits.filter(start_date__range=[parse_date(start_date), parse_date(end_date)])
        if site_id:
            visits = visits.filter(site_id=site_id)

        data = visits.values("site__name", "start_date", "end_date", "mentor__username")

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="visits_report.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 800, "Visits Report")

        y = 760
        p.setFont("Helvetica", 12)
        for row in data:
            p.drawString(
                50,
                y,
                f"Site: {row['site__name']} | Start: {row['start_date']} | End: {row['end_date']} | Mentor: {row['mentor__username']}"
            )
            y -= 20
            if y < 50:
                p.showPage()
                y = 800

        p.showPage()
        p.save()
        return response
