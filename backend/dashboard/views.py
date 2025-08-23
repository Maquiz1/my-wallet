from locations.models import Country
from clinical.models import Disease
from mentorship.models import Visit
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    login_url = 'users:login'  # or '/users/login/' depending on your URL config

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        # Counts and recent visits
        context['country_count'] = Country.objects.count()
        context['disease_count'] = Disease.objects.count()
        context['visit_count'] = Visit.objects.count()
        context['recent_visits'] = Visit.objects.select_related('site', 'mentor').order_by('-start_date')[:5]

        # User object
        context['user'] = user

        # Precompute roles for template
        context['is_admin'] = user.is_superuser or user.groups.filter(name='Admin').exists()
        context['is_mentor'] = user.groups.filter(name='Mentor').exists()
        context['is_mentee'] = user.groups.filter(name='Mentee').exists()

        return context
