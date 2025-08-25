from django.views.generic import ListView, DetailView
from .models import Disease, Competence
from django.db.models import Count

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

class CompetenceDetailView(DetailView):
    model = Competence
    template_name = 'clinical/competence_detail.html'
    context_object_name = 'competence'
