import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash
from database import SessionLocal
from models import Course, Session as CourseSession
from sqlalchemy import func
dash.register_page(__name__, path='/admin/cours', title='Cours — Admin SGA')




def get_courses():
    db = SessionLocal()
    try:
        return db.query(Course).all()
    finally:
        db.close()


def get_progression(code):
    db = SessionLocal()
    try:
        c = db.query(Course).filter_by(code=code).first()
        if not c:
            return 0, 0
        done = db.query(func.sum(CourseSession.duree)).filter_by(course_code=code).scalar() or 0
        return float(done), c.volume_h
    finally:
        db.close()


def _build_list():
    courses = get_courses()
    if not courses:
        return dbc.Alert("Aucun cours enregistré.", color="info")

    rows = []
    for c in courses:
        done, total = get_progression(c.code)
        pct   = int(done / total * 100) if total > 0 else 0
        color = "success" if pct >= 80 else ("warning" if pct >= 40 else "danger")

        rows.append(
            html.Tr([
                html.Td(html.Span(c.code,    style={"fontWeight":"600","color":"var(--blue)","fontFamily":"'Outfit',sans-serif","fontSize":"13px"})),
                html.Td(c.libelle),
                html.Td(c.enseignant or "—", style={"color":"var(--grey-400)"}),
                html.Td(f"{total}h",         style={"textAlign":"center"}),
                html.Td([
                    html.Div(f"{done:.0f}h / {total}h · {pct}%", style={"fontSize":"11px","color":"var(--grey-400)","marginBottom":"4px"}),
                    dbc.Progress(value=pct, color=color, style={"height":"6px"}),
                ], style={"minWidth":"160px"}),
                html.Td(html.Div([
                    dbc.Button("Modifier",   id={"type":"btn-edit-cours-admin","index":c.code}, color="warning", size="sm", className="me-1"),
                    dbc.Button("Supprimer",  id={"type":"btn-del-cours-admin", "index":c.code}, color="danger",  size="sm"),
                ], style={"display":"flex","gap":"4px"})),
            ])
        )

    header = html.Thead(html.Tr([
        html.Th("Code"), html.Th("Intitulé"), html.Th("Enseignant"),
        html.Th("Volume", style={"textAlign":"center"}),
        html.Th("Progression"), html.Th("Actions"),
    ]))
    return dbc.Table([header, html.Tbody(rows)],
                     striped=False, hover=True, responsive=True, bordered=False)


def layout():
    return html.Div([
        html.Div([
            html.Div([
                html.H2("Gestion des cours"),
                html.Div("Curriculum, suivi horaire et progression", className="page-sub"),
            ]),
            dbc.Button("Nouveau cours", id="btn-open-modal-cours-admin", color="primary"),
        ], className="page-header", style={"display":"flex","justifyContent":"space-between","alignItems":"center"}),

        html.Div([
            html.Div([
                html.Div("Liste des cours", className="card-header"),
                html.Div(html.Div(id="cours-list-admin", children=_build_list()), className="card-body p-0"),
            ], className="card"),
        ], className="page-body"),

        # Modal ajout/modif
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(html.Span(id="modal-cours-title-admin", children="Nouveau cours"))),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([dbc.Label("Code *"),           dbc.Input(id="inp-code-admin",       placeholder="ex : MATH101")], width=6),
                    dbc.Col([dbc.Label("Volume horaire *"), dbc.Input(id="inp-volume-admin",     type="number", min=1, placeholder="ex : 60")], width=6),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([dbc.Label("Intitulé *"),       dbc.Input(id="inp-libelle-admin",    placeholder="ex : Mathématiques")], width=6),
                    dbc.Col([dbc.Label("Enseignant"),       dbc.Input(id="inp-enseignant-admin", placeholder="ex : Prof. Dupont")], width=6),
                ], className="mb-3"),
                html.Div(id="cours-form-feedback-admin"),
                dcc.Store(id="store-edit-code-admin"),
            ]),
            dbc.ModalFooter([
                dbc.Button("Annuler",     id="btn-cancel-cours-admin", color="secondary", outline=True),
                dbc.Button("Enregistrer", id="btn-save-cours-admin",   color="primary"),
            ]),
        ], id="modal-cours-admin", is_open=False),

        # Modal suppression
        dbc.Modal([
            dbc.ModalHeader("Confirmer la suppression"),
            dbc.ModalBody(html.P(id="del-cours-msg-admin")),
            dbc.ModalFooter([
                dbc.Button("Annuler",    id="btn-cancel-del-cours-admin",  color="secondary", outline=True),
                dbc.Button("Supprimer",  id="btn-confirm-del-cours-admin", color="danger"),
            ]),
            dcc.Store(id="store-del-code-admin"),
        ], id="modal-del-cours-admin", is_open=False),
    ])


@callback(
    Output("modal-cours-admin","is_open",allow_duplicate=True),
    Output("inp-code-admin","value",allow_duplicate=True),
    Output("inp-libelle-admin","value",allow_duplicate=True),
    Output("inp-volume-admin","value",allow_duplicate=True),
    Output("inp-enseignant-admin","value",allow_duplicate=True),
    Output("store-edit-code-admin","data",allow_duplicate=True),
    Output("modal-cours-title-admin","children",allow_duplicate=True),
    Input("btn-open-modal-cours-admin","n_clicks"),
    prevent_initial_call=True,
)
def open_new(_):
    return True,"","",None,"",None,"Nouveau cours"


@callback(
    Output("modal-cours-admin","is_open",allow_duplicate=True),
    Output("inp-code-admin","value",allow_duplicate=True),
    Output("inp-libelle-admin","value",allow_duplicate=True),
    Output("inp-volume-admin","value",allow_duplicate=True),
    Output("inp-enseignant-admin","value",allow_duplicate=True),
    Output("store-edit-code-admin","data",allow_duplicate=True),
    Output("modal-cours-title-admin","children",allow_duplicate=True),
    Input({"type":"btn-edit-cours-admin","index":dash.ALL},"n_clicks"),
    prevent_initial_call=True,
)
def open_edit(n):
    if not any(n): return [dash.no_update]*7
    code = ctx.triggered_id["index"]
    db = SessionLocal()
    try:
        c = db.query(Course).filter_by(code=code).first()
        if not c: return [dash.no_update]*7
        return True, c.code, c.libelle, c.volume_h, c.enseignant or "", code, f"Modifier · {c.code}"
    finally:
        db.close()


@callback(Output("modal-cours-admin","is_open",allow_duplicate=True), Input("btn-cancel-cours-admin","n_clicks"), prevent_initial_call=True)
def close_modal(_): return False


@callback(
    Output("cours-list-admin","children"),
    Output("cours-form-feedback-admin","children"),
    Output("modal-cours-admin","is_open",allow_duplicate=True),
    Input("btn-save-cours-admin","n_clicks"),
    State("inp-code-admin","value"), State("inp-libelle-admin","value"),
    State("inp-volume-admin","value"), State("inp-enseignant-admin","value"),
    State("store-edit-code-admin","data"),
    prevent_initial_call=True,
)
def save(_, code, libelle, volume, enseignant, edit_code):
    if not code or not libelle or not volume:
        return dash.no_update, dbc.Alert("Champs obligatoires manquants (*)", color="warning"), True
    code = code.strip().upper()
    db = SessionLocal()
    try:
        if edit_code:
            c = db.query(Course).filter_by(code=edit_code).first()
            if c:
                c.libelle = libelle.strip(); c.volume_h = int(volume)
                c.enseignant = enseignant.strip() if enseignant else None
        else:
            if db.query(Course).filter_by(code=code).first():
                return dash.no_update, dbc.Alert(f"Le cours '{code}' existe déjà.", color="danger"), True
            db.add(Course(code=code, libelle=libelle.strip(), volume_h=int(volume),
                          enseignant=enseignant.strip() if enseignant else None))
        db.commit()
    except Exception as e:
        db.rollback()
        return dash.no_update, dbc.Alert(f"Erreur : {e}", color="danger"), True
    finally:
        db.close()
    return _build_list(), "", False


@callback(
    Output("modal-del-cours-admin","is_open",allow_duplicate=True),
    Output("del-cours-msg-admin","children"), Output("store-del-code-admin","data"),
    Input({"type":"btn-del-cours-admin","index":dash.ALL},"n_clicks"),
    prevent_initial_call=True,
)
def open_del(n):
    if not any(n): return dash.no_update,"",dash.no_update
    code = ctx.triggered_id["index"]
    return True, f"Supprimer le cours '{code}' et toutes ses séances ?", code


@callback(Output("modal-del-cours-admin","is_open",allow_duplicate=True), Input("btn-cancel-del-cours-admin","n_clicks"), prevent_initial_call=True)
def cancel_del(_): return False


@callback(
    Output("cours-list-admin","children",allow_duplicate=True),
    Output("modal-del-cours-admin","is_open",allow_duplicate=True),
    Input("btn-confirm-del-cours-admin","n_clicks"),
    State("store-del-code-admin","data"),
    prevent_initial_call=True,
)
def confirm_del(_, code):
    if not code: return dash.no_update, False
    db = SessionLocal()
    try:
        c = db.query(Course).filter_by(code=code).first()
        if c: db.delete(c); db.commit()
    except: db.rollback()
    finally: db.close()
    return _build_list(), False
