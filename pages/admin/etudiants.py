import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from database import SessionLocal
from models import Student, Grade, Attendance, Session as CS

dash.register_page(__name__, path='/admin/etudiants', title='Étudiants — Admin SGA')


def _get_students():
    db = SessionLocal()
    try:
        rows = []
        for s in db.query(Student).order_by(Student.nom).all():
            nb_notes = db.query(Grade).filter_by(id_student=s.id).count()
            nb_abs   = db.query(Attendance).filter_by(id_student=s.id, type_abs="absence").count()
            rows.append({
                "id":      s.id,
                "nom":     s.nom,
                "prenom":  s.prenom,
                "email":   s.email or "—",
                "classe":  s.classe or "—",
                "dob":     str(s.dob) if s.dob else "—",
                "nb_notes": nb_notes,
                "nb_abs":   nb_abs,
            })
        return rows
    finally:
        db.close()


def _build_table(students):
    if not students:
        return dbc.Alert("Aucun étudiant enregistré.", color="info")
    header = html.Thead(html.Tr([
        html.Th("Nom"), html.Th("Prénom"), html.Th("Classe"),
        html.Th("Email"), html.Th("Naissance"),
        html.Th("Notes"), html.Th("Abs."), html.Th("Actions"),
    ]))
    def classe_badge(c):
        return html.Span(c, style={
            "background": "rgba(16,110,190,0.09)", "color": "#1E6EBE",
            "borderRadius": "20px", "padding": "2px 10px",
            "fontSize": "11px", "fontWeight": "600",
        })
    rows = [html.Tr([
        html.Td(html.Span(s["nom"], style={"fontWeight": "600", "color": "#1E6EBE"})),
        html.Td(s["prenom"]),
        html.Td(classe_badge(s["classe"])),
        html.Td(s["email"], style={"fontSize": "12px", "color": "#6B7280"}),
        html.Td(s["dob"],   style={"fontSize": "12px", "color": "#6B7280"}),
        html.Td(html.Span(str(s["nb_notes"]),
                style={"fontWeight": "600", "color": "#7C3AED"})),
        html.Td(html.Span(str(s["nb_abs"]),
                style={"fontWeight": "600", "color": "#EF4444" if s["nb_abs"] > 0 else "#10B981"})),
        html.Td(html.Div([
            dbc.Button("Fiche",     id={"type": "btn-fiche-etud-admin",  "index": s["id"]},
                       color="primary",  size="sm", className="me-1", outline=True),
            dbc.Button("Modifier",  id={"type": "btn-edit-etud-admin",   "index": s["id"]},
                       color="warning",  size="sm", className="me-1"),
            dbc.Button("Supprimer", id={"type": "btn-del-etud-admin",    "index": s["id"]},
                       color="danger",   size="sm"),
        ], style={"display": "flex", "gap": "4px", "flexWrap": "nowrap"})),
    ]) for s in students]
    return dbc.Table([header, html.Tbody(rows)],
                     striped=False, hover=True, responsive=True, bordered=False)


def layout():
    students = _get_students()
    return html.Div([
        html.Div([
            html.Div([
                html.H2("Gestion des étudiants"),
                html.Div("Inscriptions, fiches et suivi individuel", className="page-sub"),
            ]),
            dbc.Button("+ Nouvel étudiant", id="btn-open-modal-etud-admin", color="primary"),
        ], className="page-header",
           style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}),

        html.Div([
            html.Div([
                html.Div("Liste des étudiants", className="card-header"),
                html.Div(
                    html.Div(id="etud-list-admin", children=_build_table(students)),
                    className="card-body p-0",
                ),
            ], className="card"),
        ], className="page-body"),

        # Modal ajout / modification
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(html.Span(id="modal-etud-title-admin",
                                                      children="Nouvel étudiant"))),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([dbc.Label("Nom *"),    dbc.Input(id="inp-etud-nom-admin",    placeholder="Diallo")], width=6),
                    dbc.Col([dbc.Label("Prénom *"), dbc.Input(id="inp-etud-prenom-admin", placeholder="Mamadou")], width=6),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([dbc.Label("Email *"), dbc.Input(id="inp-etud-email-admin", type="email",
                                                              placeholder="mamadou.diallo@ensae.sn")], width=6),
                    dbc.Col([dbc.Label("Classe"),  dbc.Input(id="inp-etud-classe-admin", placeholder="ISE1")], width=6),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([dbc.Label("Date de naissance"), dbc.Input(id="inp-etud-dob-admin", type="date")], width=6),
                ], className="mb-3"),
                html.Div(id="etud-form-feedback-admin"),
                dcc.Store(id="store-edit-etud-id-admin"),
            ]),
            dbc.ModalFooter([
                dbc.Button("Annuler",     id="btn-cancel-etud-admin",  color="secondary", outline=True),
                dbc.Button("Enregistrer", id="btn-save-etud-admin",    color="primary"),
            ]),
        ], id="modal-etud-admin", is_open=False, size="lg"),

        # Modal suppression
        dbc.Modal([
            dbc.ModalHeader("Confirmer la suppression"),
            dbc.ModalBody(html.P(id="del-etud-msg-admin")),
            dbc.ModalFooter([
                dbc.Button("Annuler",     id="btn-cancel-del-etud-admin",  color="secondary", outline=True),
                dbc.Button("Supprimer",   id="btn-confirm-del-etud-admin", color="danger"),
            ]),
            dcc.Store(id="store-del-etud-id-admin"),
        ], id="modal-del-etud-admin", is_open=False),

        # Modal fiche étudiant
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(html.Span(id="fiche-etud-title-admin"))),
            dbc.ModalBody(html.Div(id="fiche-etud-body-admin")),
            dbc.ModalFooter(dbc.Button("Fermer", id="btn-close-fiche-admin", color="secondary")),
        ], id="modal-fiche-etud-admin", is_open=False, size="lg"),
    ])


# --- Ouvrir modal nouveau ---
@callback(
    Output("modal-etud-admin", "is_open",               allow_duplicate=True),
    Output("inp-etud-nom-admin",    "value",             allow_duplicate=True),
    Output("inp-etud-prenom-admin", "value",             allow_duplicate=True),
    Output("inp-etud-email-admin",  "value",             allow_duplicate=True),
    Output("inp-etud-classe-admin", "value",             allow_duplicate=True),
    Output("inp-etud-dob-admin",    "value",             allow_duplicate=True),
    Output("store-edit-etud-id-admin", "data",           allow_duplicate=True),
    Output("modal-etud-title-admin", "children",         allow_duplicate=True),
    Input("btn-open-modal-etud-admin", "n_clicks"),
    prevent_initial_call=True,
)
def open_new(_):
    return True, "", "", "", "", "", None, "Nouvel étudiant"


# --- Ouvrir modal modification ---
@callback(
    Output("modal-etud-admin", "is_open",               allow_duplicate=True),
    Output("inp-etud-nom-admin",    "value",             allow_duplicate=True),
    Output("inp-etud-prenom-admin", "value",             allow_duplicate=True),
    Output("inp-etud-email-admin",  "value",             allow_duplicate=True),
    Output("inp-etud-classe-admin", "value",             allow_duplicate=True),
    Output("inp-etud-dob-admin",    "value",             allow_duplicate=True),
    Output("store-edit-etud-id-admin", "data",           allow_duplicate=True),
    Output("modal-etud-title-admin", "children",         allow_duplicate=True),
    Input({"type": "btn-edit-etud-admin", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_edit(n):
    if not any(n):
        return [dash.no_update] * 8
    sid = ctx.triggered_id["index"]
    db = SessionLocal()
    try:
        s = db.query(Student).filter_by(id=sid).first()
        if not s:
            return [dash.no_update] * 8
        return (True, s.nom, s.prenom, s.email or "", s.classe or "",
                str(s.dob) if s.dob else "", sid, f"Modifier · {s.prenom} {s.nom}")
    finally:
        db.close()


# --- Annuler ---
@callback(
    Output("modal-etud-admin", "is_open", allow_duplicate=True),
    Input("btn-cancel-etud-admin", "n_clicks"),
    prevent_initial_call=True,
)
def cancel(_):
    return False


# --- Enregistrer (ajout ou modif) ---
@callback(
    Output("etud-list-admin",          "children",  allow_duplicate=True),
    Output("etud-form-feedback-admin", "children"),
    Output("modal-etud-admin",         "is_open",   allow_duplicate=True),
    Input("btn-save-etud-admin", "n_clicks"),
    State("inp-etud-nom-admin",    "value"),
    State("inp-etud-prenom-admin", "value"),
    State("inp-etud-email-admin",  "value"),
    State("inp-etud-classe-admin", "value"),
    State("inp-etud-dob-admin",    "value"),
    State("store-edit-etud-id-admin", "data"),
    prevent_initial_call=True,
)
def save(_, nom, prenom, email, classe, dob, edit_id):
    if not nom or not prenom or not email:
        return dash.no_update, dbc.Alert("Champs obligatoires manquants (*).", color="warning"), True
    db = SessionLocal()
    try:
        from datetime import datetime
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date() if dob else None
        if edit_id:
            s = db.query(Student).filter_by(id=int(edit_id)).first()
            if s:
                s.nom    = nom.strip()
                s.prenom = prenom.strip()
                s.email  = email.strip()
                s.classe = classe.strip() if classe else None
                s.dob    = dob_date
        else:
            if db.query(Student).filter_by(email=email.strip()).first():
                return dash.no_update, dbc.Alert("Cet email est déjà utilisé.", color="danger"), True
            db.add(Student(nom=nom.strip(), prenom=prenom.strip(),
                           email=email.strip(), classe=classe.strip() if classe else None,
                           dob=dob_date))
        db.commit()
    except Exception as e:
        db.rollback()
        return dash.no_update, dbc.Alert(f"Erreur : {e}", color="danger"), True
    finally:
        db.close()
    return _build_table(_get_students()), "", False


# --- Ouvrir modal suppression ---
@callback(
    Output("modal-del-etud-admin",   "is_open",  allow_duplicate=True),
    Output("del-etud-msg-admin",     "children"),
    Output("store-del-etud-id-admin","data"),
    Input({"type": "btn-del-etud-admin", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_del(n):
    if not any(n):
        return dash.no_update, "", dash.no_update
    sid = ctx.triggered_id["index"]
    db = SessionLocal()
    try:
        s = db.query(Student).filter_by(id=sid).first()
        name = f"{s.prenom} {s.nom}" if s else str(sid)
    finally:
        db.close()
    return True, f"Supprimer définitivement '{name}' et toutes ses données (notes, absences) ?", sid


@callback(
    Output("modal-del-etud-admin", "is_open", allow_duplicate=True),
    Input("btn-cancel-del-etud-admin", "n_clicks"),
    prevent_initial_call=True,
)
def cancel_del(_):
    return False


@callback(
    Output("etud-list-admin",       "children", allow_duplicate=True),
    Output("modal-del-etud-admin",  "is_open",  allow_duplicate=True),
    Input("btn-confirm-del-etud-admin", "n_clicks"),
    State("store-del-etud-id-admin", "data"),
    prevent_initial_call=True,
)
def confirm_del(_, sid):
    if not sid:
        return dash.no_update, False
    db = SessionLocal()
    try:
        s = db.query(Student).filter_by(id=int(sid)).first()
        if s:
            db.delete(s)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
    return _build_table(_get_students()), False


# --- Ouvrir fiche étudiant ---
@callback(
    Output("modal-fiche-etud-admin", "is_open",      allow_duplicate=True),
    Output("fiche-etud-title-admin", "children"),
    Output("fiche-etud-body-admin",  "children"),
    Input({"type": "btn-fiche-etud-admin", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_fiche(n):
    if not any(n):
        return dash.no_update, dash.no_update, dash.no_update
    sid = ctx.triggered_id["index"]
    db = SessionLocal()
    try:
        s = db.query(Student).filter_by(id=sid).first()
        if not s:
            return True, "Étudiant", dbc.Alert("Introuvable.", color="warning")

        from models import Grade, Attendance
        grades = db.query(Grade).filter_by(id_student=sid).all()
        atts   = db.query(Attendance).filter_by(id_student=sid).all()

        grades_data = [{"cours": g.course.libelle if g.course else g.course_code,
                         "note": g.note, "coeff": g.coefficient,
                         "type": g.type_eval or "devoir"} for g in grades]
        nb_abs = sum(1 for a in atts if a.type_abs == "absence")
        nb_ret = sum(1 for a in atts if a.type_abs == "retard")

        moy = 0
        if grades_data:
            pts   = sum(g["note"] * g["coeff"] for g in grades_data)
            coeff = sum(g["coeff"] for g in grades_data)
            moy   = round(pts / coeff, 2) if coeff else 0

        title = f"{s.prenom} {s.nom} · {s.classe or '—'}"
    finally:
        db.close()

    moy_color = "#10B981" if moy >= 10 else "#EF4444"

    body = html.Div([
        dbc.Row([
            dbc.Col(html.Div([
                html.Div(str(moy) + "/20", style={"fontSize": "28px", "fontWeight": "800",
                                                   "color": moy_color}),
                html.Div("Moyenne générale", style={"fontSize": "12px", "color": "#6B7280"}),
            ], style={"textAlign": "center", "padding": "16px",
                       "background": "#F9FAFB", "borderRadius": "8px"}), md=3),
            dbc.Col(html.Div([
                html.Div(str(nb_abs), style={"fontSize": "28px", "fontWeight": "800", "color": "#EF4444"}),
                html.Div("Absences", style={"fontSize": "12px", "color": "#6B7280"}),
            ], style={"textAlign": "center", "padding": "16px",
                       "background": "#FEF2F2", "borderRadius": "8px"}), md=3),
            dbc.Col(html.Div([
                html.Div(str(nb_ret), style={"fontSize": "28px", "fontWeight": "800", "color": "#F59E0B"}),
                html.Div("Retards", style={"fontSize": "12px", "color": "#6B7280"}),
            ], style={"textAlign": "center", "padding": "16px",
                       "background": "#FFFBEB", "borderRadius": "8px"}), md=3),
            dbc.Col(html.Div([
                html.Div(str(len(grades_data)), style={"fontSize": "28px", "fontWeight": "800", "color": "#7C3AED"}),
                html.Div("Évaluations", style={"fontSize": "12px", "color": "#6B7280"}),
            ], style={"textAlign": "center", "padding": "16px",
                       "background": "#F5F3FF", "borderRadius": "8px"}), md=3),
        ], className="mb-4"),
        html.H6("Notes par matière", style={"fontWeight": "700", "marginBottom": "10px"}),
        html.Table([
            html.Thead(html.Tr([html.Th("Matière"), html.Th("Type"), html.Th("Note"), html.Th("Coeff")])),
            html.Tbody([
                html.Tr([
                    html.Td(g["cours"], style={"fontWeight": "600"}),
                    html.Td(g["type"].capitalize()),
                    html.Td(html.Span(f"{g['note']}/20", style={
                        "fontWeight": "700",
                        "color": "#10B981" if g["note"] >= 10 else "#EF4444",
                    })),
                    html.Td(g["coeff"]),
                ]) for g in grades_data
            ]) if grades_data else html.Tr([html.Td("Aucune note.", colSpan=4,
                style={"textAlign": "center", "color": "#6B7280", "padding": "16px"})]),
        ], className="table"),
    ])

    return True, title, body


@callback(
    Output("modal-fiche-etud-admin", "is_open", allow_duplicate=True),
    Input("btn-close-fiche-admin", "n_clicks"),
    prevent_initial_call=True,
)
def close_fiche(_):
    return False
