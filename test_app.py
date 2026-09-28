import unittest
from datetime import datetime, timedelta
from app import app, db
from models import User, Event, Registration, Course, TechResource, Announcement
from helpers import seed_database

class TechSphereTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            seed_database()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_01_authentication_and_roles(self):
        """Test authentication for all 5 roles."""
        # HOD Login
        response = self.login('hod@techsphere.edu', 'password123')
        self.assertIn(b'Signed in as HOD', response.data)
        self.logout()

        # Faculty Login
        response = self.login('faculty@techsphere.edu', 'password123')
        self.assertIn(b'Signed in as Faculty', response.data)
        self.logout()

        # Coordinator Login
        response = self.login('coordinator@techsphere.edu', 'password123')
        self.assertIn(b'Signed in as Club Coordinator', response.data)
        self.logout()

        # Event Manager Login
        response = self.login('eventmanager@techsphere.edu', 'password123')
        self.assertIn(b'Signed in as Event Manager', response.data)
        self.logout()

        # Student Login
        response = self.login('student@techsphere.edu', 'password123')
        self.assertIn(b'Signed in as Student', response.data)
        self.logout()

    def test_02_student_role_protection_403(self):
        """Verify Student role receives 403 Forbidden on admin & edit routes."""
        self.login('student@techsphere.edu', 'password123')

        # Attempt to access HOD user management page
        resp_admin = self.client.get('/admin/users')
        self.assertEqual(resp_admin.status_code, 403)

        # Attempt to access Event Creation page
        resp_create_event = self.client.get('/events/create')
        self.assertEqual(resp_create_event.status_code, 403)

        # Attempt to access Course Creation page
        resp_create_course = self.client.get('/courses/create')
        self.assertEqual(resp_create_course.status_code, 403)

        self.logout()

    def test_03_hod_admin_access(self):
        """Verify HOD role can access user management."""
        self.login('hod@techsphere.edu', 'password123')
        resp = self.client.get('/admin/users')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'HOD Administration Console', resp.data)
        self.logout()

    def test_04_create_event_and_register(self):
        """Test event creation and student registration."""
        self.login('coordinator@techsphere.edu', 'password123')

        event_data = {
            'title': 'Automated Test Hackathon 2026',
            'event_type': 'Hackathon',
            'description': 'Testing event creation pipeline.',
            'date': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%dT%H:%M'),
            'registration_deadline': (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%dT%H:%M'),
            'venue': 'Lab 1',
            'organizer': 'Test Cell',
            'capacity': 50,
            'registration_link': '',
            'status': 'Upcoming'
        }

        resp = self.client.post('/events/create', data=event_data, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Automated Test Hackathon 2026', resp.data)

        # Find newly created event
        with app.app_context():
            ev = Event.query.filter_by(title='Automated Test Hackathon 2026').first()
            self.assertIsNotNone(ev)
            ev_id = ev.id

        # Register a student for this event
        reg_data = {
            'student_name': 'Test Student',
            'roll_number': 'TESTROLL999',
            'email': 'test@student.edu',
            'department': 'Computer Science & Engineering'
        }
        resp_reg = self.client.post(f'/events/{ev_id}/register', data=reg_data, follow_redirects=True)
        self.assertIn(b'Registration successful!', resp_reg.data)

        # Attempt DUPLICATE registration with SAME roll number for SAME event
        resp_dup = self.client.post(f'/events/{ev_id}/register', data=reg_data, follow_redirects=True)
        self.assertIn(b'Duplicate registration prevented', resp_dup.data)

    def test_05_course_and_resource_creation(self):
        """Test creating course and tech resource."""
        self.login('faculty@techsphere.edu', 'password123')

        # Course Creation
        course_data = {
            'title': 'Automated Test Course',
            'provider': 'Test Provider',
            'technology': 'Python',
            'level': 'Beginner',
            'duration': '2 Weeks',
            'learning_link': 'https://python.org',
            'description': 'Test course description.'
        }
        resp_c = self.client.post('/courses/create', data=course_data, follow_redirects=True)
        self.assertIn(b'Automated Test Course', resp_c.data)

        # Tech Resource Creation
        res_data = {
            'title': 'Automated Test Resource',
            'technology': 'Web Development',
            'category': 'Roadmaps',
            'description': 'Test resource description.',
            'external_link': 'https://developer.mozilla.org'
        }
        resp_r = self.client.post('/tech-hub/create', data=res_data, follow_redirects=True)
        self.assertIn(b'Automated Test Resource', resp_r.data)

        self.logout()

if __name__ == '__main__':
    unittest.main()
