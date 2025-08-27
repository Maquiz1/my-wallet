from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from reports.services import get_dashboard_context
from clinical.models import Disease

class GeneralDashboardReportView(View):
    template_name = "reports/general_dashboard_report.html"

    def get(self, request, *args, **kwargs):
        # Filters
        disease_id = request.GET.get("disease", "all")
        user_filter = request.GET.get("user_filter", "all")

        # Dashboard context from services
        context = get_dashboard_context()

        # Add filters and disease list
        context['user_filter'] = user_filter
        context['diseases'] = Disease.objects.all()
        context['selected_disease'] = int(disease_id) if disease_id != "all" else "all"

        # Define charts for template
        context['charts'] = [
            {'id': 'visitsChart', 'title': 'Visits per Site'},
            {'id': 'progressChart', 'title': 'Mentorship Progress Over Time'},
            {'id': 'statusChart', 'title': 'Competence Completion Status'},
            {'id': 'compVisitChart', 'title': 'Competence per Visit'},
            {'id': 'compDiseaseChart', 'title': 'Competence per Disease'},
            {'id': 'compMenteeChart', 'title': 'Competence per Mentee'},
        ]

        # AJAX response for chart updates
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(context)

        return render(request, self.template_name, context)
