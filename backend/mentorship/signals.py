# mentorship/signals.py
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    if sender.name == "mentorship":  # only when your app is migrated
        for group_name in ["Mentor", "Mentee", "Reviewer", "Admin"]:
            Group.objects.get_or_create(name=group_name)
