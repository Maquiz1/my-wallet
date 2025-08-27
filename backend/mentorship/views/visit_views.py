from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView,TemplateView
from django.contrib import messages
from ..models import Visit
from ..forms import VisitForm
from .mixins import AdminCheckMixin, RoleRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class IndexView(TemplateView):
    template_name = "mentorship/index.html"


class VisitListView(LoginRequiredMixin, AdminCheckMixin, ListView):
    model = Visit
    template_name = 'mentorship/visit_list.html'
    context_object_name = 'visits'
    ordering = ['-start_date']

    def get_queryset(self):
        user = self.request.user

        # Reviewer sees all visits
        if user.groups.filter(name='Reviewer').exists() or user.is_superuser:
            return Visit.objects.all().order_by('-start_date')

        # Admin sees visits they created (for any site they selected)
        elif user.groups.filter(name='Admin').exists():
            return Visit.objects.filter(created_by=user).order_by('-start_date')

        # Mentor sees visits where they are the mentor
        elif user.groups.filter(name='Mentor').exists():
            return Visit.objects.filter(mentor=user).order_by('-start_date')

        # Mentee sees visits where they have assigned competences
        elif user.groups.filter(name='Mentee').exists():
            return Visit.objects.filter(days__assignments__mentee=user).distinct().order_by('-start_date')

        # Otherwise, no visits
        return Visit.objects.none()


class VisitDetailView(LoginRequiredMixin, AdminCheckMixin, DetailView):
    model = Visit
    template_name = 'mentorship/visit_detail.html'
    context_object_name = 'visit'

    def get_object(self, queryset=None):
        user = self.request.user
        visit = super().get_object(queryset)

        # Reviewer / superuser can view any visit
        if user.groups.filter(name='Reviewer').exists() or user.is_superuser:
            return visit

        # Admin can only view visits they created
        elif user.groups.filter(name='Admin').exists():
            if visit.created_by != user:
                raise PermissionDenied("You cannot view this visit.")
            return visit

        # Mentor can only view visits assigned to them
        elif user.groups.filter(name='Mentor').exists():
            if visit.mentor != user:
                raise PermissionDenied("You cannot view this visit.")
            return visit

        # Mentee can only view visits where they have assigned competences
        elif user.groups.filter(name='Mentee').exists():
            if not visit.days.filter(assignments__mentee=user).exists():
                raise PermissionDenied("You cannot view this visit.")
            return visit

        # Default: deny access
        raise PermissionDenied("You cannot view this visit.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visit = self.object

        # Prepare visit days with statuses
        context['visit_days'] = visit.days.all()  # already ordered by date via Meta

        # Group assignments per day
        visit_days_with_assignments = []
        for day in context['visit_days']:
            assignments = day.assignments.all()
            visit_days_with_assignments.append({
                'day': day,
                'assignments': assignments,
                'status': day.status,  # updated by model method
            })
        context['visit_days_with_assignments'] = visit_days_with_assignments

        # Add mentor check for template
        context['is_mentor'] = self.request.user == visit.mentor

        return context


class VisitCreateView(LoginRequiredMixin, AdminCheckMixin, RoleRequiredMixin, CreateView):
    model = Visit
    form_class = VisitForm
    template_name = 'mentorship/visit_form.html'
    role_required = 'Admin'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Visit created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mentorship:visit-detail', kwargs={'pk': self.object.pk})


class VisitDeleteView(LoginRequiredMixin, AdminCheckMixin, DeleteView):
    model = Visit
    template_name = 'mentorship/visit_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        visit = self.get_object()
        if visit.status in ['in_progress', 'completed', 'reviewed']:
            messages.error(request, "This visit cannot be deleted once it is in progress, completed, or reviewed.")
            return redirect('mentorship:visit-detail', pk=visit.pk)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Visit deleted successfully.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('mentorship:visit-list')