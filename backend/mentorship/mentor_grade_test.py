from mentorship.models import Visit, VisitDay, AssignedCompetence
from locations.models import Site
from clinical.models import Disease, Competence
from django.contrib.auth import get_user_model
from datetime import date, timedelta

User = get_user_model()

# 1️⃣ Pick a mentor and mentee
mentor = User.objects.filter(groups__name='Mentor').first()
mentee = User.objects.filter(groups__name='Mentee').first()

# 2️⃣ Pick a Site
site = Site.objects.first()

# 3️⃣ Pick a Disease and Competence
disease = Disease.objects.first()
competence = Competence.objects.first()

# 4️⃣ Create a Visit
visit = Visit.objects.create(
    site=site,
    mentor=mentor,
    start_date=date.today(),
    end_date=date.today() + timedelta(days=2),
    created_by=mentor,
)

# 5️⃣ Create VisitDays automatically via model method
visit.create_visit_days()

# Pick first VisitDay
visit_day = visit.days.first()

# 6️⃣ Create AssignedCompetence
assigned = AssignedCompetence.objects.create(
    visit_day=visit_day,
    mentee=mentee,
    disease=disease,
    competence=competence,
    assigned_by=mentor,
    status='assigned'
)

print("AssignedCompetence created:")
print(assigned.id, assigned.status, assigned.visit_day.date, assigned.mentee.username)

# 7️⃣ Apply mentee self-assessment
assigned.mentee_grade = 'Excellent'
assigned.mentee_remarks = 'I feel confident'
assigned.is_self_assessed = True
assigned.status = 'completed'
assigned.save()
assigned.visit_day.update_status()
assigned.visit_day.visit.update_status()

print("After mentee self-assessment:")
print(assigned.mentee_grade, assigned.mentee_remarks, assigned.status)

# 8️⃣ Apply mentor grade
assigned.mentor_grade = 'Good'
assigned.mentor_remarks = 'Well done'
assigned.status = 'reviewed'
assigned.is_completed = True
assigned.updated_by = mentor
assigned.save()
assigned.visit_day.update_status()
assigned.visit_day.visit.update_status()

print("After mentor grading:")
print(assigned.mentor_grade, assigned.mentor_remarks, assigned.status)
