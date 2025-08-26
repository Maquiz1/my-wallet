from django import forms
from .models import VisitDay, Visit, AssignedCompetence, MenteeGrade, MentorGrade
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


# -------------------------
# Visit & VisitDay Forms
# -------------------------
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

        try:
            mentor_group = Group.objects.get(name='Mentor')
            self.fields['mentor'].queryset = mentor_group.user_set.all()
        except Group.DoesNotExist:
            self.fields['mentor'].queryset = User.objects.none()

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


# -------------------------
# Mentor Grade Form
# -------------------------
class MentorGradeForm(forms.ModelForm):
    mentor_grade = forms.ModelChoiceField(
        queryset=MentorGrade.objects.all(),
        empty_label="--- Select Grade ---",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = AssignedCompetence
        fields = ['mentor_grade', 'mentor_remarks']
        widgets = {
            'mentor_remarks': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter mentor remarks'}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


# -------------------------
# Mentee Self-Assessment Form
# -------------------------
class MenteeSelfAssessmentForm(forms.ModelForm):
    mentee_grade = forms.ModelChoiceField(
        queryset=MenteeGrade.objects.all(),
        empty_label="--- Select Grade ---",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = AssignedCompetence
        fields = ['mentee_grade', 'mentee_remarks', 'pid']
        widgets = {
            'mentee_remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Patient ID'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and self.instance.mentee != user:
            for field in self.fields:
                self.fields[field].disabled = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_completed(user=instance.mentee)
        if commit:
            instance.save()
        return instance


# -------------------------
# Competence Assignment Form
# -------------------------
class AssignedCompetenceForm(forms.ModelForm):
    class Meta:
        model = AssignedCompetence
        fields = ['visit_day', 'mentee', 'disease', 'competence', 'mentor_description']
        widgets = {
            'visit_day': forms.HiddenInput(),
            'mentee': forms.Select(attrs={'class': 'form-select'}),
            'disease': forms.Select(attrs={'class': 'form-select'}),
            'competence': forms.Select(attrs={'class': 'form-select'}),
            'mentor_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description by mentor'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        visit_day = kwargs.pop('visit_day', None)
        super().__init__(*args, **kwargs)

        if user and not user.groups.filter(name='Mentor').exists() and not user.is_superuser:
            for field in self.fields:
                self.fields[field].disabled = True

        if visit_day:
            self.fields['visit_day'].initial = visit_day

        self.fields['mentee'].queryset = User.objects.filter(groups__name='Mentee')
        self.fields['competence'].label_from_instance = lambda obj: f"{obj.name} - {obj.description}" if obj.description else obj.name

        if self.instance.pk and self.instance.is_self_assessed():
            for field_name in ['mentee', 'disease', 'competence']:
                self.fields[field_name].disabled = True


# -------------------------
# VisitDay Summary Form
# -------------------------
class VisitDaySummaryForm(forms.ModelForm):
    strengths = forms.ModelMultipleChoiceField(
        queryset=AssignedCompetence.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="List 3 main skills/areas of competency of the Mentee"
    )
    improvements = forms.ModelMultipleChoiceField(
        queryset=AssignedCompetence.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="List 3 skills/areas that require additional mentoring or training"
    )

    class Meta:
        model = VisitDay
        fields = ['strengths', 'improvements', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional comments'}),
        }

    def __init__(self, *args, **kwargs):
        visit_day = kwargs.pop('visit_day', None)
        mentee = kwargs.pop('mentee', None)
        super().__init__(*args, **kwargs)
        if visit_day and mentee:
            queryset = AssignedCompetence.objects.filter(visit_day=visit_day, mentee=mentee)
            self.fields['strengths'].queryset = queryset
            self.fields['improvements'].queryset = queryset

    def clean_strengths(self):
        data = self.cleaned_data['strengths']
        if len(data) > 3:
            raise forms.ValidationError("You can select up to 3 strengths only.")
        return data

    def clean_improvements(self):
        data = self.cleaned_data['improvements']
        if len(data) > 3:
            raise forms.ValidationError("You can select up to 3 areas for improvement only.")
        return data
