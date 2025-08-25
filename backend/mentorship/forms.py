# forms.py
from django import forms
from .models import VisitDay, Visit, AssignedCompetence
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django import forms
from .models import AssignedCompetence, GRADE_CHOICES

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

        # Show only Mentors
        try:
            mentor_group = Group.objects.get(name='Mentor')
            self.fields['mentor'].queryset = mentor_group.user_set.all()
        except Group.DoesNotExist:
            self.fields['mentor'].queryset = User.objects.none()

        # Only Admin can assign mentors
        if user and not user.groups.filter(name='Admin').exists() and not user.is_superuser:
            self.fields['mentor'].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super().save(commit=False)
        # status handled in model logic: default = pending
        if commit:
            instance.save()
        return instance


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

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Status auto-handled in model: pending → in-progress → completed → reviewed
        if commit:
            instance.save()
        return instance

class MentorGradeForm(forms.ModelForm):
    class Meta:
        model = AssignedCompetence
        fields = ['mentor_grade', 'mentor_remarks']
        widgets = {
            'mentor_grade': forms.Select(choices=GRADE_CHOICES, attrs={'class': 'form-select'}),
            'mentor_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Disable editing if already graded
        if self.instance.pk and self.instance.mentor_grade:
            for field in self.fields:
                self.fields[field].widget.attrs['readonly'] = True


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
        # Hide if not the mentee
        if user and self.instance.mentee != user:
            for field in self.fields:
                self.fields[field].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super().save(commit=False)
        # After self-assessment → update statuses
        if commit:
            instance.save()
            instance.visit_day.update_status()
            instance.visit_day.visit.update_status()
        return instance

class AssignedCompetenceForm(forms.ModelForm):
    class Meta:
        model = AssignedCompetence
        fields = ['visit_day', 'mentee', 'disease', 'competence', 'mentor_remarks']
        widgets = {
            'visit_day': forms.HiddenInput(),  # Pre-filled
            'mentee': forms.Select(attrs={'class': 'form-select'}),
            'disease': forms.Select(attrs={'class': 'form-select'}),
            'competence': forms.Select(attrs={'class': 'form-select'}),
            'mentor_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        visit_day = kwargs.pop('visit_day', None)
        super().__init__(*args, **kwargs)

        # Only mentors can assign
        if user and not user.groups.filter(name='Mentor').exists() and not user.is_superuser:
            for field in self.fields:
                self.fields[field].widget = forms.HiddenInput()

        if visit_day:
            self.fields['visit_day'].initial = visit_day

        self.fields['mentee'].queryset = User.objects.filter(groups__name='Mentee')

        # Disable fields **only if the instance exists and self-assessed**
        if self.instance.pk and self.instance.is_self_assessed:
            for field_name in ['mentee', 'disease', 'competence']:
                self.fields[field_name].disabled = True
