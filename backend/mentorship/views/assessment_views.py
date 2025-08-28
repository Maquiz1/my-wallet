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



class MentorGradeView(UpdateView):
    model = AssignedCompetence
    form_class = MentorGradeForm
    template_name = "mentorship/mentor_grade.html"
    context_object_name = 'assignment'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        
        # Ensure visit_day and visit exist
        if not obj.visit_day or not obj.visit_day.visit:
            return HttpResponseForbidden("Invalid assignment or visit day.")

        # Only the assigned mentor can grade
        if obj.visit_day.visit.mentor != request.user:
            return HttpResponseForbidden("You are not allowed to grade this assignment.")

        # Ensure mentee has self-assessed
        if not obj.is_self_assessed():
            return HttpResponseForbidden("Cannot grade before mentee self-assessment.")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)

        # Set completed/reviewed status
        obj.is_completed = True
        obj.status = 'reviewed'
        obj.updated_by = self.request.user
        if not obj.created_by:
            obj.created_by = self.request.user
        obj.save()

        # Update visit_day and visit statuses
        obj.visit_day.update_status()
        obj.visit_day.visit.update_status()

        messages.success(
            self.request,
            f"You have successfully graded {obj.mentee.get_full_name()}!"
        )
        return redirect(self.get_success_url())

    # def get_success_url(self):
    #     return reverse_lazy(
    #         "mentorship:visit-day-detail",
    #         kwargs={'visit_day_id': self.object.visit_day.id}
    #     )
    def get_success_url(self):
        return reverse_lazy('mentorship:visit-day-detail', kwargs={'pk': self.object.visit_day.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assignment"] = self.object
        context['is_admin'] = self.request.user.is_superuser or self.request.user.groups.filter(name='Admin').exists()
        return context

class MenteeSelfAssessmentView(LoginRequiredMixin, AdminCheckMixin, RoleRequiredMixin, UpdateView):
    model = AssignedCompetence
    form_class = MenteeSelfAssessmentForm
    template_name = 'mentorship/mentee_self_assess.html'
    context_object_name = 'assignment'
    role_required = 'Mentee'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.mentee != request.user:
            return HttpResponseForbidden("Not allowed to assess this competence.")
        if obj.mentor_grade:
            return HttpResponseForbidden("Cannot self-assess after mentor graded.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.status = 'completed'  # status transition
        form.instance.is_self_assessed = True
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        # Update VisitDay and Visit
        form.instance.visit_day.update_status()
        form.instance.visit_day.visit.update_status()
        return response

    def get_success_url(self):
        return reverse_lazy('mentorship:visit-day-detail', kwargs={'pk': self.object.visit_day.id})


# Assessments List
class AssignedCompetenceListView(LoginRequiredMixin, ListView):
    model = AssignedCompetence
    template_name = 'mentorship/assessments/assigned_competence_list.html'
    context_object_name = 'assignments'
    ordering = ['-created_at']
    
class AllAssessmentsListView(LoginRequiredMixin, AdminCheckMixin, RoleRequiredMixin, ListView):
    model = AssignedCompetence
    template_name = 'mentorship/all_assessments.html'
    context_object_name = 'assessments'
    ordering = ['-visit_day__date']
    role_required = ['Reviewer', 'Admin']

    def get_queryset(self):
        return AssignedCompetence.objects.all()
    
class AssignedCompetenceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = AssignedCompetence
    template_name = 'mentorship/assigned_competence_confirm_delete.html'

    def test_func(self):
        assignment = self.get_object()
        # Only allow Mentor who assigned it or Admin
        return self.request.user == assignment.assigned_by or self.request.user.is_superuser

    # def get_success_url(self):
    #     return reverse_lazy('mentorship:assign-competence', kwargs={'visit_day_id': self.object.visit_day.id})
    
    def get_success_url(self):
        return reverse_lazy('mentorship:assign-competence', kwargs={'pk': self.object.visit_day.id})
