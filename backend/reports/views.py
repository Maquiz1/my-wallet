from django.shortcuts import render
from mentorship.models import Visit, VisitDay, AssignedCompetence
from django.db.models import Count, Q
import json

def dashboard_report(request):
    # Visits per Site
    visits_qs = Visit.objects.values('site__name').annotate(total=Count('id'))
    visits_per_site = {v['site__name']: v['total'] for v in visits_qs}

    # Mentorship Progress Over Time (monthly)
    progress_qs = VisitDay.objects.values('date__month').annotate(total=Count('id')).order_by('date__month')
    progress_labels = [v['date__month'] for v in progress_qs]
    progress_data = [v['total'] for v in progress_qs]

    # Competence Completion Status
    status_qs = AssignedCompetence.objects.aggregate(
        completed=Count('id', filter=Q(is_completed=True)),
        pending=Count('id', filter=Q(is_completed=False, is_self_assessed=True)),
        in_progress=Count('id', filter=Q(is_self_assessed=False))
    )
    competence_status = {
        'Completed': status_qs['completed'],
        'Pending': status_qs['pending'],
        'In Progress': status_qs['in_progress']
    }

    # Competence per Visit
    comp_visit_qs = AssignedCompetence.objects.values('visit_day__visit__id', 'visit_day__visit__site__name').annotate(total=Count('id'))
    comp_per_visit_labels = [f"{v['visit_day__visit__site__name']} (Visit {v['visit_day__visit__id']})" for v in comp_visit_qs]
    comp_per_visit_data = [v['total'] for v in comp_visit_qs]

    # Competence per Disease
    comp_disease_qs = AssignedCompetence.objects.values('disease__name').annotate(total=Count('id'))
    comp_per_disease_labels = [v['disease__name'] for v in comp_disease_qs]
    comp_per_disease_data = [v['total'] for v in comp_disease_qs]

    # Competence per Mentee
    comp_mentee_qs = AssignedCompetence.objects.values('mentee__username').annotate(total=Count('id'))
    comp_per_mentee_labels = [v['mentee__username'] for v in comp_mentee_qs]
    comp_per_mentee_data = [v['total'] for v in comp_mentee_qs]

    context = {
        'visits_labels': json.dumps(list(visits_per_site.keys())),
        'visits_data': json.dumps(list(visits_per_site.values())),
        'progress_labels': json.dumps(progress_labels),
        'progress_data': json.dumps(progress_data),
        'status_labels': json.dumps(list(competence_status.keys())),
        'status_data': json.dumps(list(competence_status.values())),
        'comp_visit_labels': json.dumps(comp_per_visit_labels),
        'comp_visit_data': json.dumps(comp_per_visit_data),
        'comp_disease_labels': json.dumps(comp_per_disease_labels),
        'comp_disease_data': json.dumps(comp_per_disease_data),
        'comp_mentee_labels': json.dumps(comp_per_mentee_labels),
        'comp_mentee_data': json.dumps(comp_per_mentee_data),
    }

    return render(request, 'reports/index.html', context)
