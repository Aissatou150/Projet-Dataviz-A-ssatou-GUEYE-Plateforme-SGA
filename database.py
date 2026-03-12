from sqlalchemy.orm import sessionmaker
from models import engine, Base, User, Student, Course, Grade, Session as CourseSession, Attendance, hash_password, verify_password
import os, pandas as pd, random
from datetime import datetime, date, timedelta

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_users():
    """Crée les utilisateurs par défaut si la table est vide."""
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return
        defaults = [
            User(username="admin",        password_h=hash_password("admin123"),   role="admin",       nom="Administration", prenom="ENSAE"),
            User(username="responsable1", password_h=hash_password("resp123"),    role="responsable", nom="Diallo",         prenom="Mamadou"),
            User(username="etudiant1",    password_h=hash_password("etud123"),    role="etudiant",    nom="Sow",            prenom="Fatou"),
        ]
        for u in defaults:
            db.add(u)
        db.commit()
        print("[Seed] Utilisateurs par défaut créés.")
    except Exception as e:
        db.rollback(); print(f"[Seed] Erreur: {e}")
    finally:
        db.close()

def migrate_from_excel(path="./data/db.xlsx"):
    if not os.path.exists(path):
        return
    db = SessionLocal()
    try:
        if db.query(Student).count() > 0:
            print("[Migration] Base déjà peuplée, migration ignorée.")
            return
        xf = pd.ExcelFile(path)
        if "Etudiants" in xf.sheet_names or "students" in xf.sheet_names:
            sname = "Etudiants" if "Etudiants" in xf.sheet_names else "students"
            df = pd.read_excel(path, sheet_name=sname)
            df.columns = df.columns.str.strip().str.lower()
            for _, r in df.iterrows():
                try:
                    s = Student(
                        nom=str(r.get("nom","")).strip(),
                        prenom=str(r.get("prenom","")).strip(),
                        email=str(r.get("email","")).strip() or None,
                        classe=str(r.get("classe","")).strip() or None,
                    )
                    db.add(s); db.flush()
                    # Créer un compte étudiant automatiquement
                    uname = f"etud_{s.id}"
                    u = User(username=uname, password_h=hash_password("etud123"),
                             role="etudiant", nom=s.nom, prenom=s.prenom, student_id=s.id)
                    db.add(u)
                except: pass
        # Cours par défaut
        default_courses = [
            Course(code="MATH101", libelle="Mathématiques",          volume_h=60, enseignant="Prof. Ndiaye",   classe="ISE1"),
            Course(code="STAT101", libelle="Statistiques",           volume_h=60, enseignant="Prof. Diallo",   classe="ISE1"),
            Course(code="INFO101", libelle="Informatique",           volume_h=45, enseignant="Prof. Fall",     classe="ITS1"),
            Course(code="ECON101", libelle="Économie",               volume_h=45, enseignant="Prof. Sow",      classe="ISE1"),
            Course(code="DEMO101", libelle="Démographie",            volume_h=30, enseignant="Prof. Ba",       classe="TSS1"),
        ]
        for c in default_courses:
            if not db.query(Course).filter_by(code=c.code).first():
                db.add(c)
        db.commit()
        print("[Migration] Données importées.")
    except Exception as e:
        db.rollback(); print(f"[Migration] Erreur: {e}")
    finally:
        db.close()


def seed_demo_data():
    """Génère des données fictives sénégalaises si la base est vide."""
    db = SessionLocal()
    try:
        if db.query(Student).count() > 0:
            print("[Seed] Données déjà présentes, skip.")
            return

        random.seed(42)

        # --- Cours ---
        cours_data = [
            Course(code="MATH101", libelle="Mathématiques",          volume_h=60, enseignant="Prof. Ndiaye",   classe="ISE1"),
            Course(code="STAT101", libelle="Statistiques",           volume_h=60, enseignant="Prof. Diallo",   classe="ISE1"),
            Course(code="INFO101", libelle="Informatique",           volume_h=45, enseignant="Prof. Fall",     classe="ITS1"),
            Course(code="ECON101", libelle="Économie",               volume_h=45, enseignant="Prof. Sow",      classe="ISE1"),
            Course(code="DEMO101", libelle="Démographie",            volume_h=30, enseignant="Prof. Ba",       classe="TSS1"),
            Course(code="PROB101", libelle="Probabilités",           volume_h=45, enseignant="Prof. Mbaye",    classe="ISE1"),
            Course(code="ANGL101", libelle="Anglais technique",      volume_h=30, enseignant="Prof. Diouf",    classe="ISE2"),
            Course(code="PROG101", libelle="Programmation Python",   volume_h=45, enseignant="Prof. Sarr",     classe="ITS1"),
        ]
        for c in cours_data:
            if not db.query(Course).filter_by(code=c.code).first():
                db.add(c)
        db.flush()

        # --- Étudiants sénégalais ---
        prenoms_m = ["Mamadou","Abdoulaye","Ousmane","Ibrahima","Moussa","Cheikh","Modou",
                     "El Hadji","Samba","Lamine","Bamba","Aliou","Babacar","Alassane","Pape"]
        prenoms_f = ["Fatou","Aminata","Mariama","Aïssatou","Rokhaya","Khady","Ndéye",
                     "Aïda","Fatoumata","Adja","Coumba","Yacine","Dieynaba","Sokhna","Mame"]
        noms = ["Diallo","Ndiaye","Fall","Gueye","Diop","Mbaye","Sy","Sow","Ba","Diouf",
                "Thiaw","Ndour","Sarr","Wade","Cissé","Touré","Koné","Barry","Camara","Traoré"]
        classes = ["ISE1","ISE1","ISE1","ISE2","ISE2","ITS1","ITS1","TSS1"]

        students = []
        used_emails = set()
        i = 0
        while len(students) < 40:
            is_female = (i % 3 == 0)
            prenom = random.choice(prenoms_f if is_female else prenoms_m)
            nom    = random.choice(noms)
            classe = random.choice(classes)
            email_base = f"{prenom.lower().replace(' ','').replace('ï','i').replace('é','e').replace('è','e')}.{nom.lower()}@ensae.sn"
            if email_base in used_emails:
                email_base = f"{prenom.lower().replace(' ','').replace('ï','i').replace('é','e').replace('è','e')}.{nom.lower()}{i}@ensae.sn"
            used_emails.add(email_base)
            dob = date(random.randint(1999, 2004), random.randint(1,12), random.randint(1,28))
            s = Student(nom=nom, prenom=prenom, email=email_base, classe=classe, dob=dob)
            db.add(s); db.flush()
            students.append(s)
            # Compte étudiant
            uname = f"etud_{s.id}"
            if not db.query(User).filter_by(username=uname).first():
                db.add(User(username=uname, password_h=hash_password("etud123"),
                            role="etudiant", nom=s.nom, prenom=s.prenom, student_id=s.id))
            i += 1

        # Lier etudiant1 au premier étudiant si possible
        etud1 = db.query(User).filter_by(username="etudiant1").first()
        if etud1 and students:
            etud1.student_id = students[0].id
            etud1.nom = students[0].nom
            etud1.prenom = students[0].prenom
        db.flush()

        # --- Séances ---
        seances = []
        start_date = date(2025, 10, 1)
        for c in cours_data:
            nb_seances = random.randint(4, 8)
            d = start_date
            for _ in range(nb_seances):
                d += timedelta(days=random.randint(3, 10))
                duree = random.choice([1.5, 2.0, 2.5, 3.0])
                theme = random.choice([
                    "Introduction au cours","Chapitre 1 : Fondamentaux",
                    "Chapitre 2 : Approfondissement","Exercices dirigés",
                    "TD noté","Révisions","Chapitre 3","Exposés étudiants",
                ])
                s = CourseSession(course_code=c.code, date=d, duree=duree, theme=theme)
                db.add(s); db.flush()
                seances.append(s)
                # Absences aléatoires (10-20% des étudiants par séance)
                absents = random.sample(students, k=random.randint(1, max(1, len(students)//6)))
                for st in absents:
                    type_abs = random.choice(["absence","absence","retard"])
                    db.add(Attendance(id_session=s.id, id_student=st.id, type_abs=type_abs))

        # --- Notes ---
        type_evals = ["devoir","devoir","examen","partiel"]
        coefficients = {"devoir": 1.0, "examen": 2.0, "partiel": 1.5}
        for s in students:
            for c in cours_data:
                # 1 à 2 évaluations par cours
                nb_evals = random.randint(1, 2)
                for _ in range(nb_evals):
                    te = random.choice(type_evals)
                    # Notes réalistes entre 6 et 19, centrées autour de 12
                    note = round(min(20, max(0, random.gauss(12.5, 3.5))), 2)
                    coeff = coefficients.get(te, 1.0)
                    db.add(Grade(id_student=s.id, course_code=c.code,
                                 note=note, coefficient=coeff, type_eval=te))

        db.commit()
        print(f"[Seed] {len(students)} étudiants, {len(seances)} séances, notes et absences générés.")
    except Exception as e:
        db.rollback(); print(f"[Seed] Erreur: {e}")
    finally:
        db.close()


def get_user(username: str, password: str):
    db = SessionLocal()
    try:
        u = db.query(User).filter_by(username=username).first()
        if u and verify_password(password, u.password_h):
            return {"id": u.id, "username": u.username, "role": u.role,
                    "nom": u.nom or "", "prenom": u.prenom or "", "student_id": u.student_id}
        return None
    finally:
        db.close()
