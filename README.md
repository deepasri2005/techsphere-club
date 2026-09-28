# 🚀 TechSphere Club - College Technical Club Community Portal

**TechSphere Club** is a commercial-grade, production-ready web platform for managing technical club events, hackathons, coding competitions, certificate courses, technology roadmaps, announcements, and student registrations. Designed specifically for students, faculty advisors, and HODs.

---

## 🌟 Key Commercial Features

1. **Role-Based Access Control (RBAC)**:
   - **HOD**: Full admin control, system user management, role assignment, registration CSV export, and permission matrix overview.
   - **Faculty**: Event creation & management, certificate courses, tech hub resources, announcements, attendance tracking.
   - **Club Coordinator**: Full CRUD for events, courses, tech resources, announcements, and registrations.
   - **Event Manager**: Event creation/updates, event announcements, and attendance rosters.
   - **Student / Viewer**: Browse events, filter courses & roadmaps, single-click event registration with automatic duplicate roll number prevention.
2. **Instant Demo Accounts Presets**: One-click preset login buttons on the sign-in page for instant client sales demonstrations.
3. **Interactive Seat & Deadline Indicators**: Live capacity progress bars and status badges (Open, Sold Out, Deadline Passed).
4. **Attendance CSV Export**: One-click export for event registration tables in standard CSV format for college administrative reports.
5. **Real Verified Datasets**: 100% authentic links leading to official documentation (PyTorch, Mozilla MDN, Roadmap.sh, Harvard CS50, AWS, Git-SCM, LeetCode).
6. **Modern Dark Glassmorphism Design System**: Custom responsive CSS with glowing accents, smooth micro-interactions, Google Fonts (`Plus Jakarta Sans`), and zero heavy frontend framework overhead.

---

## 🛠️ Technology Stack

- **Backend**: Python Flask 3.x
- **Database**: SQLite with SQLAlchemy 2.x ORM
- **Authentication**: Flask-Login + Werkzeug Security (password hashing)
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism & Flex/Grid), Vanilla JavaScript (Live search, tab filters, CSV generator)

---

## 🔑 Demo Account Credentials

All pre-created accounts share the default password: **`password123`**

| Role | Username / Email | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **HOD** | `hod@techsphere.edu` *(or `hod_cse`)* | `password123` | Full System Admin & Role Management |
| **Faculty** | `faculty@techsphere.edu` *(or `prof_meera`)* | `password123` | Faculty Advisor & Content Manager |
| **Club Coordinator** | `coordinator@techsphere.edu` *(or `rahul_lead`)* | `password123` | Chief Student Coordinator |
| **Event Manager** | `eventmanager@techsphere.edu` *(or `priya_events`)* | `password123` | Operations Specialist |
| **Student** | `student@techsphere.edu` *(or `ananya_sen`)* | `password123` | Student Participant |

---

## 💻 How to Run in VS Code on Windows

Follow these simple step-by-step instructions to run the project on your Windows machine:

### Step 1: Open Project in VS Code
1. Launch **Visual Studio Code**.
2. Click **File > Open Folder...** and select the project directory:
   ```text
   c:\Users\deepa\OneDrive\Project\club_portal
   ```

### Step 2: Open Terminal in VS Code
Open the integrated terminal in VS Code by pressing **`Ctrl + ~`** (or selecting **Terminal > New Terminal** from the top menu).

### Step 3: Install Required Dependencies
Run the following command in the terminal to install Flask and its required packages:
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Launch the Web Application
Run the Flask server using Python:
```powershell
python app.py
```

### Step 5: Open Portal in Web Browser
Open your browser (Chrome, Edge, or Firefox) and navigate to:
```text
http://127.0.0.1:5000
```
The database (`instance/techsphere.db` or `techsphere.db`) will automatically create tables and populate initial commercial sample data upon startup!

---

## 📁 Project Structure

```text
club_portal/
├── app.py                  # Main Flask App & Routing Engine
├── models.py               # SQLAlchemy Database Models (User, Event, Registration, Course, etc.)
├── helpers.py              # Role Permission Decorators & Automatic Database Seeder
├── requirements.txt        # Python Package Dependencies
├── README.md               # Windows VS Code Execution & Manual
├── instance/
│   └── techsphere.db       # SQLite Database File
├── static/
│   ├── css/
│   │   └── style.css       # Production Glassmorphism CSS Design System
│   └── js/
│       └── main.js        # Mobile Drawer, Filters, Live Search, CSV Exporter
└── templates/
    ├── base.html           # Master Layout Template with Navbar & Footer
    ├── index.html          # Public Commercial Landing Page
    ├── login.html          # Login View with Instant Demo Presets
    ├── register.html       # Student Self-Registration Form
    ├── dashboard.html      # Role-Aware Command Dashboard
    ├── events/
    │   ├── index.html      # Event Catalog & Category Pills
    │   ├── detail.html     # Event Details & Registration Form
    │   └── form.html       # Create / Edit Event Form
    ├── registrations/
    │   └── index.html      # Event Registrations & CSV Export Table
    ├── courses/
    │   ├── index.html      # Certificate Courses Hub
    │   └── form.html       # Course Creation Form
    ├── tech_hub/
    │   ├── index.html      # Knowledge Hub & Technology Roadmaps
    │   └── form.html       # Resource Creation Form
    ├── announcements/
    │   ├── index.html      # Announcement Bulletin
    │   └── form.html       # Announcement Creation Form
    ├── admin/
    │   └── users.html      # HOD User Management & Role Control
    └── errors/
        ├── 403.html        # Custom 403 Forbidden Page
        └── 404.html        # Custom 404 Not Found Page
```

---

## 🛡️ Security Verification Matrix

- **Backend Authorization**: Unauthorized access to `/admin/users` or `/events/create` by a Student role returns a clean, custom `403 Forbidden` error page.
- **Duplicate Prevention**: Registration forms prevent double submission for the same `(event_id, roll_number)` pair with immediate feedback warnings.
- **Hashed Credentials**: All passwords are stored securely using SHA-256 salted hashes.

---

*TechSphere Club — Commercial Quality College Technical Club Community Portal.*
