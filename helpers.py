from functools import wraps
from datetime import datetime, timedelta
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from models import db, User, Event, Registration, Course, TechResource, Announcement

def role_required(*roles):
    """
    Decorator to enforce backend role permissions on routes.
    Example: @role_required('HOD', 'Faculty')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def seed_database():
    """Populates the database with real, commercial-grade initial data."""

    # Seed Users if database is empty
    if User.query.count() == 0:
        hod = User(
            username='hod_cse',
            email='hod@techsphere.edu',
            full_name='Dr. A. K. Sharma',
            role='HOD',
            department='Computer Science & Engineering',
            is_active_account=True
        )
        hod.set_password('password123')

        faculty = User(
            username='prof_meera',
            email='faculty@techsphere.edu',
            full_name='Prof. Meera Nair',
            role='Faculty',
            department='Computer Science & Engineering',
            is_active_account=True
        )
        faculty.set_password('password123')

        coordinator = User(
            username='rahul_lead',
            email='coordinator@techsphere.edu',
            full_name='Rahul Verma',
            role='Club Coordinator',
            department='Information Technology',
            is_active_account=True
        )
        coordinator.set_password('password123')

        event_mgr = User(
            username='priya_events',
            email='eventmanager@techsphere.edu',
            full_name='Priya Patel',
            role='Event Manager',
            department='Computer Science & Engineering',
            is_active_account=True
        )
        event_mgr.set_password('password123')

        student = User(
            username='ananya_sen',
            email='student@techsphere.edu',
            full_name='Ananya Sen',
            role='Student',
            department='Computer Science & Engineering',
            is_active_account=True
        )
        student.set_password('password123')

        db.session.add_all([hod, faculty, coordinator, event_mgr, student])
        db.session.commit()

    # Retrieve staff user for creation reference
    staff_user = User.query.filter_by(role='HOD').first()

    # Seed Events if empty
    if Event.query.count() == 0:
        now = datetime.utcnow()
        events = [
            Event(
                title='HackSphere 2026: 24-Hour AI & Web3 Hackathon',
                event_type='Hackathon',
                description='Join 100+ passionate student developers in building high-impact AI, Blockchain, and IoT solutions. Features 1-on-1 mentorship from industry engineers, cash prizes worth ₹1,50,000, and direct placement opportunities for top teams!',
                date=now + timedelta(days=15),
                venue='Main Auditorium & Advanced Computing Lab',
                organizer='TechSphere Club & Dept of CSE',
                registration_deadline=now + timedelta(days=12),
                capacity=100,
                registration_link='https://hackathonsphere.org',
                status='Upcoming',
                created_by_id=staff_user.id
            ),
            Event(
                title='CodeBlitz: Inter-College Algorithmic Contest',
                event_type='Coding Contest',
                description='Speed, precision, and algorithmic mastery! 5 challenging problem statements testing Data Structures, Dynamic Programming, and Graph Optimization. Official certificates and prizes awarded to the top 5 coders.',
                date=now + timedelta(days=8),
                venue='Computing Lab 3 & Online Platform',
                organizer='Competitive Programming Wing',
                registration_deadline=now + timedelta(days=7),
                capacity=80,
                registration_link='',
                status='Upcoming',
                created_by_id=staff_user.id
            ),
            Event(
                title='Generative AI & LLM Architecture Masterclass',
                event_type='Workshop',
                description='Hands-on technical workshop exploring Transformer architectures, PyTorch fine-tuning, RAG (Retrieval-Augmented Generation), and vector database integrations with LangChain and Hugging Face.',
                date=now + timedelta(days=22),
                venue='Seminar Hall B & Virtual Stream',
                organizer='AI & Machine Learning Cell',
                registration_deadline=now + timedelta(days=20),
                capacity=60,
                registration_link='',
                status='Upcoming',
                created_by_id=staff_user.id
            ),
            Event(
                title='Cloud Native & Kubernetes Infrastructure Session',
                event_type='Technical Talk',
                description='Industry session hosted by AWS Certified Solutions Architects. Learn Docker containerization, Kubernetes cluster orchestration, GitOps CI/CD pipelines, and cloud scalability best practices.',
                date=now + timedelta(days=30),
                venue='Virtual via Google Meet',
                organizer='DevOps & Cloud Community',
                registration_deadline=now + timedelta(days=28),
                capacity=150,
                registration_link='https://meet.google.com/tech-sphere-cloud',
                status='Upcoming',
                created_by_id=staff_user.id
            ),
            Event(
                title='Final Year Technical Project Showcase & Demo Day',
                event_type='Project Showcase',
                description='Annual project exhibition! Present your engineering prototypes to department faculty, HOD, and invited software leaders. Outstanding project innovations will receive seed incubation guidance.',
                date=now + timedelta(days=40),
                venue='College Exhibition Center',
                organizer='Innovation & Incubation Cell',
                registration_deadline=now + timedelta(days=35),
                capacity=40,
                registration_link='',
                status='Upcoming',
                created_by_id=staff_user.id
            )
        ]
        db.session.add_all(events)
        db.session.commit()

        # Seed sample registrations for first event to demonstrate live statistics
        ev1 = Event.query.first()
        if ev1:
            regs = [
                Registration(event_id=ev1.id, student_name='Ananya Sen', roll_number='2026CSE104', email='ananya.s@student.edu', department='Computer Science & Engineering'),
                Registration(event_id=ev1.id, student_name='Rohan Mehta', roll_number='2026CSE088', email='rohan.m@student.edu', department='Computer Science & Engineering'),
                Registration(event_id=ev1.id, student_name='Kavya Nair', roll_number='2026IT042', email='kavya.n@student.edu', department='Information Technology')
            ]
            db.session.add_all(regs)
            db.session.commit()

    # Seed Courses if empty
    if Course.query.count() == 0:
        courses = [
            Course(
                title='Full-Stack Web Development Bootcamp',
                provider='Mozilla Developer Network & Harvard CS50',
                technology='Web Development',
                level='Intermediate',
                duration='8 Weeks',
                learning_link='https://developer.mozilla.org/en-US/docs/Learn',
                description='Comprehensive curriculum covering modern HTML5, CSS3 Grid/Flexbox, Modern JS (ES6+), RESTful API design with Python Flask, and database integration.',
                created_by_id=staff_user.id
            ),
            Course(
                title='Deep Learning & Neural Networks with PyTorch',
                provider='PyTorch Foundation & DeepLearning.AI',
                technology='AI',
                level='Advanced',
                duration='6 Weeks',
                learning_link='https://pytorch.org/tutorials/',
                description='Master convolutional neural networks, transformer models, computer vision pipelines, and production model deployment using PyTorch.',
                created_by_id=staff_user.id
            ),
            Course(
                title='Python for Data Science & Analytics',
                provider='Python Software Foundation',
                technology='Python',
                level='Beginner',
                duration='4 Weeks',
                learning_link='https://docs.python.org/3/tutorial/',
                description='Learn essential Python programming syntax, NumPy matrix computations, Pandas dataset manipulation, and data visualization with Matplotlib.',
                created_by_id=staff_user.id
            ),
            Course(
                title='Cloud Infrastructure & DevOps Masterclass',
                provider='AWS Academy & Linux Foundation',
                technology='Cloud',
                level='Intermediate',
                duration='6 Weeks',
                learning_link='https://aws.amazon.com/free/',
                description='Practical training in AWS EC2 compute instances, S3 object storage, IAM security policies, Docker containers, and CI/CD pipelines.',
                created_by_id=staff_user.id
            ),
            Course(
                title='Cybersecurity Fundamentals & Ethical Hacking',
                provider='Cisco Networking Academy',
                technology='Cybersecurity',
                level='Beginner',
                duration='5 Weeks',
                learning_link='https://www.netacad.com/courses/cybersecurity',
                description='Fundamental principles of computer network defense, vulnerability assessment, cryptography standards, and penetration testing techniques.',
                created_by_id=staff_user.id
            )
        ]
        db.session.add_all(courses)
        db.session.commit()

    # Seed Tech Resources if empty
    if TechResource.query.count() == 0:
        resources = [
            TechResource(
                title='Interactive Frontend Developer Roadmap 2026',
                technology='Web Development',
                category='Roadmaps',
                description='Step-by-step visual learning path covering core web concepts, HTML/CSS, JavaScript, state management, build tooling, and performance optimization.',
                external_link='https://roadmap.sh/frontend',
                created_by_id=staff_user.id
            ),
            TechResource(
                title='AI & Machine Learning Engineer Career Path',
                technology='AI',
                category='Roadmaps',
                description='Structured progression guide covering Linear Algebra, Statistics, Python libraries, Deep Learning models, and MLOps engineering practices.',
                external_link='https://roadmap.sh/ai-data-scientist',
                created_by_id=staff_user.id
            ),
            TechResource(
                title='LeetCode Top 75 Coding Interview Practice Kit',
                technology='Programming',
                category='Interview Preparation',
                description='Curated selection of essential Data Structures & Algorithms coding challenges frequently featured in technical interviews at top software companies.',
                external_link='https://leetcode.com/problemset/all/',
                created_by_id=staff_user.id
            ),
            TechResource(
                title='Git & GitHub Pro Command & Workflow Reference',
                technology='Git/GitHub',
                category='Tools',
                description='Official documentation for Git branching models, rebase strategies, merge conflict resolution, pull request reviews, and versioning best practices.',
                external_link='https://git-scm.com/doc',
                created_by_id=staff_user.id
            ),
            TechResource(
                title='Production System Design Primer',
                technology='Cloud',
                category='Project Ideas',
                description='Comprehensive architectural guide for building scalable, fault-tolerant web applications, load balancers, caching layers, and microservices.',
                external_link='https://github.com/donnemartin/system-design-primer',
                created_by_id=staff_user.id
            )
        ]
        db.session.add_all(resources)
        db.session.commit()

    # Seed Announcements if empty
    if Announcement.query.count() == 0:
        announcements = [
            Announcement(
                title='🔥 Registration Open: HackSphere 2026 National Hackathon!',
                category='Hackathon',
                content='Registrations are officially open for HackSphere 2026! Form teams of up to 4 members. Early bird deadline is October 12, 2026. Cash awards worth ₹1,50,000 and direct mentorship for top finalists.',
                is_pinned=True,
                created_by_id=staff_user.id
            ),
            Announcement(
                title='⚡ Monthly Technical Activity: CodeBlitz Algorithmic Sprint',
                category='Monthly Activity',
                content='This month\'s mandatory club technical activity is CodeBlitz. All CS & IT students are encouraged to participate. Leaderboard points count towards annual technical distinction awards.',
                is_pinned=True,
                created_by_id=staff_user.id
            ),
            Announcement(
                title='🎓 Placement Preparation: Technical Mock Interviews & Resume Clinic',
                category='Placement',
                content='The Department of CSE in collaboration with TechSphere Club will conduct 1-on-1 technical mock interviews for final year students. Slots are limited; register in the Events module.',
                is_pinned=False,
                created_by_id=staff_user.id
            ),
            Announcement(
                title='🚀 New Industry Certificate Courses Added to Tech Hub',
                category='Certificate',
                content='We have added certified learning paths for PyTorch AI, Full-Stack Web Dev, and AWS Cloud in the Courses module. All links lead directly to official learning platforms.',
                is_pinned=False,
                created_by_id=staff_user.id
            )
        ]
        db.session.add_all(announcements)
        db.session.commit()
