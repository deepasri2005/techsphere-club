import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Event, Registration, Course, TechResource, Announcement
from helpers import role_required, seed_database

app = Flask(__name__)

if os.environ.get('VERCEL'):
    db_path = os.path.join('/tmp', 'techsphere.db')
else:
    db_path = os.path.join(app.root_path, 'techsphere.db')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'techsphere-secret-key-2026-production-ready')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Initialize database & seed initial commercial data
with app.app_context():
    db.create_all()
    seed_database()

# --------------------------------------------------------------------------
# Custom Error Handlers
# --------------------------------------------------------------------------
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

# --------------------------------------------------------------------------
# Authentication & User Management Routes
# --------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if not user or not user.check_password(password):
            flash('Invalid username/email or password.', 'error')
            return redirect(url_for('login'))

        if not user.is_active_account:
            flash('Your account has been deactivated by HOD administration.', 'error')
            return redirect(url_for('login'))

        login_user(user)
        flash(f'Welcome back, {user.full_name}! Signed in as {user.role}.', 'success')
        
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        department = request.form.get('department', 'Computer Science & Engineering').strip()
        password = request.form.get('password', '')

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('An account with this email address already exists.', 'error')
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            department=department,
            role='Student',
            is_active_account=True
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Account created successfully! Welcome to TechSphere Club.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')

# --------------------------------------------------------------------------
# Public Landing Page & Dashboard
# --------------------------------------------------------------------------
@app.route('/')
def index():
    events_count = Event.query.count()
    courses_count = Course.query.count()
    registrations_count = Registration.query.count()
    resources_count = TechResource.query.count()

    upcoming_events = Event.query.filter(Event.status == 'Upcoming').order_by(Event.date.asc()).limit(3).all()
    latest_announcements = Announcement.query.order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).limit(3).all()
    popular_courses = Course.query.limit(3).all()

    return render_template(
        'index.html',
        events_count=events_count,
        courses_count=courses_count,
        registrations_count=registrations_count,
        resources_count=resources_count,
        upcoming_events=upcoming_events,
        latest_announcements=latest_announcements,
        popular_courses=popular_courses
    )


@app.route('/dashboard')
@login_required
def dashboard():
    events_count = Event.query.count()
    upcoming_count = Event.query.filter_by(status='Upcoming').count()
    courses_count = Course.query.count()
    registrations_count = Registration.query.count()
    resources_count = TechResource.query.count()

    upcoming_events = Event.query.filter_by(status='Upcoming').order_by(Event.date.asc()).limit(4).all()
    latest_announcements = Announcement.query.order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).limit(4).all()

    return render_template(
        'dashboard.html',
        events_count=events_count,
        upcoming_count=upcoming_count,
        courses_count=courses_count,
        registrations_count=registrations_count,
        resources_count=resources_count,
        upcoming_events=upcoming_events,
        latest_announcements=latest_announcements
    )

# --------------------------------------------------------------------------
# Event Management Routes
# --------------------------------------------------------------------------
@app.route('/events')
def events():
    all_events = Event.query.order_by(Event.date.asc()).all()
    return render_template('events/index.html', events=all_events)


@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('events/detail.html', event=event)


@app.route('/events/create', methods=['GET', 'POST'])
@role_required('HOD', 'Faculty', 'Club Coordinator', 'Event Manager')
def create_event():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        event_type = request.form.get('event_type', 'Workshop')
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '')
        venue = request.form.get('venue', '').strip()
        organizer = request.form.get('organizer', '').strip()
        deadline_str = request.form.get('registration_deadline', '')
        capacity = int(request.form.get('capacity', 50))
        registration_link = request.form.get('registration_link', '').strip()
        status = request.form.get('status', 'Upcoming')

        event_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        deadline_date = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')

        new_event = Event(
            title=title,
            event_type=event_type,
            description=description,
            date=event_date,
            venue=venue,
            organizer=organizer,
            registration_deadline=deadline_date,
            capacity=capacity,
            registration_link=registration_link,
            status=status,
            created_by_id=current_user.id
        )

        db.session.add(new_event)
        db.session.commit()

        flash(f'Event "{title}" published successfully!', 'success')
        return redirect(url_for('events'))

    return render_template('events/form.html', event=None)


@app.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@role_required('HOD', 'Faculty', 'Club Coordinator', 'Event Manager')
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.title = request.form.get('title', '').strip()
        event.event_type = request.form.get('event_type', event.event_type)
        event.description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '')
        event.venue = request.form.get('venue', '').strip()
        event.organizer = request.form.get('organizer', '').strip()
        deadline_str = request.form.get('registration_deadline', '')
        event.capacity = int(request.form.get('capacity', event.capacity))
        event.registration_link = request.form.get('registration_link', '').strip()
        event.status = request.form.get('status', event.status)

        if date_str:
            event.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        if deadline_str:
            event.registration_deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')

        db.session.commit()
        flash('Event details updated successfully.', 'success')
        return redirect(url_for('event_detail', event_id=event.id))

    return render_template('events/form.html', event=event)


@app.route('/events/<int:event_id>/delete', methods=['POST'])
@role_required('HOD', 'Club Coordinator')
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    title = event.title
    db.session.delete(event)
    db.session.commit()
    flash(f'Event "{title}" deleted.', 'info')
    return redirect(url_for('events'))

# --------------------------------------------------------------------------
# Student Registration & Duplicate Prevention
# --------------------------------------------------------------------------
@app.route('/events/<int:event_id>/register', methods=['POST'])
def register_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.is_full:
        flash('Registration failed: Event capacity is full.', 'error')
        return redirect(url_for('event_detail', event_id=event.id))

    if event.is_deadline_passed:
        flash('Registration failed: Registration deadline has passed.', 'error')
        return redirect(url_for('event_detail', event_id=event.id))

    student_name = request.form.get('student_name', '').strip()
    roll_number = request.form.get('roll_number', '').strip()
    email = request.form.get('email', '').strip()
    department = request.form.get('department', '').strip()

    # Prevent Duplicate Registration for same event + roll number
    existing_reg = Registration.query.filter_by(
        event_id=event.id,
        roll_number=roll_number
    ).first()

    if existing_reg:
        flash(f'Duplicate registration prevented: Roll number "{roll_number}" is already registered for this event.', 'warning')
        return redirect(url_for('event_detail', event_id=event.id))

    new_reg = Registration(
        event_id=event.id,
        student_name=student_name,
        roll_number=roll_number,
        email=email,
        department=department
    )

    db.session.add(new_reg)
    db.session.commit()

    flash(f'Registration successful! {student_name} (Roll: {roll_number}) is registered for {event.title}.', 'success')
    return redirect(url_for('event_detail', event_id=event.id))


@app.route('/registrations')
@role_required('HOD', 'Faculty', 'Club Coordinator', 'Event Manager')
def registrations():
    all_registrations = Registration.query.order_by(Registration.created_at.desc()).all()
    all_events = Event.query.all()
    return render_template('registrations/index.html', registrations=all_registrations, events=all_events)

# --------------------------------------------------------------------------
# Course Module Routes
# --------------------------------------------------------------------------
@app.route('/courses')
def courses():
    all_courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('courses/index.html', courses=all_courses)


@app.route('/courses/create', methods=['GET', 'POST'])
@role_required('HOD', 'Faculty', 'Club Coordinator')
def create_course():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        provider = request.form.get('provider', '').strip()
        technology = request.form.get('technology', 'Web Development')
        level = request.form.get('level', 'Beginner')
        duration = request.form.get('duration', '').strip()
        learning_link = request.form.get('learning_link', '').strip()
        description = request.form.get('description', '').strip()

        new_course = Course(
            title=title,
            provider=provider,
            technology=technology,
            level=level,
            duration=duration,
            learning_link=learning_link,
            description=description,
            created_by_id=current_user.id
        )

        db.session.add(new_course)
        db.session.commit()

        flash(f'Course "{title}" added successfully!', 'success')
        return redirect(url_for('courses'))

    return render_template('courses/form.html')


@app.route('/courses/<int:course_id>/delete', methods=['POST'])
@role_required('HOD', 'Faculty', 'Club Coordinator')
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    title = course.title
    db.session.delete(course)
    db.session.commit()
    flash(f'Course "{title}" deleted.', 'info')
    return redirect(url_for('courses'))

# --------------------------------------------------------------------------
# Technology Hub Routes
# --------------------------------------------------------------------------
@app.route('/tech-hub')
def tech_hub():
    resources = TechResource.query.order_by(TechResource.created_at.desc()).all()
    return render_template('tech_hub/index.html', resources=resources)


@app.route('/tech-hub/create', methods=['GET', 'POST'])
@role_required('HOD', 'Faculty', 'Club Coordinator')
def create_resource():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        technology = request.form.get('technology', '').strip()
        category = request.form.get('category', 'Roadmaps')
        description = request.form.get('description', '').strip()
        external_link = request.form.get('external_link', '').strip()

        new_res = TechResource(
            title=title,
            technology=technology,
            category=category,
            description=description,
            external_link=external_link,
            created_by_id=current_user.id
        )

        db.session.add(new_res)
        db.session.commit()

        flash(f'Tech resource "{title}" added to Knowledge Hub!', 'success')
        return redirect(url_for('tech_hub'))

    return render_template('tech_hub/form.html')


@app.route('/tech-hub/<int:resource_id>/delete', methods=['POST'])
@role_required('HOD', 'Faculty', 'Club Coordinator')
def delete_resource(resource_id):
    res = TechResource.query.get_or_404(resource_id)
    title = res.title
    db.session.delete(res)
    db.session.commit()
    flash(f'Tech resource "{title}" deleted.', 'info')
    return redirect(url_for('tech_hub'))

# --------------------------------------------------------------------------
# Club Announcements Routes
# --------------------------------------------------------------------------
@app.route('/announcements')
def announcements():
    all_announcements = Announcement.query.order_by(
        Announcement.is_pinned.desc(),
        Announcement.created_at.desc()
    ).all()
    return render_template('announcements/index.html', announcements=all_announcements)


@app.route('/announcements/create', methods=['GET', 'POST'])
@role_required('HOD', 'Faculty', 'Club Coordinator', 'Event Manager')
def create_announcement():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'General')
        content = request.form.get('content', '').strip()
        is_pinned = request.form.get('is_pinned') == 'true'

        new_ann = Announcement(
            title=title,
            category=category,
            content=content,
            is_pinned=is_pinned,
            created_by_id=current_user.id
        )

        db.session.add(new_ann)
        db.session.commit()

        flash('Announcement notice published!', 'success')
        return redirect(url_for('announcements'))

    return render_template('announcements/form.html')


@app.route('/announcements/<int:announcement_id>/delete', methods=['POST'])
@role_required('HOD', 'Faculty', 'Club Coordinator', 'Event Manager')
def delete_announcement(announcement_id):
    ann = Announcement.query.get_or_404(announcement_id)
    db.session.delete(ann)
    db.session.commit()
    flash('Announcement deleted.', 'info')
    return redirect(url_for('announcements'))

# --------------------------------------------------------------------------
# HOD Administration Routes
# --------------------------------------------------------------------------
@app.route('/admin/users')
@role_required('HOD')
def admin_users():
    users = User.query.order_by(User.id.asc()).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/<int:user_id>/update', methods=['POST'])
@role_required('HOD')
def admin_update_user(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    is_active_account_val = request.form.get('is_active_account') == 'true'

    if new_role in ['HOD', 'Faculty', 'Club Coordinator', 'Event Manager', 'Student']:
        user.role = new_role

    user.is_active_account = is_active_account_val
    db.session.commit()

    flash(f'Updated user account for {user.full_name} ({user.username}). Role: {user.role}, Status: {"Active" if user.is_active_account else "Inactive"}.', 'success')
    return redirect(url_for('admin_users'))

# --------------------------------------------------------------------------
# Application Runner
# --------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
