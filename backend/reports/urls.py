from django.urls import path
from reports.views import (
    UsersReportView,
    UsersExportExcelView,
    UsersExportPDFView,
    CompetenceReportView,
    CompetenceExportExcelView,
    CompetenceExportPDFView,
    # Visits views CBVs
    VisitsReportView,
    VisitsExportExcelView,
    VisitsExportPDFView,
    IndexView,
    DashboardReportView,
    LocationsReportView,
    LocationsExportExcelView,
    LocationsExportPDFView,
    DashboardExportExcelView,
    DashboardExportPDFView,
)

app_name = "reports"

urlpatterns = [
    # Dashboard
    path("", IndexView.as_view(), name="index"),
    path("dashboard-report/", DashboardReportView.as_view(), name="dashboard-report"),
    path("dashboard/export-excel/", DashboardExportExcelView.as_view(), name="dashboard-export-excel"),
    path("dashboard/export-pdf/", DashboardExportPDFView.as_view(), name="dashboard-export-pdf"),
    # Visits reports
    path("visits/", VisitsReportView.as_view(), name="visits"),
    path("visits/export-excel/", VisitsExportExcelView.as_view(), name="visits-export-excel"),
    path("visits/export-pdf/", VisitsExportPDFView.as_view(), name="visits-export-pdf"),

    # Competence reports
    path("competence/", CompetenceReportView.as_view(), name="competence"),
    path("competence/export-excel/", CompetenceExportExcelView.as_view(), name="competence-export-excel"),
    path("competence/export-pdf/", CompetenceExportPDFView.as_view(), name="competence-export-pdf"),

    # Users reports
    path("users/", UsersReportView.as_view(), name="users"),
    path("users/export-excel/<str:group>/", UsersExportExcelView.as_view(), name="users-export-excel"),
    path("users/export-pdf/<str:group>/", UsersExportPDFView.as_view(), name="users-export-pdf"),

    # Locations reports (if still function-based, can keep as is)
    path("locations/", LocationsReportView.as_view(), name="locations"),
    path("locations/export-excel/", LocationsExportExcelView.as_view(), name="locations-export-excel"),
    path("locations/export-pdf/", LocationsExportPDFView.as_view(), name="locations-export-pdf"),
]
