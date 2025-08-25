from django.contrib import admin
from .models import Disease, Competence

class CompetenceInline(admin.TabularInline):
    model = Competence
    extra = 1  # Number of empty forms to display

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [CompetenceInline]

@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    list_display = ['name','description', 'disease']
