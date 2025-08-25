from django.core.management.base import BaseCommand
from mentorship.models import Visit, VisitDay, AssignedCompetence
from locations.models import Site
from clinical.models import Disease, Competence
from django.contrib.auth import get_user_model
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = "Create a test Visit, VisitDay, and AssignedCompetence with mentee and mentor grading"

    def handle(self, *args, **kwargs):
        # 1️⃣ Pick users
        mentor = User.objects.filter(groups__name='Mentor').first()
        mentee = User.objects.filter(groups__name='Mentee').first()
        if not mentor or not mentee:
            self.stdout.write(self.style.ERROR("No Mentor or Mentee found."))
            return

        # 2️⃣ Pick Site, Disease, Competence
        site = Site.objects.first()
        disease = Disease.objects.first()
        competence = Competence.objects.first()
        if not site or not disease or not competence:
            self.stdout.write(self.style.ERROR("Missing Site, Disease, or Competence."))
            return

        # 3️⃣ Create Visit
        visit = Visit.objects.create(
            site=site,
            mentor=mentor,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
            created_by=mentor,
        )
        visit.create_visit_days()
        visit_day = visit.days.first()

        # 4️⃣ Create AssignedCompetence
        assigned = AssignedCompetence.objects.create(
            visit_day=visit_day,
            mentee=mentee,
            disease=disease,
            competence=competence,
            assigned_by=mentor,
            status='assigned'
        )

        self.stdout.write(self.style.SUCCESS(
            f"AssignedCompetence created: ID={assigned.id}, Status={assigned.status}, Date={visit_day.date}, Mentee={mentee.username}"
        ))

        # 5️⃣ Mentee self-assessment
        assigned.mentee_grade = 'Excellent'
        assigned.mentee_remarks = 'I feel confident'
        assigned.is_self_assessed = True
        assigned.status = 'completed'
        assigned.save()
        assigned.visit_day.update_status()
        assigned.visit_day.visit.update_status()

        self.stdout.write(self.style.SUCCESS(
            f"After mentee self-assessment: Grade={assigned.mentee_grade}, Remarks={assigned.mentee_remarks}, Status={assigned.status}"
        ))

        # 6️⃣ Mentor grading
        assigned.mentor_grade = 'Good'
        assigned.mentor_remarks = 'Well done'
        assigned.status = 'reviewed'
        assigned.is_completed = True
        assigned.updated_by = mentor
        assigned.save()
        assigned.visit_day.update_status()
        assigned.visit_day.visit.update_status()

        self.stdout.write(self.style.SUCCESS(
            f"After mentor grading: Grade={assigned.mentor_grade}, Remarks={assigned.mentor_remarks}, Status={assigned.status}"
        ))
