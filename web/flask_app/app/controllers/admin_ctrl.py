from flask import redirect, url_for, render_template, request, flash, session, abort, jsonify, Response
from flask_argon2 import generate_password_hash
from datetime import datetime
from sqlalchemy.orm import joinedload
import pandas as pd
from io import BytesIO

from ..models import *

""" Function helper """
error_user_msg = []
error_course_msg = []

def validate_user_form(
  user_id:str, user_role:str, user_fullname:str, user_pw:str, user_confirm_pw:str, user_email_address:str, user_uid:str, user_home_address:str = None, student_class:str = None,
  lecturer_major:str = None, edit_mode:bool = False
  ) -> bool:
  is_valid = False
  # Check validation mode (edit/register)
  if not edit_mode:
    if not (user_id and user_fullname and user_pw and user_confirm_pw and user_email_address and user_uid):
      error_user_msg.append('Please fill all the form!')
    # Check if the user password is valid
    if len(user_pw) < 8:
      error_user_msg.append('Password must be at least 8 characters!')
    # Check if the password contains minimum 1 uppercase, 1 lowercase, 1 number, and 1 symbol
    if not (
      any(char.isupper() for char in user_pw) and 
      any(char.islower() for char in user_pw) and 
      any(char.isdigit() for char in user_pw) and 
      any(not char.isalnum() for char in user_pw)
    ):
      error_user_msg.append('Password must contain minimum 1 uppercase, 1 lowercase, 1 number, and 1 symbol!')
    if user_role == 'STUDENT':
      # Query to check if the student already registered
      student_exist = User.query.filter_by(
        user_id=user_id,
        user_role='STUDENT'
      ).first()
      if student_exist:
        error_user_msg.append('Student already registered!')
    elif user_role == 'LECTURER':
      # Query to check if the lecturer already registered
      lecturer_exist = User.query.filter_by(
        user_id=user_id,
        user_role='LECTURER'
      ).first()
      if lecturer_exist:
        error_user_msg.append('Lecturer already registered!')
  # If edit mode is set to True
  else:
    # Check if new user password is set
    if user_pw:
      # Then, check for the length of the password
      if len(user_pw) < 8:
        error_user_msg.append('Password must be at least 8 characters!')
      # Then, check if the password contains minimum 1 uppercase, 1 lowercase, 1 number, and 1 symbol
      if not (
        any(char.isupper() for char in user_pw) and 
        any(char.islower() for char in user_pw) and 
        any(char.isdigit() for char in user_pw) and 
        any(not char.isalnum() for char in user_pw)
      ):
        error_user_msg.append('Password must contain minimum 1 uppercase, 1 lowercase, 1 number, and 1 symbol!')
    if user_role == 'STUDENT':
      students = User.query.filter_by(user_role='STUDENT').all()
      students_nim = [
        student.user_id for student in students if student.user_id != user_id
      ]
      # Check if the student is exist except the student that want to be edited
      if user_id in students_nim:
        error_user_msg.append('Student already registered. Use different NIM!')
    elif user_role == 'LECTURER':
      lecturers = User.query.filter_by(user_role='LECTURER').all()
      lecturers_nip = [
        lecturer.user_id for lecturer in lecturers if lecturer.user_id != user_id
      ]
      # Check if the lecturer is exist except the lecturer that want to be edited
      if user_id in lecturers_nip:
        error_user_msg.append('Lecturer already registered. Use different NIP!')
  # Check if user confirm password is same as password
  if user_pw != user_confirm_pw:
    error_user_msg.append('Confirm password must be same as password!')
  # Check if user id contain space
  if (type(user_id) != int) and (" " in user_id):
    error_user_msg.append('User ID must not contain space!')
  # Validate user email address
  if not '@' in user_email_address:
    error_user_msg.append('Email address is not valid!')
  # Validate user home address
  if user_home_address:
    if len(user_home_address) > 256:
      error_user_msg.append('Home address must be less than 256 characters!')
  # Validate user role
  if user_role == 'STUDENT':
    # Check if the user id length is 10
    if len(user_id) != 10:
      error_user_msg.append('Student NIM must be 10 characters long!')
    # Check if the student class is valid
    student_class_exist = Class.query.filter_by(
      class_id=student_class
    ).first()
    if not student_class_exist:
      error_user_msg.append('Student class is not valid!')
  elif user_role == 'LECTURER':
    # Check if the lecturer nip length is 18
    if len(user_id) != 18:
      error_user_msg.append('Lecturer NIP must be 18 characters long!')
    # Check if the lecturer major is valid
    lecturer_major_list = [major.value for major in Major]
    if lecturer_major not in lecturer_major_list:
      error_user_msg.append('Lecturer major is not valid!')
  # Set is valid to True if there is no error message
  if not error_user_msg:
    is_valid = True
  # Return is_valid
  return is_valid

def is_valid_day(day: str) -> bool:
  days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  return day.capitalize() in days_of_week

def is_valid_time(time: str) -> bool:
  try:
    datetime.strptime(time, '%H:%M:%S')
    return True
  except ValueError:
    return False

def validate_course_form(
  course_id:str, course_name:str, course_sks:int, at_semester:int,
  day:str, time_start:str, time_end:str, course_description:str,
  lecturer_nip:str, class_id:str, room_id:str, edit_mode:bool=False
) -> bool:
  is_valid = False
  if not edit_mode:
    if not (course_id and course_name and course_sks and at_semester 
            and day and time_start and time_end
            and lecturer_nip and class_id and room_id
    ):
      error_course_msg.append('Please fill all the form!')
    # Check if course already registered
    course_exist = Course.query.filter_by(course_id=course_id).first()
    if course_exist:
      error_course_msg.append('Course already registered!')
  else:
    # Check if course already registered except the course that want to be edited
    courses =  [
      course.course_id for course in Course.query.all() if course.course_id != course_id
    ]
    if course_id in courses:
      error_course_msg.append('Course already registered. Use different course ID!')
  # Check if course_id contain space
  if (" " in course_id):
    error_course_msg.append('Course ID must not contain space!')
  if len(course_id) > 15:
    error_course_msg.append('Course ID must be less than 15 characters!')
  if len(course_name) > 100:
    error_course_msg.append('Course name must be less than 100 characters!')
  if not (isinstance(course_sks,int)) or (course_sks<1 or course_sks>=6):
    error_course_msg.append('Course SKS must be between 1 and 6!')
  if not (isinstance(at_semester,int)) or (at_semester<1 or at_semester>=8):
    error_course_msg.append('Course semester must be between 1 and 8!')
  if not is_valid_day(day):
    error_course_msg.append('Day must be a day of week!')
  if time_start == time_end:
    error_course_msg.append('Time start and time end must be different!')
  if not (is_valid_time(time_start) or is_valid_time(time_end)):
    error_course_msg.append('Time start or time end must be in format HH:MM AM/PM!')
  if course_description:
    if len(course_description) > 256:
      error_course_msg.append('Course description must be less than 256 characters!')
  # Check for lecturer NIP
  lecturer_exist = User.query.filter_by(
    user_id=lecturer_nip,
    user_role='LECTURER'
  ).first()
  if not lecturer_exist:
    error_course_msg.append('Lecturer NIP is not valid!')
  # Check for class ID
  class_exist = Class.query.filter_by(class_id=class_id).first()
  if not class_exist:
    error_course_msg.append('Class ID is not valid!')
  # Check for room ID
  room_exist = Room.query.filter_by(room_id=room_id).first()
  if not room_exist:
    error_course_msg.append('Room ID is not valid!')
  # Set is valid to True if there is no error message
  if not error_course_msg:
    is_valid = True
  # Return is_valid
  return is_valid

def format_time(time_object:datetime):
  formatted_time = time_object.strftime('%a, %d %b %Y %H:%M:%S')
  return formatted_time
""" End of function helper """

""" Registration """
def add():
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  # Check user session
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  # Check user role
  if sess_user_role != 'ADMIN':
    return abort(403)
  return render_template('admin/registrasi.html')

def add_student():
  global error_user_msg
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  # Check user session
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  # Check user role
  if sess_user_role != 'ADMIN':
    return abort(403)
  form = request.form
  student_class = Class.query.all()
  if request.method == 'POST':
    student_name = form['student_name']
    student_nim = form['student_nim']
    student_class = form['student_class']
    student_pw = form['student_pw']
    student_confirm_pw = form['student_confirm_pw']
    student_email_address = form['student_email_address']
    student_home_address = form['student_home_address'] or None
    student_uid = form['student_uid']
    # Validate user form
    is_form_valid = validate_user_form(
      user_id=student_nim, user_role='STUDENT', user_fullname=student_name, user_pw=student_pw, user_confirm_pw=student_confirm_pw, user_email_address=student_email_address, user_uid=student_uid, user_home_address=student_home_address, student_class=student_class
    )
    # Check if the form is valid
    if not is_form_valid:
      # Show to error message
      flash(error_user_msg, 'danger')
      # Clear the error messages after flashing
      error_user_msg = []
      return redirect(url_for('admin_ep.add_student'))
    # If the form valid, then add new student to database based on the form input
    new_student = User (
      user_id = student_nim,
      user_role = 'STUDENT',
      user_fullname = student_name,
      user_password_hash = generate_password_hash(student_pw),
      user_rfid = student_uid,
      user_email_address = student_email_address,
      user_home_address = student_home_address,
      student_class = student_class
    )
    # Add new student to database
    db.session.add(new_student)
    db.session.commit()
    flash('Student successfully registered!', 'success')
    return redirect(url_for('admin_ep.add'))
  return render_template(
    'admin/regis-mhsw.html',
    student_class=student_class
  )

def add_lecturer():
  global error_user_msg
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  # Check user session
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  # Check user role
  if sess_user_role != 'ADMIN':
    return abort(403)
  form = request.form
  major_list = [major.value for major in Major]
  if request.method == 'POST':
    lecturer_name = form['lecturer_name']
    lecturer_nip = form['lecturer_nip']
    lecturer_major = form['lecturer_major']
    lecturer_pw = form['lecturer_pw']
    lecturer_confirm_pw = form['lecturer_confirm_pw']
    lecturer_email_address = form['lecturer_email_address']
    lecturer_home_address = form['lecturer_home_address'] or None
    lecturer_uid = form['lecturer_uid']
    # Validate the user form
    is_form_valid = validate_user_form(
      user_id=lecturer_nip, user_role='LECTURER', user_fullname=lecturer_name, user_pw=lecturer_pw, user_confirm_pw=lecturer_confirm_pw, user_email_address=lecturer_email_address, user_uid=lecturer_uid, user_home_address=lecturer_home_address, lecturer_major=lecturer_major
    )
    if not is_form_valid:
      # Show to error message
      flash(error_user_msg, 'danger')
      # Clear the error messages after flashing
      error_user_msg = []
      return redirect(url_for('admin_ep.add_lecturer'))
    new_lecturer = User (
      user_id = lecturer_nip,
      user_role = 'LECTURER',
      user_fullname = lecturer_name,
      user_password_hash = generate_password_hash(lecturer_pw),
      user_rfid = lecturer_uid,
      user_email_address = lecturer_email_address,
      user_home_address = lecturer_home_address,
      lecturer_major = lecturer_major
    )
    db.session.add(new_lecturer)
    db.session.commit()
    flash('Lecturer successfully registered!', 'success')
    return redirect(url_for('admin_ep.add'))
  return render_template(
    'admin/regis-dosen.html',
    major_list=major_list
  )

def add_course():
  global error_course_msg
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  list_classes = Class.query.all()
  days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  lecturers = User.query.filter_by(user_role='LECTURER').all()
  rooms = Room.query.all()
  form = request.form
  if request.method == 'POST':
    course_name = form['course_name']
    course_id = form['course_id']
    course_sks = int(form['course_sks'])
    course_semester = int(form['course_semester'])
    course_day = form['course_day']
    course_start = form['time_start']
    course_end = form['time_end']
    course_description = form['course_description'] or None
    lecturer_nip = form['lecturer_nip']
    class_id = form['class_id']
    room_id = form['room_id']
    # Validate course form
    is_course_form_valid = validate_course_form(
      course_id=course_id, course_name=course_name, course_sks=course_sks, at_semester=course_semester, day=course_day, 
      time_start=course_start, time_end=course_end, course_description=course_description,
      lecturer_nip=lecturer_nip, class_id=class_id, room_id=room_id
    )
    # Check if the form is valid
    if not is_course_form_valid:
      flash(error_course_msg, 'danger')
      # Clear the error messages after flashing
      error_course_msg = []
      return redirect(url_for('admin_ep.add_course'))
    # If the form valid, then add new course to database based on the form input
    new_course = Course (
      course_id = course_id,
      course_name = course_name,
      course_sks = course_sks,
      at_semester = course_semester,
      day = course_day,
      time_start = course_start,
      time_end = course_end,
      course_description = course_description,
      lecturer_nip = lecturer_nip,
      class_id = class_id,
      room_id = room_id
    )
    # Add new course to database
    db.session.add(new_course)
    db.session.commit()
    flash('Course successfully registered!', 'success')
    return redirect(url_for('admin_ep.add'))
  return render_template(
    'admin/regis-course.html',
    list_classes=list_classes,
    days_of_week=days_of_week,
    lecturers=lecturers,
    rooms=rooms
  )
""" End of registration """

""" Courses """
def serialized_course(class_id:str = None):
  """
  This function is to serialize course data based on class_id.
  Required param: class_id (str)
  """
  serialized_courses = [] # Empty list to store serialized courses
  # Check if class id param is passed
  if class_id:
    # Query to get all the courses data based on class_id
    courses = (
      db.session.query(Course)
      .join(User, User.user_id == Course.lecturer_nip)
      .options(joinedload(Course.class_course))
      .filter(Course.class_id == class_id)
      .all()
    )
    # Serialize courses to JSON format
    serialized_courses = [
      {
        'course_id': course.course_id,
        'course_name': course.course_name,
        'lecturer': course.user_course.user_fullname,
        'total_students': len(course.class_course.courses),
        'course_sks': course.course_sks,
        'at_semester': course.at_semester,  # Added comma here
        'day': course.day,
        'time_start': str(course.time_start),
        'time_end': str(course.time_end),
        'course_description': course.course_description,
        'class_id': course.class_id,
        'room_id': course.room_id
      }
      for course in courses
    ]
  else:
    courses = (
    db.session.query(Course)
      .join(User, User.user_id == Course.lecturer_nip)
      .options(joinedload(Course.class_course))
    ).all()
    # Serialize all courses to JSON format
    serialized_courses = [
      {
        'course_id': course.course_id,
        'course_name': course.course_name,
        'lecturer': course.user_course.user_fullname,
        'total_students': len(course.class_course.courses),
        'course_sks': course.course_sks,
        'at_semester': course.at_semester,  # Added comma here
        'day': course.day,
        'time_start': str(course.time_start),
        'time_end': str(course.time_end),
        'course_description': course.course_description,
        'class_id': course.class_id,
        'room_id': course.room_id
      }
      for course in courses
    ]
  # Return the serialized courses
  return serialized_courses

def get_courses():
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  # Get class id from query param
  class_id = request.args.get('class_id', type=str)
  # Serialized course
  courses = serialized_course(class_id=class_id)
  # courses list to store serialized courses
  return jsonify({"courses": courses}), 200

def courses():
  """
  This is a view of course page
  No required param.
  """
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  classes = Class.query.all()
  return render_template(
    'admin/course.html',
    classes=classes
  )
""" End of courses """

""" Classes """
def classes():
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  classes = Class.query.all()
  total_students = {}
  for c in classes:
    count_students = User.query.filter_by(
      student_class=c.class_id,
      user_role='STUDENT'
    ).count()
    total_students[c.class_id] = count_students
  # Return class render template
  return render_template(
    'admin/class.html',
    classes=classes,
    total_students=total_students
  )
""" End of classes """

""" Attendance """
def serialized_logs(selected_role:str, selected_course_id:str=None, student_nim:str=None, lecturer_nip:str=None) -> list:
  """
  This function is for serializing or converting user attendance logs based on selected role and selected course id in JSON format.
  Required param: selected_role (str), and
  Optional params:
    - selected_course_id (str)
    - student_nim (str)
    - lecturer_nip (str)
  """
  # A list to store serialized logs (in JSON format)
  serialized_logs = []
  if selected_role == 'STUDENT':
    student_attendance_logs = db.session.query(StudentAttendanceLogs).options(
      joinedload(StudentAttendanceLogs.user_student),
      joinedload(StudentAttendanceLogs.course_student),
      joinedload(StudentAttendanceLogs.room_student)
    )
    # Check if course_id is passed in query string
    if selected_course_id:
      student_attendance_logs = student_attendance_logs.filter_by(course_id=selected_course_id)
    if student_nim:
      student_attendance_logs = student_attendance_logs.filter_by(student_nim=student_nim)
    # Get all student attendance logs
    student_attendance_logs = student_attendance_logs.all()
    # Serialize student attendance logs
    serialized_logs = [
      {
        'log_id': log.log_id,
        'nim': log.user_student.user_id,
        'name': log.user_student.user_fullname,
        'course': log.course_student.course_name,
        'room': log.room_student.room_id,
        'time_in': format_time(log.time_in),
        'status': log.status.value
      }
      for log in student_attendance_logs
    ]
  elif selected_role == 'LECTURER':
    lecturer_attendance_logs = db.session.query(LecturerAttendanceLogs).options(
      joinedload(LecturerAttendanceLogs.user_lecturer),
      joinedload(LecturerAttendanceLogs.course_lecturer),
      joinedload(LecturerAttendanceLogs.room_lecturer)
    )
    # Check if course_id is passed in query string
    if selected_course_id:
      lecturer_attendance_logs = lecturer_attendance_logs.filter_by(course_id=selected_course_id)
    if lecturer_nip:
      lecturer_attendance_logs = lecturer_attendance_logs.filter_by(lecturer_nip=lecturer_nip)
    # Get all lecturer attendance logs
    lecturer_attendance_logs = lecturer_attendance_logs.all()
    # Serialize lecturer attendance logs
    serialized_logs = [
      {
        'log_id': log.log_id,
        'nip': log.user_lecturer.user_id,
        'name': log.user_lecturer.user_fullname,
        'course': log.course_lecturer.course_name,
        'room': log.room_lecturer.room_id,
        'time_in': format_time(log.time_in),
        'status': log.status.value
      }
      for log in lecturer_attendance_logs
    ]
  else:
    return jsonify({'message': 'User role is not valid!'}), 400
  # Return the serialized attendance logs
  return serialized_logs

def get_attendance(selected_role:str):
  """
  This function is to send response to the client (JS) in JSON format, which contains attendance logs data.
  Required param: selected_role (str)
  """
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  # If the selected role is student
  if selected_role in ['STUDENT', 'LECTURER']:
    selected_course_id = request.args.get('course_id', type=str)
    # Check if user pass course_id in query string
    if selected_course_id:
      attendance_logs = serialized_logs(selected_role=selected_role, selected_course_id=selected_course_id)
    # If not, then fetch all attendance logs
    else:
      attendance_logs = serialized_logs(selected_role=selected_role)
    return jsonify({'attendance': attendance_logs}), 200
  else:
    return jsonify({'message': 'User role is invalid'}), 400

def view_attendance():
  """
  This is a view page of attendance logs.
  No param required.
  """
  # Get the user session
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  # Check for user session
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  # Check if the session of user_role is admin or not
  if sess_user_role != 'ADMIN':
    return abort(403)
  roles = ['STUDENT', 'LECTURER']
  courses = Course.query.all()
  return render_template(
    'admin/rekap_absen.html',
    roles=roles,
    courses=courses
  )

def export_attendance(selected_role:str):
  """
  This function is to export attendance logs data to excel file.
  Required param: selected_role (str)
  """
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  if selected_role in ['STUDENT', 'LECTURER']:
    selected_course_id = request.args.get('course_id', type=str)
    student_nim = request.args.get('nim', type=str)
    lecturer_nip = request.args.get('nip', type=str)
    if selected_course_id:
      attendance_logs = serialized_logs(selected_role=selected_role, selected_course_id=selected_course_id)
    elif student_nim:
      attendance_logs = serialized_logs(selected_role=selected_role, student_nim=student_nim)
    elif lecturer_nip:
      attendance_logs = serialized_logs(selected_role=selected_role, lecturer_nip=lecturer_nip)
    else:
      attendance_logs = serialized_logs(selected_role=selected_role)
  # Create dataframe from serialized logs
  df = pd.DataFrame(attendance_logs)
  # Create a BytesIO buffer to store the Excel file
  excel_buffer = BytesIO()
  # Export dataframe to excel_buffer
  df.to_excel(excel_buffer, index=False, header=True)
  # Set the position of the buffer to the beginning
  excel_buffer.seek(0)
  # Create response object
  response = Response(
    excel_buffer.read(),
    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  )
  output_file = f"{selected_role.lower()}_attendance_logs.xlsx"
  # Add headers to response
  response.headers["Content-Disposition"] = f"attachment; filename={output_file}"
  # Return response
  return response

def get_attendance_detail(selected_role:str):
  """
  This function is to send response to the client (JS) in JSON format, which contains spesific user attendance logs data.
  Required param: selected_role (str)
  """
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  if selected_role in ['STUDENT', 'LECTURER']:
    student_nim = request.args.get('nim')
    lecturer_nip = request.args.get('nip')
    # Check if nim is passed in query string
    if student_nim:
      student_attendance_logs = serialized_logs(selected_role=selected_role, student_nim=student_nim)
      return jsonify({'attendance_detail': student_attendance_logs}), 200
    # If the lecturer nip is passed in query string
    elif lecturer_nip:
      lecturer_attendance_logs = serialized_logs(selected_role=selected_role, lecturer_nip=lecturer_nip)
      return jsonify({'attendance_detail': lecturer_attendance_logs}), 200
    # Otherwise, return parameter error if the nim or nip is not passed in query string
    else:
      return jsonify({"message": "You've to provide the student nim or lecturer nip in query parameters"}), 400
  # Return role error if the selected role is not student or lecturer
  return jsonify({"message": "User role is invalid"}), 400

def view_attendance_detail(selected_role:str):
  """
  This is a view page of attendance logs detail.
  Required param: selected_role (str)
  """
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  if selected_role in ['STUDENT', 'LECTURER']:
    # Get the value of nim or nip from query string
    student_nim = request.args.get('nim')
    lecturer_nip = request.args.get('nip')
    # Check the student nim or lecturer nip is exist in the database
    found_student = User.query.filter_by(user_id=student_nim, user_role='STUDENT').first()
    found_lecturer = User.query.filter_by(user_id=lecturer_nip, user_role='LECTURER').first()
    # If the student nim or lecturer nip is not exist, then return error message
    if not (found_student or found_lecturer):
      flash("Student or lecturer not found!", 'danger')
      return redirect(url_for('admin_ep.attendance'))
    # If the student nim is passed in query string and the student is exist in the database, then return the student attendance detail page
    if student_nim and found_student:
      return render_template(
        'admin/student-attendance-detail.html',
        student=found_student
      )
    # If the lecturer nip is passed in query string and the lecturer is exist in the database, then return the lecturer attendance detail page
    elif lecturer_nip and found_lecturer:
      return render_template(
        'admin/lecturer-attendance-detail.html',
        lecturer=found_lecturer
      )
    # Otherwise, return parameter error if the nim or nip is not passed in query string
    else:
      flash("You've to provide the student nim or lecturer nip in query parameters", 'danger')
      return redirect(url_for('admin_ep.attendance'))
  # Otherwise, return role error if the selected role is not student or lecturer
  flash("User role is invalid!")
  return redirect(url_for('admin_ep.attendance'))
""" End of attendance """

""" Edit action """
def edit_student(nim:str):
  global error_user_msg
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  # Query to check if the student exists
  found_student = User.query.filter_by(
    user_id=nim,
    user_role='STUDENT'
  ).first()
  # If the student not found
  if not found_student:
    flash('Student not found', 'danger')
    return redirect(url_for('user_ep.dashboard'))
  form = request.form
  if request.method == 'POST':
    student_nim = form['student_nim']
    student_class = form['student_class']
    student_name = form['student_name']
    student_pw = form['student_pw']
    student_confirm_pw = form['student_confirm_pw']
    student_uid = form['student_uid']
    student_email_address = form['student_email_address']
    student_home_address = form['student_home_address'] or None
    # Validate edit student form
    is_valid_form = validate_user_form(
      user_id=student_nim, user_role='STUDENT', user_fullname=student_name, user_pw=student_pw, user_confirm_pw=student_confirm_pw, user_email_address=student_email_address, user_uid=student_uid, user_home_address=student_home_address, student_class=student_class,
      edit_mode=True
    )
    # Check if form submit is valid
    if not is_valid_form:
      flash(error_user_msg, 'danger')
      # Clear the error messages after flashing
      error_user_msg = []
      return redirect(url_for('user_ep.dashboard'))
    try:
      found_student.user_fullname = student_name
      # If the field student_pw is not empty, then generate the password hash
      if student_pw != "":
        found_student.user_password_hash = generate_password_hash(student_pw)
      # Same thing with the student_uid
      if student_uid != "":
        found_student.user_rfid = student_uid
      found_student.user_email_address = student_email_address
      found_student.user_home_address = student_home_address
      db.session.commit()
      flash('Update student data success', 'success')
    except Exception as err:
      flash(f'Update student data error. {err}', 'danger')
  return redirect(url_for('user_ep.dashboard'))

def edit_lecturer(nip:str):
  global error_user_msg
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  # Query to check if the student exists
  found_lecturer = User.query.filter_by(
    user_id=nip,
    user_role='LECTURER'
  ).first()
  # If the student not found
  if not found_lecturer:
    flash('Lecturer not found', 'danger')
    return redirect(url_for('user_ep.dashboard'))
  form = request.form
  if request.method == 'POST':
    lecturer_nip = form['lecturer_nip']
    lecturer_major = form['lecturer_major']
    lecturer_name = form['lecturer_name']
    lecturer_pw = form['lecturer_pw']
    lecturer_confirm_pw = form['lecturer_confirm_pw']
    lecturer_uid = form['lecturer_uid']
    lecturer_email_address = form['lecturer_email_address']
    lecturer_home_address = form['lecturer_home_address'] or None
    # Validate edit student form
    is_valid_form = validate_user_form(
      user_id=lecturer_nip, user_role='LECTURER', user_fullname=lecturer_name, user_pw=lecturer_pw, user_confirm_pw=lecturer_confirm_pw, user_email_address=lecturer_email_address, user_uid=lecturer_uid, user_home_address=lecturer_home_address, lecturer_major=lecturer_major,
      edit_mode=True
    )
    # Check if form submit is valid
    if not is_valid_form:
      flash(error_user_msg, 'danger')
      # Clear the error messages after flashing
      error_user_msg = []
      return redirect(url_for('user_ep.dashboard'))
    try:
      found_lecturer.user_fullname = lecturer_name
      # If the field lecturer_pw is not empty, then generate the password hash
      if lecturer_pw != "":
        found_lecturer.user_password_hash = generate_password_hash(lecturer_pw)
      # Same thing with the lecturer_uid
      if lecturer_uid != "":
        found_lecturer.user_rfid = lecturer_uid
      found_lecturer.user_email_address = lecturer_email_address
      found_lecturer.user_home_address = lecturer_home_address
      db.session.commit()
      flash('Update lecturer data success', 'success')
    except Exception as err:
      flash(f'Update lecturer data error. {err}', 'danger')
  return redirect(url_for('user_ep.dashboard'))

def edit_course(course_id:str):
  global error_course_msg
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  found_course = Course.query.filter_by(course_id=course_id).first()
  if not found_course:
    flash('Course not found', 'danger')
    return redirect(url_for('admin_ep.courses'))
  form = request.form
  if request.method == 'POST':
    course_name = form['course_name']
    course_sks = int(form['course_sks'])
    course_semester = int(form['course_semester'])
    course_day = form['course_day']
    course_time_start = form['course_time_start']
    course_time_end = form['course_time_end']
    course_description = form['course_description'] or None
    course_lecturer = form['course_lecturer']
    course_class = form['course_class']
    course_room = form['course_room']
    # Get nim of course lecturer
    lecturer_nip = User.query.filter_by(user_fullname=course_lecturer).first().user_id
    # Validate the course edit form
    is_valid_course_form = validate_course_form(
      course_id=course_id, course_name=course_name, course_sks=course_sks, at_semester=course_semester, day=course_day, 
      time_start=course_time_start, time_end=course_time_end, course_description=course_description,
      lecturer_nip=lecturer_nip, class_id=course_class, room_id=course_room,
      edit_mode=True
    )
    # Check if the form is valid
    if not is_valid_course_form:
      flash(error_course_msg, 'danger')
      # Clear the error messages after flashing
      error_course_msg = []
      return redirect(url_for('admin_ep.courses'))
    # If the form valid, then update the course data based on the form input
    try:
      found_course.course_name = course_name
      found_course.course_sks = course_sks
      found_course.at_semester = course_semester
      found_course.day = course_day
      found_course.time_start = course_time_start
      found_course.time_end = course_time_end
      found_course.course_description = course_description
      found_course.lecturer_nip = lecturer_nip
      found_course.class_id = course_class
      found_course.room_id = course_room
      db.session.commit()
      flash('Update course data success!', 'success')
    except Exception as err:
      flash(f'Update course data failed. {err}!', 'danger')
  return redirect(url_for('admin_ep.courses'))
""" End of edit action """


""" Delete action """
def delete_student(nim:str):
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  found_student = User.query.filter_by(
    user_id=nim,
    user_role='STUDENT'
  ).first()
  if not found_student:
    flash('Student not found', 'danger')
    return redirect(url_for('user_ep.dashboard'))
  if request.method == 'POST':
    try:
      db.session.delete(found_student)
      db.session.commit()
      flash('Delete student data success!', 'success')
    except Exception as err:
      flash(f'Delete student data failed. {err}!', 'danger')
  return redirect(url_for('user_ep.dashboard'))

def delete_lecturer(nip:str):
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  found_lecturer = User.query.filter_by(
    user_id=nip,
    user_role='LECTURER'
  ).first()
  if not found_lecturer:
    flash('Lecturer not found', 'danger')
    return redirect(url_for('user_ep.dashboard'))
  if request.method == 'POST':
    try:
      db.session.delete(found_lecturer)
      db.session.commit()
      flash('Delete lecturer data success!', 'success')
    except Exception as err:
      flash(f'Delete lecturer data failed. {err}!', 'danger')
  return redirect(url_for('user_ep.dashboard'))

def delete_course(course_id:str):
  global error_user_msg
  sess_user_id = session.get('user_id')
  sess_user_role = session.get('user_role')
  if not (sess_user_id and sess_user_role):
    return redirect(url_for('user_ep.login'))
  if sess_user_role != 'ADMIN':
    return abort(403)
  found_course = Course.query.filter_by(course_id=course_id).first()
  if not found_course:
    flash('Course not found', 'danger')
    return redirect(url_for('admin_ep.courses'))
  if request.method == 'POST':
    try:
      db.session.delete(found_course)
      db.session.commit()
      flash('Delete course data success!', 'success')
    except Exception as err:
      flash(f'Delete course data failed. {err}!', 'danger')
  return redirect(url_for('admin_ep.courses'))
""" End of delete action """
