from flask import redirect, url_for, render_template, request, flash, session, abort, jsonify, Response
from flask_argon2 import generate_password_hash
from datetime import datetime
from sqlalchemy.orm import joinedload

from ..models import *

""" Function helper """
def student_dashboard():
    sess_user_id = session.get('user_id')
    sess_user_role = session.get('user_role')

    # Check for user session
    if not (sess_user_id and sess_user_role):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user_ep.dashboard'))

    # Fetch student information
    student = User.query.filter_by(user_id=sess_user_id).first()

    # Check if student exists
    if not student:
        flash('Student not found!', 'danger')
        return redirect(url_for('user_ep.dashboard'))

    # Fetch student courses
    student_courses = Course.query.filter_by(class_id=student.student_class).all()

    # Check if there are courses for the student
    if not student_courses:
        flash('No courses found for the student!', 'warning')
        return render_template('student/index.html', student=student, student_courses=[], lecturer=None, attendance_data={})

    # Fetch lecturer information for the courses
    lecturers_nip = [course.lecturer_nip for course in student_courses]
    lecturer = User.query.filter(User.user_id.in_(lecturers_nip), User.user_role == 'LECTURER').first()

    # Fetch student attendance logs for each course
    attendance_data = {}
    for course in student_courses:
        attendance_logs = StudentAttendanceLogs.query.filter_by(student_nim=student.user_id, course_id=course.course_id).all()
        attendance_data[course.course_id] = attendance_logs

    return render_template('student/index.html', student=student, student_courses=student_courses, lecturer=lecturer, attendance_data=attendance_data)

        
def course():
    sess_user_id = session.get('user_id')
    sess_user_role = session.get('user_role')

    if not (sess_user_id and sess_user_role and sess_user_role == 'STUDENT'):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('student/course.html')

    
""" Attendance """
def format_time(time_object: datetime):
    formatted_time = time_object.strftime('%a, %d %b %Y %H:%M:%S')
    return formatted_time
""" End of function helper """

def serialized_logs(student_nim:str, selected_course_id:str) -> list:
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
  student_attendance_logs = db.session.query(StudentAttendanceLogs).options(
    joinedload(StudentAttendanceLogs.user_student),
    joinedload(StudentAttendanceLogs.course_student),
    joinedload(StudentAttendanceLogs.room_student)
  )
  student_attendance_logs = student_attendance_logs.filter_by(
    student_nim=student_nim,
    course_id=selected_course_id
  ).all()
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
  # Return the serialized attendance logs
  return serialized_logs

def get_attendance_student(selected_course:str):
    """
    This function is to send response to the client (JS) in JSON format, which contains attendance logs data.
    """
    sess_user_id = session.get('user_id')
    sess_user_role = session.get('user_role')
    if not (sess_user_id and sess_user_role):
      return redirect(url_for('user_ep.login'))
    if sess_user_role != 'STUDENT':
      return abort(403)
    # Check if user pass course_id in query string
    if not selected_course:
      return jsonify({'message': 'Course not found'}), 404
    attendance_logs = serialized_logs(
      student_nim=sess_user_id,
      selected_course_id=selected_course
    )
    return jsonify({'attendance': attendance_logs}), 200


def view_attendance_student():
    """
    This is a view page of attendance logs.
    No param required.
    """
    # Get the user session
    sess_user_id = session.get('user_id')
    sess_user_role = session.get('user_role')
    # Check for user session
    if not (sess_user_id and sess_user_role):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('user_ep.dashboard'))
    if sess_user_role != 'STUDENT':
      return abort(403)
    student = User.query.filter_by(
      user_id=sess_user_id,
      user_role=sess_user_role
    ).first()
    courses = Course.query.filter_by(class_id=student.student_class).all()
    return render_template(
        'student/rekap_absen.html',
        courses=courses
    )

def get_attendance_detail_student(selected_role:str):
    """
    This function is to send response to the client (JS) in JSON format, which contains specific user attendance logs data.
    """
    sess_user_id = session.get('user_id')
    sess_user_role = session.get('user_role')
    if not (sess_user_id and sess_user_role and sess_user_role == 'STUDENT'):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
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

def view_attendance_detail_student():
    """
    This is a view page of attendance logs detail.
    """
    sess_user_id = session.get('user_id')
    sess_user_role = session.get('user_role')

    if not (sess_user_id and sess_user_role and sess_user_role == 'STUDENT'):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    student_nim = request.args.get('nim')

    # Check the student nim or lecturer nip is exist in the database
    found_student = User.query.filter_by(user_id=student_nim, user_role='STUDENT').first()

    # If the student nim or lecturer nip is not exist, then return error message
    if not (found_student):
        flash("Student or lecturer not found!", 'danger')
        return redirect(url_for('student_ep.attendance'))

    # Jika ditemukan mahasiswa dan nim diberikan, tampilkan halaman detail mahasiswa
    if student_nim and found_student:
        return render_template('student/student-attendance-detail.html', student=found_student)

    # Otherwise, return parameter error if the nim or nip is not passed in query string
    else:
        flash("You've to provide the student nim or lecturer nip in query parameters")
        return redirect(url_for('student_ep.attendance'))

    flash("User role is invalid!")
    return redirect(url_for('student_ep.attendance'))
