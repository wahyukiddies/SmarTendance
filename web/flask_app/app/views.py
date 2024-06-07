from flask import Blueprint

from .controllers.user_ctrl import *
from .controllers.admin_ctrl import *
from .controllers.lecturer_ctrl import *
from .controllers.student_ctrl import *

# Creating endpoint blueprints for each user (from general to specific)
user_ep = Blueprint('user_ep', __name__)
admin_ep = Blueprint('admin_ep', __name__, url_prefix='/admin')
lecturer_ep = Blueprint('lecturer_ep', __name__, url_prefix='/lecturer')
student_ep = Blueprint('student_ep', __name__, url_prefix='/student')

# List of user endpoints (general routes)
user_ep.add_url_rule('/', endpoint="index", view_func=index, methods=['GET'])
user_ep.add_url_rule('/login', endpoint="login", view_func=login, methods=['GET', 'POST'])
user_ep.add_url_rule('/logout', endpoint="logout", view_func=logout, methods=['GET'])
user_ep.add_url_rule('/dashboard', endpoint="dashboard", view_func=dashboard, methods=['GET'])

""" List of admin endpoints (admin routes) """
# Action for registation (insert/add)
admin_ep.add_url_rule('/add', endpoint="add", view_func=add, methods=['GET'])
admin_ep.add_url_rule('/add/student', endpoint="add_student", view_func=add_student, methods=['GET', 'POST'])
admin_ep.add_url_rule('/add/lecturer', endpoint="add_lecturer", view_func=add_lecturer, methods=['GET', 'POST'])
admin_ep.add_url_rule('/add/course', endpoint="add_course", view_func=add_course, methods=['GET', 'POST'])

# Action for view course
admin_ep.add_url_rule('/courses/get', endpoint="get_courses", view_func=get_courses, methods=['GET'])
admin_ep.add_url_rule('/courses', endpoint="courses", view_func=courses, methods=['GET'])

# Action for view class
admin_ep.add_url_rule('/classes', endpoint="classes", view_func=classes, methods=['GET'])

# Action for attendance
admin_ep.add_url_rule('/attendance', endpoint="view_attendance", view_func=view_attendance, methods=['GET'])
admin_ep.add_url_rule('/attendance/<string:selected_role>/get', endpoint="get_attendance", view_func=get_attendance, methods=['GET'])
admin_ep.add_url_rule('/attendance/<string:selected_role>/export', endpoint="export_attendance", view_func=export_attendance, methods=['GET'])
admin_ep.add_url_rule('/attendance/<string:selected_role>/get_detail', endpoint="get_attendance_detail", view_func=get_attendance_detail, methods=['GET'])
admin_ep.add_url_rule('/attendance/<string:selected_role>/detail', endpoint="view_attendance_detail", view_func=view_attendance_detail, methods=['GET'])

# Action for edit
# edit student
admin_ep.add_url_rule('/<string:nim>/edit/student', endpoint="edit_student", view_func=edit_student, methods=['GET', 'POST'])
# edit lecturer
admin_ep.add_url_rule('/<string:nip>/edit/lecturer', endpoint="edit_lecturer", view_func=edit_lecturer, methods=['GET', 'POST'])
# edit course
admin_ep.add_url_rule('/<string:course_id>/edit/course', endpoint="edit_course", view_func=edit_course, methods=['GET', 'POST'])

# Action for delete
# delete student
admin_ep.add_url_rule('/<string:nim>/delete/student', endpoint="delete_student", view_func=delete_student, methods=['GET', 'POST'])
# delete lecturer
admin_ep.add_url_rule('/<string:nip>/delete/lecturer', endpoint="delete_lecturer", view_func=delete_lecturer, methods=['GET', 'POST'])
# delete course
admin_ep.add_url_rule('/<string:course_id>/delete/course', endpoint="delete_course", view_func=delete_course, methods=['GET', 'POST'])

""" List of lecturer endpoints (lecturer routes) """

# lecturer attendance logs
lecturer_ep.add_url_rule('/logs', endpoint="view_lecturer_logs", view_func=view_lecturer_logs, methods=['GET'])
lecturer_ep.add_url_rule('/logs/get', endpoint="get_lecturer_logs", view_func=get_lecturer_logs, methods=['GET'])
lecturer_ep.add_url_rule('/logs/export', endpoint="export_lecturer_attendance", view_func=export_lecturer_logs, methods=['GET'])
# edit lecturer attendance
# lecturer_ep.add_url_rule('/logs/<string:log_id>/edit')

# student attendance logs
lecturer_ep.add_url_rule('/student_logs', endpoint="view_student_data", view_func=view_student_data, methods=['GET'])
lecturer_ep.add_url_rule('/student_logs/<string:course_id>/students_data', endpoint="get_student_data", view_func=get_student_data, methods=['GET'])
lecturer_ep.add_url_rule('/students_logs/<string:selected_course>/get', endpoint="get_data_student", view_func=get_student_data, methods=['GET'])

lecturer_ep.add_url_rule('/logs/<string:course_id>/student/get', endpoint='get_student_logs', view_func=get_student_logs, methods=['GET'])

lecturer_ep.add_url_rule('/logs/<string:course_id>/student', endpoint="view_student_logs", view_func=view_student_logs, methods=['GET'])


# List of student endpoints (student routes)
# Student only can view their attendance
student_ep.add_url_rule('/course', endpoint="course", view_func=course, methods=['GET', 'POST'])
student_ep.add_url_rule('/dashboard', endpoint="dashboard", view_func=student_dashboard, methods=['GET', 'POST'])

# Action student for attendance
student_ep.add_url_rule('/attendance', endpoint="view_attendance", view_func=view_attendance_student, methods=['GET'])
student_ep.add_url_rule('/attendance/<string:selected_course>/get', endpoint="get_attendance", view_func=get_attendance_student, methods=['GET'])
student_ep.add_url_rule('/attendance/<string:selected_course>/get_detail', endpoint="get_attendance_detail", view_func=get_attendance_detail_student, methods=['GET'])
student_ep.add_url_rule('/attendance/<string:selected_course>/detail', endpoint="view_attendance_detail", view_func=view_attendance_detail_student, methods=['GET'])
