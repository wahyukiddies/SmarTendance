from flask import redirect, url_for, render_template, request, flash, session

from ..models import User, Course, Class

def index():
  return redirect(url_for('user_ep.login'))

def login():
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if sess_user_id and sess_user_role:
    return redirect(url_for('user_ep.dashboard'))
  # create login form
  form = request.form
  if request.method == 'POST':
    user_id = form['user_id']
    user_pw = form['user_pw']
    # Check for existing user
    found_user = User.query.filter_by(user_id=user_id).first()
    if found_user and found_user.verify_password(user_pw):
      session['user_id']=found_user.user_id
      session['user_role']=found_user.user_role.value
      flash('Login success!', 'success')
      return redirect(url_for('user_ep.dashboard'))
    else:
      flash('Login failed. Invalid id or password!', 'danger')
      return redirect(url_for('user_ep.login'))
  return render_template('user/login.html')

def dashboard():
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role == 'ADMIN':
    admin = User.query.filter_by(user_id=sess_user_id, user_role='ADMIN').first()
    students = User.query.filter_by(user_role='STUDENT').all()
    lecturers = User.query.filter_by(user_role='LECTURER').all()
    total_students = len(students)
    total_lecturers = len(lecturers)
    total_courses = len(Course.query.all())
    total_classes = len(Class.query.all())
    # Get total course each student
    student_courses = {}
    for student in students:
      student_courses[student.user_id] = len(
        Course.query.filter_by(class_id=student.student_class).all()
      )
    lecturer_courses = {}
    for lecturer in lecturers:
      lecturer_courses[lecturer.user_id] = len(
        Course.query.filter_by(lecturer_nip=lecturer.user_id).all()
      )
    return render_template(
      'admin/index.html',
      admin=admin,
      students=students,
      lecturers=lecturers,
      total_students=total_students,
      total_lecturers=total_lecturers,
      total_courses=total_courses,
      total_classes=total_classes,
      student_courses=student_courses,
      lecturer_courses=lecturer_courses
    )
  elif sess_user_role == 'LECTURER':
    lecturer = User.query.filter_by(user_id=sess_user_id, user_role='LECTURER').first()
    courses = Course.query.filter_by(lecturer_nip=lecturer.user_id).all()
    students = (
      User.query
        .join(Class, User.student_class == Class.class_id)
        .join(Course, Course.class_id == Class.class_id)
        .filter(Course.course_id.in_([course.course_id for course in courses]))
        .all()
    )
    
    total_classes = (
        Course.query
        .filter_by(lecturer_nip=sess_user_id)
        .distinct(Course.class_id)
        .count()
    )
    total_students = (
        User.query
        .filter((User.user_role == 'STUDENT') & (User.student_class == Course.class_id))
        .filter(Course.lecturer_nip == sess_user_id)
        .count()
    )
    total_courses = Course.query.filter_by(lecturer_nip=sess_user_id).count()
    # Menginisialisasi dictionary untuk menyimpan data student_courses
    student_courses = {}
    # Iterasi untuk setiap course yang diajarkan oleh lecturer
    for course in courses:
      # Mengambil mahasiswa yang mengikuti kursus tertentu
      students = (
        User.query
          .join(Class, User.student_class == Class.class_id)
          .join(Course, Course.class_id == Class.class_id)
          .filter(Course.course_id == course.course_id)
          .all()
      )
      # Menambahkan data ke dictionary student_courses
      student_courses[course.course_id] = {
        'course_name': course.course_name,
        'students': students
      }
    return render_template(
        'lecturer/index.html',
        lecturer=lecturer, students=students, courses=courses,
        total_courses=total_courses,
        total_classes=total_classes,
        total_students=total_students,
        student_courses=student_courses
    )
  else:
    student = User.query.filter_by(user_id=sess_user_id).first()
    return render_template('student/index.html', student=student)

def logout():
  session.pop('user_id', None)
  session.pop('user_role', None)
  flash('Logout success!', 'success')
  return redirect(url_for('user_ep.login'))