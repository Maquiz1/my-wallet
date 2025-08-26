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
