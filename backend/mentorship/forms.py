# forms.py
from django import forms
from .models import VisitDay, Visit, AssignedCompetence
from django.contrib.auth import get_user_model

User = get_user_model()

GRADE_CHOICES = [
    ('', '---'),
    ('Excellent', 'Excellent'),
    ('Good', 'Good'),
    ('Fair', 'Fair'),
    ('Poor', 'Poor'),
]

class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['site', 'mentor', 'start_date', 'end_date']
        widgets = {
            'site': forms.Select(attrs={'class': 'form-select'}),
            'mentor': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Only show users in Mentor group for the mentor dropdown
        from django.contrib.auth.models import Group
        mentor_group = Group.objects.get(name='Mentor')
        self.fields['mentor'].queryset = mentor_group.user_set.all()

        # Only admins can assign a mentor; others see it hidden
        if user and not user.groups.filter(name='Admin').exists() and not user.is_superuser:
            self.fields['mentor'].widget = forms.HiddenInput()


class VisitDayForm(forms.ModelForm):
    class Meta:
        model = VisitDay
        fields = ['date']

    def __init__(self, *args, **kwargs):
        self.visit = kwargs.pop('visit', None)
        super().__init__(*args, **kwargs)

    def clean_date(self):
        date = self.cleaned_data['date']
        if VisitDay.objects.filter(visit=self.visit, date=date).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Another VisitDay already exists with this date.")
        return date


class MentorGradeForm(forms.ModelForm):
    class Meta:
        model = AssignedCompetence
        fields = ['mentor_grade', 'mentor_remarks']
        widgets = {
            'mentor_grade': forms.Select(choices=GRADE_CHOICES),
            'mentor_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Only the mentor assigned to the visit can see these fields
        if user and self.instance.visit_day.visit.mentor != user:
            for field in self.fields:
                self.fields[field].widget = forms.HiddenInput()


class MenteeSelfAssessmentForm(forms.ModelForm):
    class Meta:
        model = AssignedCompetence
        fields = ['mentee_grade', 'mentee_remarks']
        widgets = {
            'mentee_grade': forms.Select(choices=GRADE_CHOICES),
            'mentee_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Only the assigned mentee can see these fields
        if user and self.instance.mentee != user:
            for field in self.fields:
                self.fields[field].widget = forms.HiddenInput()

class AssignedCompetenceForm(forms.ModelForm):
    class Meta:
        model = AssignedCompetence
        fields = ['visit_day', 'mentee', 'disease', 'competence', 'mentor_remarks']
        widgets = {
            'visit_day': forms.HiddenInput(),  # Pre-fill from URL, hidden from mentor
            'mentee': forms.Select(attrs={'class': 'form-select'}),
            'disease': forms.Select(attrs={'class': 'form-select'}),
            'competence': forms.Select(attrs={'class': 'form-select'}),
            'mentor_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        visit_day = kwargs.pop('visit_day', None)  # Pass visit_day from view
        super().__init__(*args, **kwargs)

        # Only mentors can assign competencies
        if user and not user.groups.filter(name='Mentor').exists() and not user.is_superuser:
            for field in self.fields:
                self.fields[field].widget = forms.HiddenInput()

        # Pre-fill and hide visit_day
        if visit_day:
            self.fields['visit_day'].initial = visit_day

        # Only show mentees (optional: you can filter by mentor’s site)
        self.fields['mentee'].queryset = User.objects.filter(groups__name='Mentee')

        # Optional: you can filter competence by disease if needed
        # self.fields['competence'].queryset = Competence.objects.all()