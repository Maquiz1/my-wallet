from django.db.models import Count
from datetime import timedelta, date
from mentorship.models import Visit, AssignedCompetence
from locations.models import Country
from clinical.models import Disease
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Counts
        context['country_count'] = Country.objects.count()
        context['disease_count'] = Disease.objects.count()
        context['visit_count'] = Visit.objects.count()
        context['recent_visits'] = Visit.objects.select_related('site', 'mentor').order_by('-start_date')[:5]

        # Roles
        context['is_admin'] = user.is_superuser or user.groups.filter(name='Admin').exists()
        context['is_mentor'] = user.groups.filter(name='Mentor').exists()
        context['is_mentee'] = user.groups.filter(name='Mentee').exists()

        # Visits per site (for chart)
        visits_per_site = Visit.objects.values('site__name').annotate(count=Count('id'))
        context['visits_chart_labels'] = [v['site__name'] for v in visits_per_site]
        context['visits_chart_data'] = [v['count'] for v in visits_per_site]

        # Mentee submissions last 7 days
        last_7_days = date.today() - timedelta(days=6)
        submissions = (
            AssignedCompetence.objects.filter(created_at__date__gte=last_7_days)
            .extra({'day': "date(created_at)"})
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        context['activity_chart_labels'] = [(last_7_days + timedelta(days=i)).strftime("%a") for i in range(7)]
        counts_dict = {s['day'].strftime("%a"): s['count'] for s in submissions}
        context['activity_chart_data'] = [counts_dict.get((last_7_days + timedelta(days=i)).strftime("%a"), 0) for i in range(7)]

        # Recent activity (latest 5 assignments)
        context['recent_activity'] = AssignedCompetence.objects.select_related('mentee', 'competence', 'visit_day') \
            .order_by('-created_at')[:5]

        context['user'] = user
        return context
