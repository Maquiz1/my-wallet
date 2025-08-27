from clinical.models import Disease,Competence
from mentorship.models import Visit, VisitDay, AssignedCompetence
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView,TemplateView
from datetime import date, timedelta
from django.db.models import Count
from django.db.models import Q



class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Total visits
        total_visits = Visit.objects.count()
        context['total_visits'] = total_visits

        # Completed visits
        # completed_count = Visit.objects.filter(status="completed").count()
        # reviewed_count = Visit.objects.filter(status="reviewed").count()
        # total_finished = completed_count + reviewed_count
        
        completed_visits = Visit.objects.filter(
            Q(status="completed") | Q(status="reviewed")
        ).count()
        context['completed_visits'] = completed_visits

        # Progress percentage
        if total_visits > 0:
            context['visits_percentage'] = int((completed_visits / total_visits) * 100)
        else:
            context['visits_percentage'] = 0
            
        # Total visit days
        visitday_count = VisitDay.objects.count()
        context['visitday_count'] = visitday_count

        # Total Assessment Done
        assignment_count = AssignedCompetence.objects.count()
        context['assignment_count'] = assignment_count
        
        # Total number of competences from Competence model
        total_competences = Competence.objects.aggregate(total=Count('id'))['total']  # replace Disease if needed
        context['total_competences'] = total_competences

        # Count unique competences that have been assessed in AssignedCompetence
        assessed_competences_qs = AssignedCompetence.objects.filter(
            status__in=['completed', 'reviewed']
        ).values_list('competence', flat=True).distinct()  # distinct ensures no duplicates
        context['assessed_competences'] = assessed_competences_qs.count()

        # Compute percentage
        if total_competences > 0:
            context['assessed_percentage'] = int((context['assessed_competences'] / total_competences) * 100)
        else:
            context['assessed_percentage'] = 0



        # Roles
        context['is_admin'] = user.is_superuser or user.groups.filter(name='Admin').exists()
        context['is_mentor'] = user.groups.filter(name='Mentor').exists()
        context['is_mentee'] = user.groups.filter(name='Mentee').exists()

        # Visits per site (for chart)
        visits_per_site = Visit.objects.values('site__name').annotate(count=Count('id'))
        context['visits_chart_labels'] = [v['site__name'] for v in visits_per_site]
        context['visits_chart_data'] = [v['count'] for v in visits_per_site]

        # Recent activity
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

        # Recent visits
        context['recent_visits'] = Visit.objects.select_related('site', 'mentor', 'created_by', 'updated_by') \
            .order_by('-created_at')[:5]

        # Recent activity
        context['recent_activity'] = AssignedCompetence.objects.select_related('mentee','assigned_by', 'competence', 'visit_day') \
            .order_by('-created_at')[:5]
            
        context['user'] = user
        return context
