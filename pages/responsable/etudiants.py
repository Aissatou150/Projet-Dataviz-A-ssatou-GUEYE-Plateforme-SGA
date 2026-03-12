import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash
from database import SessionLocal
from models import Student
dash.register_page(__name__, path='/responsable/etudiants', title='etudiants — Responsable SGA')




def get_students():
    db = SessionLocal()
    try:
        return db.query(Student).order_by(Student.nom).all()
    finally:
        db.close()


def _build_table(students):
    if not students:
        return dbc.Alert("Aucun étudiant enregistré.", color="info")
    header = html.Thead(html.Tr([
        html.Th("ID"), html.Th("Nom"), html.Th("Prénom"),
        html.Th("Email"), html.Th("Date de naissance"), html.Th("Actions"),
    ]))
    rows = [html.Tr([
        html.Td(s.id, style={"color":"var(--grey-400)","fontSize":"12px"}),
        html.Td(html.Span(s.nom, style={"fontWeight":"600","color":"var(--blue)"})),
        html.Td(s.prenom),
        html.Td(s.email, style={"color":"var(--grey-400)","fontSize":"12px"}),
        html.Td(str(s.dob) if s.dob else "—", style={"color":"var(--grey-400)"}),
        html.Td(html.Div([
            dbc.Button("Modifier",  id={"type":"btn-edit-etud-resp",  "index":s.id}, color="warning", size="sm", className="me-1"),
            dbc.Button("Supprimer", id={"type":"btn-del-etud-resp",   "index":s.id}, color="danger",  size="sm"),
        ], style={"display":"flex","gap":"4px"})),
    ]) for s in students]
    return dbc.Table([header, html.Tbody(rows)], striped=False, hover=True, responsive=True, bordered=False)


def layout():
    return html.Div([
        html.Div([
            html.Div([
                html.H2("Gestion des étudiants"),
                html.Div("Inscriptions, fiches et suivi individuel", className="page-sub"),
            ]),
            dbc.Button("Nouvel étudiant", id="btn-open-modal-etud-resp", color="primary"),
        ], className="page-header", style={"display":"flex","justifyContent":"space-between","alignItems":"center"}),

        html.Div([
            html.Div([
                html.Div("Liste des étudiants", className="card-header"),
                html.Div(html.Div(id="etud-list-resp", children=_build_table(get_students())), className="card-body p-0"),
            ], className="card"),
        ], className="page-body"),

        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(html.Span(id="modal-etud-title-resp", children="Nouvel étudiant"))),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([dbc.Label("Nom *"),    dbc.Input(id="inp-etud-nom-resp")],    width=6),
                    dbc.Col([dbc.Label("Prénom *"), dbc.Input(id="inp-etud-prenom-resp")], width=6),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([dbc.Label("Email *"),           dbc.Input(id="inp-etud-email-resp", type="email")], width=6),
                    dbc.Col([dbc.Label("Date de naissance"), dbc.Input(id="inp-etud-dob-resp",   type="date")],  width=6),
                ], className="mb-3"),
                html.Div(id="etud-form-feedback-resp"),
                dcc.Store(id="store-edit-etud-id-resp"),
            ]),
            dbc.ModalFooter([
                dbc.Button("Annuler",     id="btn-cancel-etud-resp", color="secondary", outline=True),
                dbc.Button("Enregistrer", id="btn-save-etud-resp",   color="primary"),
            ]),
        ], id="modal-etud-resp", is_open=False),

        dbc.Modal([
            dbc.ModalHeader("Confirmer la suppression"),
            dbc.ModalBody(html.P(id="del-etud-msg-resp")),
            dbc.ModalFooter([
                dbc.Button("Annuler",    id="btn-cancel-del-etud-resp",  color="secondary", outline=True),
                dbc.Button("Supprimer",  id="btn-confirm-del-etud-resp", color="danger"),
            ]),
            dcc.Store(id="store-del-etud-id-resp"),
        ], id="modal-del-etud-resp", is_open=False),
    ])


@callback(
    Output("modal-etud-resp","is_open",allow_duplicate=True),
    Output("inp-etud-nom-resp","value",allow_duplicate=True),
    Output("inp-etud-prenom-resp","value",allow_duplicate=True),
    Output("inp-etud-email-resp","value",allow_duplicate=True),
    Output("inp-etud-dob-resp","value",allow_duplicate=True),
    Output("store-edit-etud-id-resp","data",allow_duplicate=True),
    Output("modal-etud-title-resp","children",allow_duplicate=True),
    Input("btn-open-modal-etud-resp","n_clicks"), prevent_initial_call=True,
)
def open_new(_): return True,"","","","",None,"Nouvel étudiant"


@callback(
    Output("modal-etud-resp","is_open",allow_duplicate=True),
    Output("inp-etud-nom-resp","value",allow_duplicate=True),
    Output("inp-etud-prenom-resp","value",allow_duplicate=True),
    Output("inp-etud-email-resp","value",allow_duplicate=True),
    Output("inp-etud-dob-resp","value",allow_duplicate=True),
    Output("store-edit-etud-id-resp","data",allow_duplicate=True),
    Output("modal-etud-title-resp","children",allow_duplicate=True),
    Input({"type":"btn-edit-etud-resp","index":dash.ALL},"n_clicks"), prevent_initial_call=True,
)
def open_edit(n):
    if not any(n): return [dash.no_update]*7
    sid = ctx.triggered_id["index"]
    db = SessionLocal()
    try:
        s = db.query(Student).filter_by(id=sid).first()
        if not s: return [dash.no_update]*7
        return True, s.nom, s.prenom, s.email, str(s.dob) if s.dob else "", sid, f"Modifier · {s.prenom} {s.nom}"
    finally:
        db.close()


@callback(Output("modal-etud-resp","is_open",allow_duplicate=True), Input("btn-cancel-etud-resp","n_clicks"), prevent_initial_call=True)
def cancel(_): return False


@callback(
    Output("etud-list-resp","children"),
    Output("etud-form-feedback-resp","children"),
    Output("modal-etud-resp","is_open",allow_duplicate=True),
    Input("btn-save-etud-resp","n_clicks"),
    State("inp-etud-nom-resp","value"), State("inp-etud-prenom-resp","value"),
    State("inp-etud-email-resp","value"), State("inp-etud-dob-resp","value"),
    State("store-edit-etud-id-resp","data"),
    prevent_initial_call=True,
)
def save(_, nom, prenom, email, dob, edit_id):
    if not nom or not prenom or not email:
        return dash.no_update, dbc.Alert("Champs obligatoires manquants (*)", color="warning"), True
    db = SessionLocal()
    try:
        from datetime import datetime
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date() if dob else None
        if edit_id:
            s = db.query(Student).filter_by(id=int(edit_id)).first()
            if s: s.nom=nom.strip(); s.prenom=prenom.strip(); s.email=email.strip(); s.dob=dob_date
        else:
            if db.query(Student).filter_by(email=email.strip()).first():
                return dash.no_update, dbc.Alert("Cet email est déjà utilisé.", color="danger"), True
            db.add(Student(nom=nom.strip(), prenom=prenom.strip(), email=email.strip(), dob=dob_date))
        db.commit()
    except Exception as e:
        db.rollback(); return dash.no_update, dbc.Alert(f"Erreur : {e}", color="danger"), True
    finally:
        db.close()
    return _build_table(get_students()), "", False


@callback(
    Output("modal-del-etud-resp","is_open",allow_duplicate=True),
    Output("del-etud-msg-resp","children"), Output("store-del-etud-id-resp","data"),
    Input({"type":"btn-del-etud-resp","index":dash.ALL},"n_clicks"), prevent_initial_call=True,
)
def open_del(n):
    if not any(n): return dash.no_update,"",dash.no_update
    sid = ctx.triggered_id["index"]
    db = SessionLocal()
    try:
        s = db.query(Student).filter_by(id=sid).first()
        name = f"{s.prenom} {s.nom}" if s else str(sid)
    finally:
        db.close()
    return True, f"Supprimer l'étudiant '{name}' et toutes ses données ?", sid


@callback(Output("modal-del-etud-resp","is_open",allow_duplicate=True), Input("btn-cancel-del-etud-resp","n_clicks"), prevent_initial_call=True)
def cancel_del(_): return False


@callback(
    Output("etud-list-resp","children",allow_duplicate=True),
    Output("modal-del-etud-resp","is_open",allow_duplicate=True),
    Input("btn-confirm-del-etud-resp","n_clicks"),
    State("store-del-etud-id-resp","data"), prevent_initial_call=True,
)
def confirm_del(_, sid):
    if not sid: return dash.no_update, False
    db = SessionLocal()
    try:
        s = db.query(Student).filter_by(id=int(sid)).first()
        if s: db.delete(s); db.commit()
    except: db.rollback()
    finally: db.close()
    return _build_table(get_students()), False
