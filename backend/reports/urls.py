from django.urls import path
from reports.views import (
    GradeSummaryReportView,
    GradeSummaryExportPDFView,
    GradeSummaryExportExcelView,
    UsersReportView,
    UsersExportExcelView,
    UsersExportPDFView,
    CompetenceReportView,
    CompetenceExportExcelView,
    CompetenceExportPDFView,
    VisitsReportView,
    VisitsExportExcelView,
    VisitsExportPDFView,
    GeneralVisualizationReportView,
    GeneralReportView,
    GeneralDashboardReportView,
    LocationsReportView,
    LocationsExportExcelView,
    LocationsExportPDFView,
    DashboardExportExcelView,
    DashboardExportPDFView,
)

app_name = "reports"

urlpatterns = [
    path('grade-summary/', GradeSummaryReportView.as_view(), name='grade-summary'),
    path('grade-summary/export/excel/', GradeSummaryExportExcelView.as_view(), name='grade-summary-excel'),
    path('grade-summary/export/pdf/', GradeSummaryExportPDFView.as_view(), name='grade-summary-pdf'),
    # ===========================
    # Dashboard Reports
    # ===========================
    path("reports/dashboard/general/", GeneralDashboardReportView.as_view(), name="general-dashboard"),
    path("reports/dashboard/visualization/", GeneralVisualizationReportView.as_view(), name="general-visualization"),
    path("reports/dashboard/report/", GeneralReportView.as_view(), name="general-report"),
    path("reports/dashboard/export-excel/", DashboardExportExcelView.as_view(), name="dashboard-export-excel"),
    path("reports/dashboard/export-pdf/", DashboardExportPDFView.as_view(), name="dashboard-export-pdf"),

    # ===========================
    # Visits Reports
    # ===========================
    path("reports/visits/", VisitsReportView.as_view(), name="visits"),
    path("reports/visits/export-excel/", VisitsExportExcelView.as_view(), name="visits-export-excel"),
    path("reports/visits/export-pdf/", VisitsExportPDFView.as_view(), name="visits-export-pdf"),

    # ===========================
    # Competence Reports
    # ===========================
    path("reports/competence/", CompetenceReportView.as_view(), name="competence"),
    path("reports/competence/export-excel/", CompetenceExportExcelView.as_view(), name="competence-export-excel"),
    path("reports/competence/export-pdf/", CompetenceExportPDFView.as_view(), name="competence-export-pdf"),

    # ===========================
    # Users Reports
    # ===========================
    path("reports/users/", UsersReportView.as_view(), name="users"),
    path("reports/users/export-excel/<str:group>/", UsersExportExcelView.as_view(), name="users-export-excel"),
    path("reports/users/export-pdf/<str:group>/", UsersExportPDFView.as_view(), name="users-export-pdf"),

    # ===========================
    # Locations Reports
    # ===========================
    path("reports/locations/", LocationsReportView.as_view(), name="locations"),
    path("reports/locations/export-excel/", LocationsExportExcelView.as_view(), name="locations-export-excel"),
    path("reports/locations/export-pdf/", LocationsExportPDFView.as_view(), name="locations-export-pdf"),
]
