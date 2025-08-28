# mentorship/tests/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User, Group
from mentorship.models import Visit, VisitDay, AssignedCompetence
from clinical.models import Disease, Competence, Site
from datetime import date

class VisitModelTest(TestCase):
    def setUp(self):
        self.mentor_group = Group.objects.create(name='Mentor')
        self.mentor = User.objects.create_user(username='mentor1', password='pass')
        self.mentor.groups.add(self.mentor_group)

        self.site = Site.objects.create(name='Site A')
        self.disease = Disease.objects.create(name='Diabetes')

        self.visit = Visit.objects.create(
            mentor=self.mentor,
            site=self.site,
            start_date=date.today(),
            end_date=date.today()
        )

    def test_visit_str(self):
        self.assertEqual(str(self.visit), f"Visit {self.visit.pk} by {self.mentor.username}")

    def test_visit_has_site(self):
        self.assertEqual(self.visit.site.name, 'Site A')
