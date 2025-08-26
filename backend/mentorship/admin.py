from django.contrib import admin
from .models import Mentorship, Visit, VisitDay, AssignedCompetence, MenteeGrade, MentorGrade

admin.site.register(Mentorship)  # Assuming you have a Mentorship model to register
admin.site.register(Visit)  # Assuming you have a Visit model to register
admin.site.register(VisitDay)  # Assuming you have a VisitDay model to register
admin.site.register(AssignedCompetence)  # Assuming you have a AssignedCompetence model to register
admin.site.register(MenteeGrade)  # Register MenteeGrade model
admin.site.register(MentorGrade)  # Register MentorGrade model

