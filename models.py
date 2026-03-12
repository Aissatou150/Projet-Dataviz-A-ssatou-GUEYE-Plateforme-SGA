from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship
import hashlib

Base = declarative_base()
DATABASE_URL = "sqlite:///./data/sga.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    username   = Column(String, unique=True, nullable=False)
    password_h = Column(String, nullable=False)
    role       = Column(String, nullable=False)  # admin | responsable | etudiant
    nom        = Column(String)
    prenom     = Column(String)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    student    = relationship("Student", foreign_keys=[student_id])
    def check_password(self, pwd):
        return self.password_h == hash_password(pwd)

class Student(Base):
    __tablename__ = "students"
    id      = Column(Integer, primary_key=True, autoincrement=True)
    nom     = Column(String, nullable=False)
    prenom  = Column(String, nullable=False)
    email   = Column(String, unique=True)
    dob     = Column(Date)
    classe  = Column(String)
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete")
    grades      = relationship("Grade",      back_populates="student", cascade="all, delete")

class Course(Base):
    __tablename__ = "courses"
    code       = Column(String, primary_key=True)
    libelle    = Column(String, nullable=False)
    volume_h   = Column(Integer, nullable=False)
    enseignant = Column(String)
    classe     = Column(String)
    sessions   = relationship("Session",   back_populates="course", cascade="all, delete")
    grades     = relationship("Grade",     back_populates="course", cascade="all, delete")
    pdfs       = relationship("CoursePDF", back_populates="course", cascade="all, delete")

class Session(Base):
    __tablename__ = "sessions"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String, ForeignKey("courses.code"), nullable=False)
    date        = Column(Date,   nullable=False)
    duree       = Column(Float,  nullable=False)
    theme       = Column(String)
    type_seance = Column(String, default="cours")
    course      = relationship("Course",     back_populates="sessions")
    attendances = relationship("Attendance", back_populates="session", cascade="all, delete")

class Attendance(Base):
    __tablename__ = "attendance"
    id_session = Column(Integer, ForeignKey("sessions.id"), primary_key=True)
    id_student = Column(Integer, ForeignKey("students.id"), primary_key=True)
    type_abs   = Column(String, default="absence")
    session    = relationship("Session", back_populates="attendances")
    student    = relationship("Student", back_populates="attendances")

class Grade(Base):
    __tablename__ = "grades"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    id_student  = Column(Integer, ForeignKey("students.id"),  nullable=False)
    course_code = Column(String,  ForeignKey("courses.code"), nullable=False)
    note        = Column(Float,   nullable=False)
    coefficient = Column(Float,   default=1.0)
    type_eval   = Column(String,  default="devoir")
    student     = relationship("Student", back_populates="grades")
    course      = relationship("Course",  back_populates="grades")

class CoursePDF(Base):
    __tablename__ = "course_pdfs"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String, ForeignKey("courses.code"), nullable=False)
    titre       = Column(String, nullable=False)
    filename    = Column(String, nullable=False)
    course      = relationship("Course", back_populates="pdfs")

def init_db():
    Base.metadata.create_all(engine)


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed
