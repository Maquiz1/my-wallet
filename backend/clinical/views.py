from django.views.generic import ListView, DetailView
from django.db.models import Count
from .models import Disease, Competence

class DiseaseListView(ListView):
    model = Disease
    template_name = "clinical/disease_list.html"
    context_object_name = "diseases"

    def get_queryset(self):
        return Disease.objects.annotate(
            competence_count=Count("competences", distinct=True)
        )


class DiseaseDetailView(DetailView):
    model = Disease
    template_name = 'clinical/disease_detail.html'
    context_object_name = 'disease'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add competences with assessment counts
        context["competences"] = self.object.competences.annotate(
            assessment_count=Count("assignedcompetence", distinct=True)
        )
        return context


class CompetenceDetailView(DetailView):
    model = Competence
    template_name = 'clinical/competence_detail.html'
    context_object_name = 'competence'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add assessment count
        context["assessment_count"] = self.object.assignedcompetence_set.count()
        return context
