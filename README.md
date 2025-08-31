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





```markdown
# 📝 Logbook – Mentorship Management System

![Django](https://img.shields.io/badge/Django-4.2-green)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## **Project Overview**
**Logbook** is a Django web application designed to manage mentorship activities in clinical and healthcare settings. It allows administrators, mentors, and mentees to track mentorship visits, assign competencies, and monitor progress efficiently.

**Key Features:**
- Mentorship visit scheduling and management  
- Assignment of competencies to mentees  
- Progress tracking and assessment reporting  
- Role-based access (Admin, Mentor, Mentee, Reviewer)  
- Dashboards with charts and statistics  

**Tech Stack:**  
- **Backend:** Django, Django REST Framework  
- **Frontend:** Django Templates + Bootstrap 5  
- **Database:** PostgreSQL / MySQL  
- **Charts & Visualization:** Chart.js  

---

## **Features**

### ✅ User Management
- User registration, login, and logout  
- Password reset and email verification  
- Role-based permissions: Admin, Mentor, Mentee, Reviewer  

### ✅ Mentorship Visits
- Create, update, and delete visits (Admin)  
- Assign mentors to sites and diseases  
- Filter visits by mentor, site, disease, status, and date range  
- View detailed visit information  

### ✅ Assignments & Competencies
- Assign competencies to mentees for each visit day  
- Track completion progress  
- Dashboard shows top competencies per disease  

### ✅ Dashboards & Reports
- Charts for visits per site and mentee submissions  
- Recent activity feed  
- Progress indicators for visits, assessments, and competencies  

---

## **Project Structure**
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

## **Installation & Setup**

1. **Clone the repository:**  
```bash
git clone <repo-url>
cd logbook/backend
````

2. **Create a virtual environment & install dependencies:**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Setup the database:**

```bash
python manage.py migrate
python manage.py createsuperuser
```

4. **Run the development server:**

```bash
python manage.py runserver
```

5. **Access the app:**
   Visit `http://127.0.0.1:8000/` in your browser

---

## **Screenshots / Demo**

> Include screenshots of key pages here:

* Dashboard
* Visit List with filters
* Add Visit form
* Assignment / Competence page
* Charts for visits and submissions

---

## **Testing**

* Tests are located in `mentorship/tests.py`
* Run tests with:

```bash
python manage.py test mentorship
```

---

## **Future Improvements**

* Export reports to Excel/PDF
* Email/SMS notifications for new visits or assignments
* Mobile-friendly frontend (React or responsive templates)
* Advanced analytics and KPI tracking

---

## **Contribution & Maintenance**

* Follows Django best practices
* Clean separation of forms, views, and templates
* Uses `get_queryset` and `get_context_data` for filtering and dashboard data
* Easy to extend with additional roles, sites, or reporting features

---

## **Author & Contact**

**Developer:** Winstone Makwesheni
**Email:** [manquiz92@gmail.com](mailto:manquiz92@gmail.com)
**Location:** Dar es Salaam, Tanzania

---

**License:** MIT License

---

> This project is production-ready and can be deployed for clinical mentorship management.

```# my-wallet
