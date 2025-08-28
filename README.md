# logbook

Mentorship App

Perfect! Here's a ready-to-use **Markdown documentation** for your Logbook project. You can save it as `LOGBOOK_PROJECT.md` in your repository:

```markdown
# Logbook – Mentorship Management System

## 1. Project Overview
**Title:** Logbook – Mentorship Management System  

**Description:**  
Logbook is a Django web application designed to manage mentorship activities in clinical settings. It supports:
- Mentorship visit scheduling
- Assignment of competencies to mentees
- Progress tracking and assessment reporting
- Role-based access control (Admin, Mentor, Mentee, Reviewer)
- Dashboards with charts and statistics

**Tech Stack:**  
- **Backend:** Django, Django REST Framework  
- **Frontend:** Django Templates + Bootstrap 5  
- **Database:** PostgreSQL / MySQL  
- **Other:** Chart.js for dashboard charts  

---

## 2. Features

### User Management
- Registration, login, logout
- Password reset and email verification
- Roles: Admin, Mentor, Mentee, Reviewer
- Profile management

### Mentorship Visits
- Schedule visits with start/end dates
- Assign mentors to sites and specific diseases
- Filter visits by mentor, site, disease, status, and date range
- View visit details and delete (Admin only)

### Assignments & Competencies
- Assign competencies to mentees per visit day
- Track assessment progress
- Dashboard shows total assessments, completed competences, and top competencies by disease

### Dashboards & Reports
- Charts: Visits per site, mentee submissions
- Recent activity feed
- Progress indicators for visits, assessments, and competences

### Permissions
- **Admin:** Full access, can add/edit/delete visits  
- **Mentor:** View visits, assign competencies, assess mentees  
- **Mentee:** View assigned competencies, submit assessments  
- **Reviewer:** View and review completed visits  

---

## 3. Project Structure
```

logbook/
├── backend/
│   ├── mentorship/
│   │   ├── models.py          # Visit, VisitDay, AssignedCompetence
│   │   ├── views.py           # ListView, DetailView, CreateView, Dashboard
│   │   ├── forms.py           # Visit and Assignment forms
│   │   ├── templates/         # HTML templates
│   │   └── tests.py           # Unit tests for the app
│   ├── clinical/
│   │   ├── models.py          # Disease, Competence
│   │   └── ...
│   └── src/
│       └── settings.py
└── frontend/                  # React app (if used)

````

---

## 4. Installation / Setup Instructions
1. **Clone the repository:**  
```bash
git clone <repo-url>
cd logbook/backend
````

2. **Create virtual environment & install dependencies:**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Setup database:**

```bash
python manage.py migrate
python manage.py createsuperuser
```

4. **Run server:**

```bash
python manage.py runserver
```

5. **Access:**
   Open your browser at `http://127.0.0.1:8000/`

---

## 5. Screenshots / Demo

> Add screenshots here to showcase the UI:

* Dashboard
* Visit list with filters
* Add Visit form
* Assignment/Competence page
* Charts for visits and submissions

---

## 6. Testing

* Tests are located in `mentorship/tests.py`
* Run tests with:

```bash
python manage.py test mentorship
```

---

## 7. Future Improvements

* Add **export to Excel/PDF** for filtered reports
* Email/SMS notifications for new visits or assignments
* Mobile-friendly React frontend
* More detailed analytics and KPI tracking

---

## 8. Contribution / Maintenance

* Code is structured using Django best practices
* Forms, templates, and views follow consistent patterns
* Filtering and dashboard data handled via `get_queryset` and `get_context_data`

---

## 9. Authors / Contacts

* **Developer:** Winstone Makwesheni
* **Email:** [manquiz92@gmail.com](mailto:manquiz92@gmail.com)
* **Location:** Dar es Salaam, Tanzania

---

*This documentation is intended for future reference, maintenance, and showcasing in portfolios.*

```

---

If you want, I can **also create a version ready for GitHub README** with **badges, live demo link, and nicer formatting** so it looks professional in your portfolio.  

Do you want me to do that?
```
