from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Visit, VisitDay, AssignedCompetence
from .forms import VisitForm, VisitDayForm, AssignedCompetenceForm, MentorGradeForm, MenteeSelfAssessmentForm
from django.core.exceptions import PermissionDenied

from django.contrib.auth import get_user_model

User = get_user_model()


# ------------------- Mixins -------------------
class RoleRequiredMixin(UserPassesTestMixin):
    role_required = None

    def test_func(self):
        if not self.role_required:
            return True
        user = self.request.user
        roles = self.role_required
        if isinstance(roles, str):
            roles = [roles]
        return user.groups.filter(name__in=roles).exists() or user.is_superuser


class AdminCheckMixin:
    """Adds is_admin to template context"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_admin'] = user.is_superuser or user.groups.filter(name='Admin').exists()
        return context


# ------------------- Views -------------------

def index(request):
    return render(request, 'mentorship/index.html')


class VisitListView(LoginRequiredMixin, AdminCheckMixin, ListView):
    model = Visit
    template_name = 'mentorship/visit_list.html'
    context_object_name = 'visits'
    ordering = ['-start_date']

class VisitDetailView(LoginRequiredMixin, AdminCheckMixin, DetailView):
    model = Visit
    template_name = 'mentorship/visit_detail.html'
    context_object_name = 'visit'

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
        context['is_mentor'] = self.request.user.id == visit.mentor.id

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

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Visit deleted successfully.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('mentorship:visit-list')


class VisitDayDetailView(LoginRequiredMixin, AdminCheckMixin, DetailView):
    model = VisitDay
    template_name = 'mentorship/visit_day_detail.html'
    context_object_name = 'visit_day'
    pk_url_kwarg = 'visit_day_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignments'] = self.object.assignments.all()
        context['is_mentor'] = self.request.user.id == self.object.visit.mentor.id
        return context


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
        if obj.assignments.exists():
            messages.error(request, "Cannot delete this Visit Day as it has assigned competencies.")
            return redirect('mentorship:visit-detail', pk=obj.visit.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "Visit Day deleted successfully.")
        return reverse_lazy('mentorship:visit-detail', kwargs={'pk': self.object.visit.pk})
    
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
        # Only the assigned mentor can grade
        if obj.visit_day.visit.mentor != request.user:
            return HttpResponseForbidden("You are not allowed to grade this assignment.")
        # Must wait for mentee self-assessment
        if not obj.is_self_assessed():
            return HttpResponseForbidden("Cannot grade before mentee self-assessment.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.is_completed = True
        obj.status = 'reviewed'
        obj.updated_by = self.request.user
        # set created_by if not already set
        if not obj.created_by:
            obj.created_by = self.request.user
        obj.save()

        # Update VisitDay and Visit statuses
        obj.visit_day.update_status()
        obj.visit_day.visit.update_status()

        messages.success(
            self.request,
            f"You have successfully graded {obj.mentee.get_full_name()}!"
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy(
            "mentorship:visit-day-detail",
            kwargs={'visit_day_id': self.object.visit_day.id}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assignment"] = self.object
        context['is_admin'] = (
            self.request.user.is_superuser or 
            self.request.user.groups.filter(name='Admin').exists()
        )
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
        return reverse('mentorship:visit-day-detail', kwargs={'visit_day_id': self.object.visit_day.id})


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

    def get_success_url(self):
        return reverse_lazy('mentorship:assign-competence', kwargs={'visit_day_id': self.object.visit_day.id})
