# mentorship/tests/test_views.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group

class VisitListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='pass')
        self.admin_group = Group.objects.create(name='Admin')
        self.user.groups.add(self.admin_group)
        self.client.login(username='admin', password='pass')

    def test_visit_list_status_code(self):
        url = reverse('mentorship:visit-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mentorship/visit_list.html')

    def test_visit_list_no_visits(self):
        url = reverse('mentorship:visit-list')
        response = self.client.get(url)
        self.assertContains(response, "No records found")
