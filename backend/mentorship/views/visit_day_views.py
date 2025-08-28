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

class VisitDayDetailView(LoginRequiredMixin, DetailView):
    model = VisitDay
    template_name = 'mentorship/visit_day_detail.html'
    context_object_name = 'visit_day'
    slug_field = "slug"
    slug_url_kwarg = "slug"
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        visit_day = super().get_object(queryset)
        visit = visit_day.visit
        user = self.request.user

        # Reviewer / superuser
        if user.groups.filter(name='Reviewer').exists() or user.is_superuser:
            return visit_day
        # Admin (only visits they created)
        elif user.groups.filter(name='Admin').exists():
            if visit.created_by != user:
                raise PermissionDenied("You cannot view this visit day.")
            return visit_day
        # Mentor (only their visits)
        elif user.groups.filter(name='Mentor').exists():
            if visit.mentor != user:
                raise PermissionDenied("You cannot view this visit day.")
            return visit_day
        # Mentee (only assignments for themselves)
        elif user.groups.filter(name='Mentee').exists():
            if not visit_day.assignments.filter(mentee=user).exists():
                raise PermissionDenied("You cannot view this visit day.")
            return visit_day

        raise PermissionDenied("You cannot view this visit day.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visit_day = self.object
        user = self.request.user

        assignments = AssignedCompetence.objects.filter(
            visit_day=visit_day
        ).select_related('mentee', 'competence', 'disease')

        # Group assignments by mentee
        mentee_assignments = {}
        mentee_summary_forms = []

        for assignment in assignments:
            mentee = assignment.mentee
            # Only show mentee their own assignments
            if user.groups.filter(name='Mentee').exists() and mentee != user:
                continue

            if mentee not in mentee_assignments:
                mentee_assignments[mentee] = []
                form = VisitDaySummaryForm(
                    instance=visit_day,
                    visit_day=visit_day,
                    mentee=mentee,
                    prefix=str(mentee.id)
                )
                mentee_summary_forms.append((mentee, form))
            mentee_assignments[mentee].append(assignment)

        # Annotate self-assessment
        for mentee, assigns in mentee_assignments.items():
            mentee.has_self_assessed = any(a.is_self_assessed() for a in assigns)

        context['mentee_assignments'] = mentee_assignments
        context['mentee_summary_forms'] = mentee_summary_forms
        context['is_mentor'] = user == visit_day.visit.mentor
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        visit_day = self.object
        assignments = AssignedCompetence.objects.filter(
            visit_day=visit_day
        ).select_related('mentee')

        processed_mentees = set()
        response_data = {'success': False}

        for assignment in assignments:
            mentee = assignment.mentee
            # Only process form for the mentee making the request or for mentor
            if request.user.groups.filter(name='Mentee').exists() and mentee != request.user:
                continue

            if mentee.id not in processed_mentees:
                form = VisitDaySummaryForm(
                    request.POST,
                    instance=visit_day,
                    visit_day=visit_day,
                    mentee=mentee,
                    prefix=str(mentee.id)
                )
                processed_mentees.add(mentee.id)
                if form.is_valid():
                    form.save()
                    response_data['success'] = True
                else:
                    response_data['errors'] = form.errors
                    return JsonResponse(response_data)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(response_data)

        return redirect('mentorship:visit-day-detail', pk=visit_day.pk)
    
    
class VisitDayUpdateView(LoginRequiredMixin, AdminCheckMixin, UpdateView):
    model = VisitDay
    form_class = VisitDayForm
    template_name = 'mentorship/edit_visit_day.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['visit'] = self.object.visit
        return kwargs

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        self.object.update_status()  # Update status after editing
        self.object.visit.update_status()  # Update parent visit status
        return response

    def get_success_url(self):
        messages.success(self.request, "Visit Day updated successfully.")
        return reverse_lazy('mentorship:visit-detail', kwargs={'pk': self.object.visit.pk})


class VisitDayDeleteView(LoginRequiredMixin, AdminCheckMixin, DeleteView):
    model = VisitDay
    template_name = 'mentorship/delete_visit_day.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        # Rule 1: Cannot delete if parent Visit is locked
        if obj.visit.status in ['in_progress', 'completed', 'reviewed']:
            messages.error(request, "Cannot delete this Visit Day because the parent Visit is in progress, completed, or reviewed.")
            return redirect('mentorship:visit-detail', pk=obj.visit.pk)

        # Rule 2: Cannot delete if VisitDay has assignments
        if obj.assignments.exists():
            messages.error(request, "Cannot delete this Visit Day as it has assigned competencies.")
            return redirect('mentorship:visit-detail', pk=obj.visit.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "Visit Day deleted successfully.")
        return reverse_lazy('mentorship:visit-detail', kwargs={'pk': self.object.visit.pk})

class VisitDaySummaryUpdateView(UpdateView):
    model = VisitDay
    form_class = VisitDaySummaryForm
    template_name = "mentorship/visit_day_summary.html"
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        visit_day = super().get_object(queryset)
        visit = visit_day.visit
        user = self.request.user

        # Reviewer / superuser can access any visit day
        if user.groups.filter(name='Reviewer').exists() or user.is_superuser:
            return visit_day

        # Admin can access only visit days they created
        elif user.groups.filter(name='Admin').exists():
            if visit.created_by != user:
                raise PermissionDenied("You cannot edit this visit day.")
            return visit_day

        # Mentor can access only their visit days
        elif user.groups.filter(name='Mentor').exists():
            if visit.mentor != user:
                raise PermissionDenied("You cannot edit this visit day.")
            return visit_day

        # Mentee can access only if they have an assigned competence
        elif user.groups.filter(name='Mentee').exists():
            if not visit_day.assignments.filter(mentee=user).exists():
                raise PermissionDenied("You cannot edit this visit day.")
            return visit_day

        # Default deny
        raise PermissionDenied("You cannot edit this visit day.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        visit_day = self.get_object()

        # For simplicity, take the first mentee assigned to this visit day
        mentee = visit_day.assignments.first().mentee if visit_day.assignments.exists() else None
        kwargs.update({'visit_day': visit_day, 'mentee': mentee})
        return kwargs

    def get_success_url(self):
        return reverse_lazy('mentorship:visit-day-detail', kwargs={'pk': self.object.pk})