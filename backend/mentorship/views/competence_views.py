from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from urllib3 import request
from ..models import Visit, VisitDay, AssignedCompetence
from ..forms import VisitForm, VisitDayForm, AssignedCompetenceForm, MentorGradeForm, MenteeSelfAssessmentForm,VisitDaySummaryForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from .mixins import AdminCheckMixin, RoleRequiredMixin

from django.contrib.auth import get_user_model

User = get_user_model()

class AssignCompetenceView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = AssignedCompetence
    form_class = AssignedCompetenceForm
    template_name = 'mentorship/assign_competence.html'
    role_required = 'Mentor'

    def get_initial(self):
        initial = super().get_initial()
        self.visit_day = VisitDay.objects.get(pk=self.kwargs.get('visit_day_id'))
        initial['visit_day'] = self.visit_day
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['visit_day'] = self.visit_day
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['visit_day'] = self.visit_day

        # Show existing assignments
        assignments = AssignedCompetence.objects.filter(visit_day=self.visit_day)
        context['assignments'] = assignments

        # Add flags for template
        context['is_mentor'] = self.request.user == self.visit_day.visit.mentor
        context['is_admin'] = self.request.user.is_superuser or self.request.user.groups.filter(name='Admin').exists()

        return context

    def form_valid(self, form):
        form.instance.assigned_by = self.request.user
        form.instance.status = 'assigned'
        response = super().form_valid(form)
        # Update VisitDay and Visit statuses
        self.visit_day.update_status()
        self.visit_day.visit.update_status()
        messages.success(
            self.request,
            f"Competence {form.instance.competence} assigned to {form.instance.mentee.get_full_name()}!"
        )
        return response

    def get_success_url(self):
        return reverse('mentorship:assign-competence', kwargs={'visit_day_id': self.visit_day.id})

    # def get_success_url(self):
    #     return reverse_lazy('mentorship:assign-competence', kwargs={'pk': self.object.visit_day.id})


class AssignedCompetenceDetailView(LoginRequiredMixin, AdminCheckMixin, DetailView):
    model = AssignedCompetence
    template_name = 'mentorship/assigned_competence_view.html'
    context_object_name = 'assignment'


class AssignedCompetenceUpdateView(LoginRequiredMixin, AdminCheckMixin, UpdateView):
    model = AssignedCompetence
    form_class = AssignedCompetenceForm
    template_name = 'mentorship/assigned_competence_form.html'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        form.instance.visit_day.update_status()
        form.instance.visit_day.visit.update_status()
        return response

    def get_success_url(self):
        return reverse('mentorship:visit-day-detail', kwargs={'visit_day_id': self.object.visit_day.id})
    