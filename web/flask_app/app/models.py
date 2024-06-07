from flask_argon2 import generate_password_hash, check_password_hash
from sqlalchemy import (
  Enum, ForeignKey, 
  Time, Column, Integer, String, Text, TIMESTAMP, CHAR
)
from sqlalchemy.orm import relationship
import enum

from ..extensions import db

class StudyProgram(enum.Enum):
  TMJ = 'TMJ'
  TMD = 'TMD'
  TI = 'TI'
  TKJ = 'TKJ'

class Major(enum.Enum):
  TIK = 'TIK'
  TE = 'TE'
  TGP = 'TGP'
  TM = 'TM'
  TS = 'TS'

class Class(db.Model):
  __tablename__ = 'class'
  class_id = Column(CHAR(10), primary_key=True, nullable=False)
  class_study_program = Column(Enum(StudyProgram), nullable=False)
  class_major = Column(Enum(Major), nullable=False)
  class_description = Column(Text, nullable=True)
  courses = relationship('Course', backref='class_course', lazy=True, cascade='all, delete-orphan')

class RoomBuilding(enum.Enum):
  GSG = 'GSG'
  AA = 'AA'

class Room(db.Model):
  __tablename__ = 'room'
  room_id = Column(String(10), primary_key=True, nullable=False)
  room_building = Column(Enum(RoomBuilding), nullable=False)
  room_description = Column(Text, nullable=True)
  courses = relationship('Course', backref='room_course', lazy=True)
  student_attendance_logs = relationship('StudentAttendanceLogs', backref='room_student', lazy=True, cascade='all, delete-orphan')
  lecturer_attendance_logs = relationship('LecturerAttendanceLogs', backref='room_lecturer', lazy=True, cascade='all, delete-orphan')

class RoleName(enum.Enum):
  ADMIN = 'ADMIN'
  LECTURER = 'LECTURER'
  STUDENT = 'STUDENT'

class User(db.Model):
  __tablename__ = 'user'
  user_id = Column(String(18), primary_key=True, nullable=False)
  user_role = Column(Enum(RoleName), nullable=False)
  user_fullname = Column(String(200), nullable=False)
  user_password_hash = Column(String(256), nullable=False)
  user_rfid_hash = Column(String(256), nullable=True, unique=True)
  user_email_address = Column(String(100), nullable=False, unique=True)
  user_home_address = Column(String(256), nullable=True)
  lecturer_major = Column(Enum(Major), nullable=True)
  student_class = Column(CHAR(10), ForeignKey('class.class_id'), nullable=True)
  courses = relationship('Course', backref='user_course', lazy=True, cascade='all, delete-orphan')
  student_attendance_logs = relationship('StudentAttendanceLogs', backref='user_student', lazy=True, cascade='all, delete-orphan')
  lecturer_attendance_logs = relationship('LecturerAttendanceLogs', backref='user_lecturer', lazy=True, cascade='all, delete-orphan')

  @property
  def password(self):
    raise AttributeError('password is not a readable attribute')
  
  @password.setter
  def password(self, password):
    self.user_password_hash = generate_password_hash(password)
  
  def verify_password(self, password):
    return check_password_hash(self.user_password_hash, password)
  
  @property
  def rfid(self):
    raise AttributeError('rfid is not a readable attribute')
  
  @rfid.setter
  def rfid(self, rfid):
    self.user_rfid_hash = generate_password_hash(rfid)
  
  def verify_rfid(self, rfid):
    return check_password_hash(self.user_rfid_hash, rfid)

class Course(db.Model):
  __tablename__ = 'course'
  course_id = Column(CHAR(15), primary_key=True, nullable=False)
  course_name = Column(String(100), nullable=False, unique=True)
  course_sks = Column(Integer(), nullable=False)
  at_semester = Column(Integer(), nullable=False)
  day = Column(String(9), nullable=False)
  time_start = Column(Time(timezone=True), nullable=False)
  time_end = Column(Time(timezone=True), nullable=False)
  course_description = Column(Text, nullable=True)
  lecturer_nip = Column(String(18), ForeignKey('user.user_id'), nullable=False)
  class_id = Column(CHAR(10), ForeignKey('class.class_id'), nullable=False)
  room_id = Column(CHAR(10), ForeignKey('room.room_id'), nullable=False)
  student_attendance_logs = relationship('StudentAttendanceLogs', backref='course_student', lazy=True, cascade='all, delete-orphan')
  lecturer_attendance_logs = relationship('LecturerAttendanceLogs', backref='course_lecturer', lazy=True, cascade='all, delete-orphan')

class AttendanceStatus(enum.Enum):
  PRESENT = 'PRESENT'
  LATE = 'LATE'
  ALPHA = 'ALPHA'

class StudentAttendanceLogs(db.Model):
  __tablename__ = 'student_attendance_logs'
  log_id = Column(Integer(), primary_key=True, nullable=False)
  time_in = Column(TIMESTAMP(timezone=True), nullable=False)
  status = Column(Enum(AttendanceStatus), nullable=False)
  student_nim = Column(String(18), ForeignKey('user.user_id'), nullable=False)
  course_id = Column(CHAR(15), ForeignKey('course.course_id'), nullable=False)
  room_id = Column(CHAR(10), ForeignKey('room.room_id'), nullable=False)

class LecturerAttendanceLogs(db.Model):
  __tablename__ = 'lecturer_attendance_logs'
  log_id = Column(Integer(), primary_key=True, nullable=False)
  time_in = Column(TIMESTAMP(timezone=True), nullable=False)
  status = Column(Enum(AttendanceStatus), nullable=False)
  lecturer_nip = Column(String(18), ForeignKey('user.user_id'), nullable=False)
  course_id = Column(CHAR(15), ForeignKey('course.course_id'), nullable=False)
  room_id = Column(CHAR(10), ForeignKey('room.room_id'), nullable=False)
