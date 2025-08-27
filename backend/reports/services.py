from mentorship.models import Visit, VisitDay, AssignedCompetence
from django.db.models import Count, Q
import calendar  # For month names

def get_visits_per_site():
    qs = Visit.objects.values('site__name').annotate(total=Count('id'))
    return {v['site__name']: v['total'] for v in qs}

def get_progress_over_time():
    qs = VisitDay.objects.values('date__month').annotate(total=Count('id')).order_by('date__month')
    labels = [calendar.month_abbr[v['date__month']] for v in qs]  # 'Jan', 'Feb', etc.
    data = [v['total'] for v in qs]
    return labels, data

def get_competence_status():
    qs = AssignedCompetence.objects.aggregate(
        completed=Count('id', filter=Q(is_completed=True)),
        pending=Count('id', filter=Q(is_completed=False) & Q(mentee_grade__isnull=False)),
        in_progress=Count('id', filter=Q(mentee_grade__isnull=True))
    )
    return {
        'Completed': qs['completed'],
        'Pending': qs['pending'],
        'In Progress': qs['in_progress']
    }

def get_competence_per_visit():
    qs = AssignedCompetence.objects.values('visit_day__visit__id', 'visit_day__visit__site__name').annotate(total=Count('id'))
    labels = [f"{v['visit_day__visit__site__name']} (Visit {v['visit_day__visit__id']})" for v in qs]
    data = [v['total'] for v in qs]
    return labels, data

def get_competence_per_disease():
    qs = AssignedCompetence.objects.values('competence__disease__name').annotate(total=Count('id'))
    labels = [v['competence__disease__name'] for v in qs]
    data = [v['total'] for v in qs]
    return labels, data

def get_competence_per_mentee():
    qs = AssignedCompetence.objects.values('mentee__username').annotate(total=Count('id'))
    labels = [v['mentee__username'] for v in qs]
    data = [v['total'] for v in qs]
    return labels, data

def get_dashboard_context():
    visits_per_site = get_visits_per_site()
    progress_labels, progress_data = get_progress_over_time()
    competence_status = get_competence_status()
    comp_visit_labels, comp_visit_data = get_competence_per_visit()
    comp_disease_labels, comp_disease_data = get_competence_per_disease()
    comp_mentee_labels, comp_mentee_data = get_competence_per_mentee()

    # Return Python lists, not JSON strings
    return {
        'visits_labels': list(visits_per_site.keys()),
        'visits_data': list(visits_per_site.values()),
        'progress_labels': progress_labels,
        'progress_data': progress_data,
        'status_labels': list(competence_status.keys()),
        'status_data': list(competence_status.values()),
        'comp_visit_labels': comp_visit_labels,
        'comp_visit_data': comp_visit_data,
        'comp_disease_labels': comp_disease_labels,
        'comp_disease_data': comp_disease_data,
        'comp_mentee_labels': comp_mentee_labels,
        'comp_mentee_data': comp_mentee_data,
    }
