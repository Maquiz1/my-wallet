# mentorship/tests/test_forms.py
from django.test import TestCase
from mentorship.forms import VisitForm
from mentorship.models import Visit, Site
from django.contrib.auth.models import User

class VisitFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='mentor', password='pass')
        self.site = Site.objects.create(name='Site A')

    def test_valid_form(self):
        data = {
            'mentor': self.user.id,
            'site': self.site.id,
            'start_date': '2025-08-28',
            'end_date': '2025-08-29',
        }
        form = VisitForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_fields(self):
        form = VisitForm(data={})
        self.assertFalse(form.is_valid())
