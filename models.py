from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(32), nullable=False, default='Student') # Roles: HOD, Faculty, Club Coordinator, Event Manager, Student
    department = db.Column(db.String(64), nullable=False, default='Computer Science & Engineering')
    is_active_account = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    events_created = db.relationship('Event', backref='creator', lazy=True)
    courses_created = db.relationship('Course', backref='creator', lazy=True)
    resources_created = db.relationship('TechResource', backref='creator', lazy=True)
    announcements_created = db.relationship('Announcement', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.is_active_account

    # Role check helpers
    @property
    def is_hod(self):
        return self.role == 'HOD'

    @property
    def is_faculty(self):
        return self.role in ['HOD', 'Faculty']

    @property
    def is_coordinator(self):
        return self.role in ['HOD', 'Faculty', 'Club Coordinator']

    @property
    def is_staff(self):
        return self.role in ['HOD', 'Faculty', 'Club Coordinator', 'Event Manager']

    def can_manage_events(self):
        return self.role in ['HOD', 'Faculty', 'Club Coordinator', 'Event Manager']

    def can_delete_events(self):
        return self.role in ['HOD', 'Club Coordinator']

    def can_manage_courses(self):
        return self.role in ['HOD', 'Faculty', 'Club Coordinator']

    def can_manage_resources(self):
        return self.role in ['HOD', 'Faculty', 'Club Coordinator']

    def can_manage_announcements(self):
        return self.role in ['HOD', 'Faculty', 'Club Coordinator', 'Event Manager']

    def can_manage_users(self):
        return self.role == 'HOD'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    event_type = db.Column(db.String(50), nullable=False) # Hackathon, Competition, Workshop, Seminar, Webinar, Project Showcase, Coding Contest, Technical Talk
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100), nullable=False)
    registration_deadline = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=50)
    registration_link = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Upcoming') # Upcoming, Ongoing, Completed, Cancelled
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    registrations = db.relationship('Registration', backref='event', cascade='all, delete-orphan', lazy=True)

    @property
    def registered_count(self):
        return len(self.registrations)

    @property
    def seats_left(self):
        left = self.capacity - self.registered_count
        return left if left >= 0 else 0

    @property
    def capacity_percentage(self):
        if self.capacity <= 0:
            return 100
        pct = (self.registered_count / self.capacity) * 100
        return min(round(pct, 1), 100)

    @property
    def is_full(self):
        return self.registered_count >= self.capacity

    @property
    def is_deadline_passed(self):
        return datetime.utcnow() > self.registration_deadline

    def __repr__(self):
        return f'<Event {self.title}>'


class Registration(db.Model):
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('event_id', 'roll_number', name='unique_student_event_registration'),
    )

    def __repr__(self):
        return f'<Registration {self.student_name} - {self.roll_number}>'


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    technology = db.Column(db.String(100), nullable=False) # Python, Web Development, Java, C++, SQL, Data Analytics, AI, Machine Learning, Generative AI, Cloud, Cybersecurity
    level = db.Column(db.String(30), nullable=False, default='Beginner') # Beginner, Intermediate, Advanced
    duration = db.Column(db.String(50), nullable=False)
    learning_link = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Course {self.title}>'


class TechResource(db.Model):
    __tablename__ = 'tech_resources'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    technology = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # Roadmaps, Tools, Technologies, Project Ideas, Interview Preparation, Git/GitHub, Programming, AI, Web Development, Database, Cloud
    description = db.Column(db.Text, nullable=False)
    external_link = db.Column(db.String(255), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TechResource {self.title}>'


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='General') # General, Hackathon, Workshop, Certificate, Competition, Placement, Monthly Activity
    is_pinned = db.Column(db.Boolean, default=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Announcement {self.title}>'
