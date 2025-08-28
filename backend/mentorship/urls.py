from django.urls import path
from mentorship.views import (
    CompetenceByDiseaseView,
    IndexView,
    VisitListView,
    VisitDetailView,
    VisitCreateView,
    VisitDeleteView,
    VisitDayUpdateView,
    VisitDayDeleteView,
    VisitDayDetailView,
    AssignedCompetenceView,
    AssignedCompetenceUpdateView,
    AssignedCompetenceDetailView,
    MentorGradeView,
    MenteeSelfAssessmentView,
    AllAssessmentsListView,
    AssignedCompetenceDeleteView,
    VisitDayListView,
    AssignedCompetenceListView,
    CompetenceListView,
)

# from mentorship.views import visit_views

app_name = 'mentorship'

urlpatterns = [
    # Home
    path("", IndexView.as_view(), name="index"),

    # Visits
    path('visits/', VisitListView.as_view(), name='visit-list'),
    path('visit/add/', VisitCreateView.as_view(), name='add-visit'),          # Admin only
    path('visit/<int:pk>/', VisitDetailView.as_view(), name='visit-detail'),
    path('visit/<int:pk>/delete/', VisitDeleteView.as_view(), name='delete-visit'),

    # Visit Days
    path('visit-days/', VisitDayListView.as_view(), name='visit-day-list'),
    path('visit-day/<int:pk>/edit/', VisitDayUpdateView.as_view(), name='edit-visit-day'),
    path('visit-day/<int:pk>/delete/', VisitDayDeleteView.as_view(), name='delete-visit-day'),
    path('visit-day/<int:pk>/', VisitDayDetailView.as_view(), name='visit-day-detail'),

    # Assign Competencies
    path('competences/', CompetenceListView.as_view(), name='competence-list'),
    path('competences/<int:pk>/', CompetenceListView.as_view(), name='competence-detail'),
    path('visit-day/<int:visit_day_id>/assign/', AssignedCompetenceView.as_view(), name='assign-competence'),  # Mentor only

    # Assigned Competence
    path('assessments/', AssignedCompetenceListView.as_view(), name='assigned-competence-list'),
    path('assessments/<int:pk>/', AssignedCompetenceListView.as_view(), name='assigned-competence-detail'),
    path('assigned-competence/<int:pk>/edit/', AssignedCompetenceUpdateView.as_view(), name='assigned-competence-edit'),
    path('assigned-competence/<int:pk>/view/', AssignedCompetenceDetailView.as_view(), name='assigned-competence-view'),
    path('assigned-competence/<int:pk>/delete/', AssignedCompetenceDeleteView.as_view(), name='assigned-competence-delete'),

    path("competence-by-disease/", CompetenceByDiseaseView.as_view(), name="competence-by-disease"),

    # Mentor and Mentee actions
    path('assignment/<int:pk>/mentor-grade/', MentorGradeView.as_view(), name='mentor-grade'),       # Mentor only
    path('assignment/<int:pk>/self-assess/', MenteeSelfAssessmentView.as_view(), name='mentee-self-assess'),  # Mentee only
    
    # All assessments (Reviewer/Admin)
    path('assessments/', AllAssessmentsListView.as_view(), name='all-assessments'),
]
