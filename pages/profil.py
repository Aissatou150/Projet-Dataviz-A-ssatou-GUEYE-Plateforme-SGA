import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from get_student_by_id import get_student_by_id

dash.register_page(__name__, path="/profil/<id>", title="Fiche étudiant — SGA")

def layout(id=None, **kwargs):
    try:
        student_id = int(id) if id is not None else None
    except Exception:
        student_id = None
    student = get_student_by_id(student_id)
    if not student:
        return html.Div([
            html.H2("Étudiant introuvable"),
            html.P(f"Aucun étudiant avec l'ID {id} n'a été trouvé."),
            dcc.Link("Retour", href="/responsable/etudiants")
        ])
    return html.Div([
        html.H2(f"Fiche de {student.nom} {student.prenom}"),
        html.Ul([
            html.Li(f"ID: {student.id}"),
            html.Li(f"Nom: {student.nom}"),
            html.Li(f"Prénom: {student.prenom}"),
            html.Li(f"Email: {student.email}"),
            html.Li(f"Date de naissance: {student.dob}"),
        ]),
        dcc.Link("Retour", href="/responsable/etudiants")
    ])
