from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count, Avg
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from mentorship.models import Visit, VisitDay, AssignedCompetence
from django.contrib.auth import get_user_model

User = get_user_model()


class UsersReportView(View):
    template_name = "reports/users_reports.html"

    def get(self, request, *args, **kwargs):
        mentors = User.objects.filter(groups__name="Mentor")
        mentees = User.objects.filter(groups__name="Mentee")

        mentor_data = []
        for user in mentors:
            assigned_count = AssignedCompetence.objects.filter(assigned_by=user).count()
            completed_count = AssignedCompetence.objects.filter(assigned_by=user, is_completed=True).count()
            avg_mentor_grade = AssignedCompetence.objects.filter(assigned_by=user).aggregate(avg=Avg('mentor_grade'))['avg']
            avg_mentee_grade = AssignedCompetence.objects.filter(assigned_by=user).aggregate(avg=Avg('mentee_grade'))['avg']
            visits_count = Visit.objects.filter(mentor=user).count()

            mentor_data.append({
                "username": user.username,
                "group": "Mentor",
                "assigned_count": assigned_count,
                "completed_count": completed_count,
                "avg_mentor_grade": round(avg_mentor_grade or 0, 2),
                "avg_mentee_grade": round(avg_mentee_grade or 0, 2),
                "visits_count": visits_count,
            })

        mentee_data = []
        for user in mentees:
            assigned_count = AssignedCompetence.objects.filter(mentee=user).count()
            completed_count = AssignedCompetence.objects.filter(mentee=user, is_completed=True).count()
            avg_mentor_grade = AssignedCompetence.objects.filter(mentee=user).aggregate(avg=Avg('mentor_grade'))['avg']
            avg_mentee_grade = AssignedCompetence.objects.filter(mentee=user).aggregate(avg=Avg('mentee_grade'))['avg']

            # Count visits attended by the mentee
            visits_count = Visit.objects.filter(
                id__in=VisitDay.objects.filter(
                    id__in=AssignedCompetence.objects.filter(mentee=user).values_list('visit_day_id', flat=True)
                ).values_list('visit_id', flat=True)
            ).count()

            mentee_data.append({
                "username": user.username,
                "group": "Mentee",
                "assigned_count": assigned_count,
                "completed_count": completed_count,
                "avg_mentor_grade": round(avg_mentor_grade or 0, 2),
                "avg_mentee_grade": round(avg_mentee_grade or 0, 2),
                "visits_count": visits_count,
            })

        context = {
            "mentor_data": mentor_data,
            "mentee_data": mentee_data,
        }
        return render(request, self.template_name, context)


class UsersExportExcelView(View):
    def get(self, request, group, *args, **kwargs):
        users = User.objects.all()
        if group.lower() == "mentor":
            users = users.filter(groups__name="Mentor")
        elif group.lower() == "mentee":
            users = users.filter(groups__name="Mentee")

        data = []
        for user in users:
            group_name = user.groups.first().name if user.groups.exists() else "No Group"
            if group_name == "Mentor":
                visits_count = Visit.objects.filter(mentor=user).count()
            else:
                visits_count = Visit.objects.filter(
                    id__in=VisitDay.objects.filter(
                        id__in=AssignedCompetence.objects.filter(mentee=user).values_list('visit_day_id', flat=True)
                    ).values_list('visit_id', flat=True)
                ).count()

            assigned_count = AssignedCompetence.objects.filter(mentee=user if group_name=="Mentee" else None, assigned_by=user if group_name=="Mentor" else None).count()
            completed_count = AssignedCompetence.objects.filter(mentee=user if group_name=="Mentee" else None, assigned_by=user if group_name=="Mentor" else None, is_completed=True).count()
            avg_mentor_grade = AssignedCompetence.objects.filter(mentee=user if group_name=="Mentee" else None, assigned_by=user if group_name=="Mentor" else None).aggregate(avg=Avg('mentor_grade'))['avg']
            avg_mentee_grade = AssignedCompetence.objects.filter(mentee=user if group_name=="Mentee" else None, assigned_by=user if group_name=="Mentor" else None).aggregate(avg=Avg('mentee_grade'))['avg']

            data.append({
                "Username": user.username,
                "Group": group_name,
                "Assigned Competences": assigned_count,
                "Completed Competences": completed_count,
                "Average Mentor Grade": round(avg_mentor_grade or 0, 2),
                "Average Mentee Grade": round(avg_mentee_grade or 0, 2),
                "Visits Conducted/Attended": visits_count,
            })

        df = pd.DataFrame(data)
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="users_report_{group}.xlsx"'
        df.to_excel(response, index=False)
        return response


class UsersExportPDFView(View):
    def get(self, request, group, *args, **kwargs):
        users = User.objects.all()
        if group.lower() == "mentor":
            users = users.filter(groups__name="Mentor")
        elif group.lower() == "mentee":
            users = users.filter(groups__name="Mentee")

        data = []
        for user in users:
            group_name = user.groups.first().name if user.groups.exists() else "No Group"
            if group_name == "Mentor":
                visits_count = Visit.objects.filter(mentor=user).count()
            else:
                visits_count = Visit.objects.filter(
                    id__in=VisitDay.objects.filter(
                        id__in=AssignedCompetence.objects.filter(mentee=user).values_list('visit_day_id', flat=True)
                    ).values_list('visit_id', flat=True)
                ).count()

            assigned_count = AssignedCompetence.objects.filter(mentee=user if group_name=="Mentee" else None, assigned_by=user if group_name=="Mentor" else None).count()
            completed_count = AssignedCompetence.objects.filter(mentee=user if group_name=="Mentee" else None, assigned_by=user if group_name=="Mentor" else None, is_completed=True).count()
            avg_mentor_grade = AssignedCompetence.objects.filter(mentee=user if group_name=="Mentee" else None, assigned_by=user if group_name=="Mentor" else None).aggregate(avg=Avg('mentor_grade'))['avg']
            avg_mentee_grade = AssignedCompetence.objects.filter(mentee=user if group_name=="Mentee" else None, assigned_by=user if group_name=="Mentor" else None).aggregate(avg=Avg('mentee_grade'))['avg']

            data.append({
                "Username": user.username,
                "Group": group_name,
                "Assigned Competences": assigned_count,
                "Completed Competences": completed_count,
                "Average Mentor Grade": round(avg_mentor_grade or 0, 2),
                "Average Mentee Grade": round(avg_mentee_grade or 0, 2),
                "Visits Conducted/Attended": visits_count,
            })

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="users_report_{group}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, f"Users Report ({group.capitalize()})")

        y = 760
        p.setFont("Helvetica", 12)
        for row in data:
            line = (f"Username: {row['Username']} | Group: {row['Group']} | "
                    f"Assigned: {row['Assigned Competences']} | Completed: {row['Completed Competences']} | "
                    f"Avg Mentor: {row['Average Mentor Grade']} | Avg Mentee: {row['Average Mentee Grade']} | "
                    f"Visits: {row['Visits Conducted/Attended']}")
            p.drawString(50, y, line)
            y -= 20
            if y < 50:
                p.showPage()
                y = 800

        p.showPage()
        p.save()
        return response


