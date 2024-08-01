from flask import Flask
from datetime import datetime, timedelta
import pytz

from .config import TestingConfig, ProductionConfig
from .extensions import argon2, db, migrate, csrf, mqtt
from .app.views import user_ep, admin_ep, lecturer_ep, student_ep
from .app.models import *

LOCAL_TZ = 'Asia/Jakarta'
# AttendanceFinal topic.
SUB_TOPIC = 'Smartendance/ESP8266/AttendanceFinal'
PUB_TOPIC = 'Smartendance/ESP8266/AttendanceFinal/Response'

# Activate/Deactivate class topic.
# SUB_TOPIC2 = 'Smartendance/ESP32/ActivateClass'
# PUB_TOPIC2 = 'Smartendance/ESP32/ActivateClass/Response'

def get_current_daytime():
  local_timezone = pytz.timezone(LOCAL_TZ)
  return datetime.now(local_timezone)

def get_current_time():
  local_timezone = pytz.timezone(LOCAL_TZ)
  return datetime.now(local_timezone).time()

def get_current_day():
  local_timezone = pytz.timezone(LOCAL_TZ)
  return datetime.now(local_timezone).strftime("%A")

def create_app(testing: bool):
  app = Flask(__name__)
  app.permanent_session_lifetime = timedelta(hours=1.5)
  app.url_map.strict_slashes = False

  # Check for testing parameter value.
  if testing:
    app.config.from_object(TestingConfig)
  else:
    app.config.from_object(ProductionConfig)

  # Connecting extensions to flask app
  argon2.init_app(app)
  db.init_app(app)
  migrate.init_app(app, db)
  csrf.init_app(app)
  mqtt.init_app(app)

  # Handle MQTT connection
  @mqtt.on_connect()
  def handle_connect(client, userdata, flags, rc):
    if rc == 0:
      print("Connected to broker")
      mqtt.subscribe(SUB_TOPIC, qos=0)
    else:
      print("Failed to connect, return code %d\n", rc)

  # Function to take attendance (store attendance to db)
  def do_attendance(uid: str) -> bool:
    current_time = get_current_time() # hh:mm:ss
    current_day = get_current_day() # Monday, Tuesday, etc.
    current_daytime = get_current_daytime() # yyyy-mm-dd hh:mm:ss

    # Query user with the given rfid
    found_user = User.query.filter_by(user_rfid=uid).first()

    # Exit if user not found
    if not found_user:
      message = f"101 - User not found"
      mqtt.publish(PUB_TOPIC, payload=message, qos=0)
      print(message)
      return False
    
    # Empty list to store student and lecturer courses
    found_course = []
    
    # Check the user's class id
    if found_user.user_role.value == "STUDENT":
      found_course = Course.query.filter(
        Course.class_id==found_user.student_class,
        Course.day==current_day,
        Course.time_start<=current_time,
        Course.time_end>current_time
      ).first()

      # Exit if course not found
      if not found_course:
        message = f"102 - Course not found"
        mqtt.publish(PUB_TOPIC, payload=message, qos=0)
        print(message)
        return False
      

      # Time variables for checking attendance status and exception
      time_start_with_date = datetime.combine(current_daytime, found_course.time_start)
      time_end_with_date = datetime.combine(current_daytime, found_course.time_end)
      time_start_with_delta_present = (datetime.combine(datetime.today(), found_course.time_start) + timedelta(minutes=30)).time()
      time_start_with_delta_late = (datetime.combine(datetime.today(), found_course.time_start) + timedelta(minutes=60)).time()

      print("Time:")
      print(f"Found course: {found_course}")
      print(f"Current day: {current_day}")
      print(f"Current time: {current_time}")
      print(f"Course time start: {found_course.time_start}")
      print(f"Course time end: {found_course.time_end}")
      print(f"Course time start with date: {time_start_with_date}")
      print(f"Course time end with date: {time_end_with_date}")
      print(f"Time start with delta present: {time_start_with_delta_present}")
      print(f"Time start with delta late: {time_start_with_delta_late}")
      print("End Time")

      # Check if the user has already attended the course
      found_student_log = StudentAttendanceLogs.query.filter(
        StudentAttendanceLogs.student_nim==found_user.user_id,
        StudentAttendanceLogs.course_id==found_course.course_id,
        StudentAttendanceLogs.time_in.between(time_start_with_date, time_end_with_date)
      ).first()

      if found_student_log:
        message = f"103 - Already attended"
        mqtt.publish(PUB_TOPIC, payload=message, qos=0)
        print(message)
        return False

      status = "ALPHA"

      # PRESENT if under 30 minutes after time_start
      if current_time > found_course.time_start and current_time < found_course.time_end and current_time < time_start_with_delta_present:
        status = "PRESENT"

      # LATE if under 60 minutes after time_start
      elif current_time > found_course.time_start and current_time < found_course.time_end and current_time < time_start_with_delta_late:
        status = "LATE"

      print(f"Status: {status}")

      new_student_log = StudentAttendanceLogs (
        student_nim=found_user.user_id,
        course_id=found_course.course_id,
        room_id=found_course.room_id,
        time_in=current_daytime,
        status=status
      )
      db.session.add(new_student_log)
      db.session.commit()

    # Check the user's lecturer nip (next)
    elif found_user.user_role.value == "LECTURER":
      found_course = Course.query.filter(
        Course.lecturer_nip==found_user.user_id,
        Course.day==current_day,
        Course.time_start<=current_time,
        Course.time_end>current_time
      ).first()

      # Exit if course not found
      if not found_course:
        message = f"102 - Course not found"
        mqtt.publish(PUB_TOPIC, payload=message, qos=0)
        print(message)
        return False
      
      # Time variables for checking attendance status and exception
      time_start_with_date = datetime.combine(current_daytime, found_course.time_start)
      time_end_with_date = datetime.combine(current_daytime, found_course.time_end)
      time_start_with_delta_present = (datetime.combine(datetime.today(), found_course.time_start) + timedelta(minutes=30)).time()
      time_start_with_delta_late = (datetime.combine(datetime.today(), found_course.time_start) + timedelta(minutes=60)).time()

      print("Time:")
      print(f"Found course: {found_course}")
      print(f"Current day: {current_day}")
      print(f"Current time: {current_time}")
      print(f"Course time start: {found_course.time_start}")
      print(f"Course time end: {found_course.time_end}")
      print(f"Course time start with date: {time_start_with_date}")
      print(f"Course time end with date: {time_end_with_date}")
      print(f"Time start with delta present: {time_start_with_delta_present}")
      print(f"Time start with delta late: {time_start_with_delta_late}")
      print("End Time")

      # Check if the user has already attended the course
      found_lecturer_log = LecturerAttendanceLogs.query.filter(
        LecturerAttendanceLogs.lecturer_nip==found_user.user_id,
        LecturerAttendanceLogs.course_id==found_course.course_id,
        LecturerAttendanceLogs.time_in.between(time_start_with_date, time_end_with_date)
      ).first()

      if found_lecturer_log:
        message = f"103 - Already attended"
        mqtt.publish(PUB_TOPIC, payload=message, qos=0)
        print(message)
        return False
      
      status = "ALPHA"

      # PRESENT if under 30 minutes after time_start
      if current_time > found_course.time_start and current_time < found_course.time_end and current_time < time_start_with_delta_present:
        status = "PRESENT"

      # LATE if under 60 minutes after time_start
      elif current_time > found_course.time_start and current_time < found_course.time_end and current_time < time_start_with_delta_late:
        status = "LATE"

      print(f"Status: {status}")

      new_lecturer_log = LecturerAttendanceLogs (
        lecturer_nip=found_user.user_id,
        course_id=found_course.course_id,
        room_id=found_course.room_id,
        time_in=current_daytime,
        status=status
      )

      db.session.add(new_lecturer_log)
      db.session.commit()

    else:
      message = f"104 - Invalid user role"
      mqtt.publish(PUB_TOPIC, payload=message, qos=0)
      print(message)
      return False
    
    message = f"100 - Success"
    mqtt.publish(PUB_TOPIC, payload=message, qos=0)
    print(message)
    
  # Buatkan fungsi untuk menghandle pesan MQTT apabila SUB_TOPIC2 ada pesan untuk menonaktifkan kelas, maka data student attendance logs dan lecturer attendance logs akan diupdate statusnya menjadi "Libur",
  
  def deactivate_class(uid: str) -> bool:
    current_time = get_current_time()
    current_day = get_current_day()
    current_daytime = get_current_daytime()
    
    found_user = User.query.filter_by(user_role="STUDENT").all()
    
    for user in found_user:
      found_course = Course.query.filter(
        Course.class_id==user.student_class,
        Course.day==current_day,
        Course.time_start<=current_time,
        Course.time_end>current_time
      ).first()
      
      if found_course:
        time_start_with_date = datetime.combine(current_daytime, found_course.time_start)
        time_end_with_date = datetime.combine(current_daytime, found_course.time_end)
        
        found_student_log = StudentAttendanceLogs.query.filter(
          StudentAttendanceLogs.student_nim==user.user_id,
          StudentAttendanceLogs.course_id==found_course.course_id,
          StudentAttendanceLogs.time_in.between(time_start_with_date, time_end_with_date)
        ).first()
        
        if found_student_log:
          found_student_log.status = "LIBUR"
          db.session.commit()
    
      return True
  
  # Handle MQTT message
  @mqtt.on_message()
  def handle_mqtt_message(client, userdata, msg):
    print("Instance ID:", id(app))
    uid = msg.payload.decode("utf-8")
    print("Received message: " + uid)
    print("Received message topic: " + msg.topic)
    # Do attendanec based on the user rfid
    with app.app_context():
      do_attendance(uid)

  # Handle MQTT disconnect
  @mqtt.on_disconnect()
  def handle_disconnect(client, userdata, rc):
    print("Disconnected from broker")

  # Handle MQTT error
  @mqtt.on_log()
  def handle_logging(client, userdata, level, buf):
    print("MQTT log: " + buf)
  # Registering route or endpoint blueprints
  app.register_blueprint(user_ep)
  app.register_blueprint(admin_ep)
  app.register_blueprint(lecturer_ep)
  app.register_blueprint(student_ep)
  
  return app
