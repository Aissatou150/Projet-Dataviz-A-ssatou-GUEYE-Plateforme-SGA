from models import Student
from database import SessionLocal

def get_student_by_id(student_id):
    db = SessionLocal()
    try:
        return db.query(Student).filter_by(id=student_id).first()
    finally:
        db.close()
