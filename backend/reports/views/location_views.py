from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from locations.models import Site, Country
from mentorship.models import Visit


# ----- Locations Reports -----
class LocationsReportView(View):
    template_name = "reports/locations_reports.html"

    def get(self, request, *args, **kwargs):
        sites_per_country = Site.objects.values(
            "district__region__country__name"
        ).annotate(total_sites=Count("id"))

        context = {
            "sites_per_country": list(sites_per_country)
        }
        return render(request, self.template_name, context)


# ----- Export Excel -----
class LocationsExportExcelView(View):
    def get(self, request, *args, **kwargs):
        country_id = request.GET.get("country")
        sites_qs = Site.objects.all()
        if country_id and country_id != "all":
            sites_qs = sites_qs.filter(country_id=country_id)

        data = []
        for site in sites_qs:
            visits_count = Visit.objects.filter(site=site).count()
            data.append({
                "Country": site.country.name,
                "Site": site.name,
                "Mentorship Visits": visits_count,
            })

        df = pd.DataFrame(data)
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="locations_report.xlsx"'
        df.to_excel(response, index=False)
        return response


# ----- Export PDF -----
class LocationsExportPDFView(View):
    def get(self, request, *args, **kwargs):
        country_id = request.GET.get("country")
        sites_qs = Site.objects.all()
        if country_id and country_id != "all":
            sites_qs = sites_qs.filter(country_id=country_id)

        data = []
        for site in sites_qs:
            visits_count = Visit.objects.filter(site=site).count()
            data.append({
                "Country": site.country.name,
                "Site": site.name,
                "Mentorship Visits": visits_count,
            })

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="locations_report.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 800, "Locations Report")

        y = 760
        p.setFont("Helvetica", 12)
        for row in data:
            line = f"Country: {row['Country']} | Site: {row['Site']} | Mentorship Visits: {row['Mentorship Visits']}"
            p.drawString(50, y, line)
            y -= 20
            if y < 50:
                p.showPage()
                y = 800

        p.showPage()
        p.save()
        return response
