from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import timedelta
from clinical.models import Disease, Competence
from locations.models import Site
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

GRADE_CHOICES = [
    ('', '---'),
    ('Excellent', 'Excellent'),
    ('Good', 'Good'),
    ('Fair', 'Fair'),
    ('Poor', 'Poor'),
]

# class Status(models.Model):
#     name = models.CharField(max_length=50, unique=True)  # e.g., Assigned, Completed, Reviewed
#     description = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.name

class Mentorship(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="mentorships_created"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="mentorships_updated"
    )

    def __str__(self):
        return f"Mentorship {self.id}"


class Visit(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("reviewed", "Reviewed"),
    ]

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mentorships")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="visits_created"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="visits_updated"
    )

    def __str__(self):
        return f"Visit by {self.mentor} to {self.site} ({self.start_date} to {self.end_date})"

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be earlier than start date.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)  # Safe: don't call update_status here
        self.create_visit_days()       # Create missing VisitDays if any

    def create_visit_days(self):
        total_days = (self.end_date - self.start_date).days + 1
        new_days = []
        for i in range(total_days):
            day = self.start_date + timedelta(days=i)
            if not VisitDay.objects.filter(visit=self, date=day).exists():
                new_days.append(VisitDay(visit=self, date=day))
        VisitDay.objects.bulk_create(new_days)

    def update_status(self):
        """
        Updates Visit status based on associated VisitDays.
        Avoids recursion by calling super().save() directly.
        """
        days = self.days.all()
        if not days.exists():
            new_status = "pending"
        elif all(day.status == "reviewed" for day in days):
            new_status = "reviewed"
        elif all(day.status == "completed" for day in days):
            new_status = "completed"
        elif any(day.status in ["in_progress", "completed", "reviewed"] for day in days):
            new_status = "in_progress"
        else:
            new_status = "pending"

        if self.status != new_status:
            self.status = new_status
            super().save(update_fields=["status", "updated_at"])

    def update_status_without_recursion(self):
        """
        Helper to update status from VisitDay without triggering recursive calls.
        """
        self.update_status()


class VisitDay(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("reviewed", "Reviewed"),
    ]

    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name="days")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="visitdays_created"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="visitdays_updated"
    )

    class Meta:
        unique_together = ("visit", "date")
        ordering = ["date"]

    def __str__(self):
        return f"{self.date} for {self.visit}"

    def update_status(self):
        """
        Update VisitDay status based on assigned competencies.
        Avoid recursion by calling super().save() and Visit.update_status_without_recursion()
        """
        assignments = self.assignments.all()
        if not assignments.exists():
            new_status = "pending"
        elif all(a.status == "reviewed" for a in assignments):
            new_status = "reviewed"
        elif all(a.status == "completed" for a in assignments):
            new_status = "completed"
        elif any(a.status in ["assigned", "completed", "reviewed"] for a in assignments):
            new_status = "in_progress"
        else:
            new_status = "pending"

        if self.status != new_status:
            self.status = new_status
            super().save(update_fields=["status", "updated_at"])
            self.visit.update_status_without_recursion()


class AssignedCompetence(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("completed", "Completed"),
        ("reviewed", "Reviewed"),
    ]

    visit_day = models.ForeignKey(VisitDay, on_delete=models.CASCADE, related_name="assignments")
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_competencies")
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    competence = models.ForeignKey(Competence, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="competences_assigned"
    )

    # NEW FIELD for participant/patient ID
    pid = models.CharField(max_length=50, blank=True, null=True, help_text="Patient/Participant ID")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    is_completed = models.BooleanField(default=False)

    mentee_grade = models.CharField(max_length=20, blank=True, null=True)
    mentee_remarks = models.TextField(blank=True, null=True)
    mentor_grade = models.CharField(max_length=20, blank=True, null=True)
    mentor_remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assignedcompetence_created"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assignedcompetence_updated"
    )

    class Meta:
        unique_together = ("visit_day", "mentee", "competence")

    def clean(self):
        if self.visit_day.visit.mentor == self.mentee:
            raise ValidationError("Mentor cannot assign competencies to themselves.")

        valid_grades = ["Excellent", "Good", "Fair", "Poor"]
        if self.mentor_grade and self.mentor_grade not in valid_grades:
            raise ValidationError(f"Mentor grade must be one of: {', '.join(valid_grades)}.")

        if self.mentee_grade and self.mentee_grade not in valid_grades:
            raise ValidationError(f"Mentee grade must be one of: {', '.join(valid_grades)}.")

    def __str__(self):
        return f"{self.mentee} - {self.competence} ({self.status}) [PID: {self.pid}]"

    # Status transition helpers
    def set_assigned(self, user=None):
        self.status = "assigned"
        self.updated_by = user
        super().save(update_fields=["status", "updated_by", "updated_at"])
        self.visit_day.update_status()

    def set_completed(self, user=None):
        self.status = "completed"
        self.is_completed = True
        self.updated_by = user
        super().save(update_fields=["status", "is_completed", "updated_by", "updated_at"])
        self.visit_day.update_status()

    def set_reviewed(self, user=None):
        self.status = "reviewed"
        self.updated_by = user
        super().save(update_fields=["status", "updated_by", "updated_at"])
        self.visit_day.update_status()

    def is_mentor_graded(self):
        return bool(self.mentor_grade)

    def is_self_assessed(self):
        return bool(self.mentee_grade)

