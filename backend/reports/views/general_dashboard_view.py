from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from reports.services import get_dashboard_context
from clinical.models import Disease

class GeneralDashboardReportView(View):
    template_name = "reports/general_dashboard_report.html"

    def get(self, request, *args, **kwargs):
        disease_id = request.GET.get("disease")
        user_filter = request.GET.get("user_filter", "all")

        context = get_dashboard_context()
        context['user_filter'] = user_filter
        context['selected_disease'] = int(disease_id) if disease_id and disease_id != "all" else None
        context['diseases'] = Disease.objects.all()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(context)

        return render(request, self.template_name, context)
