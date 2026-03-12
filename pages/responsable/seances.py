import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash
from database import SessionLocal
from models import Course, Session as CourseSession, Student, Attendance
from datetime import date
dash.register_page(__name__, path='/responsable/seances', title='seances — Responsable SGA')




def course_options():
    db = SessionLocal()
    try:
        return [{"label": f"{c.code} — {c.libelle}", "value": c.code} for c in db.query(Course).all()]
    finally:
        db.close()


def get_sessions(filter_course=None, sort_by="date"):
    db = SessionLocal()
    try:
        q = db.query(CourseSession).join(Course)
        if filter_course:
            q = q.filter(CourseSession.course_code == filter_course)
        q = q.order_by(CourseSession.course_code if sort_by == "cours" else CourseSession.date.desc())
        result = []
        for s in q.all():
            result.append({
                "id": s.id, "date": str(s.date),
                "cours": f"{s.course_code} — {s.course.libelle}",
                "duree": s.duree, "theme": s.theme or "—",
                "absents": len(s.attendances),
            })
        return result
    finally:
        db.close()


def layout():
    opts  = course_options()
    today = str(date.today())

    return html.Div([
        html.Div([
            html.H2("Séances & Présences"),
            html.Div("Cahier de texte numérique et appel", className="page-sub"),
        ], className="page-header"),

        html.Div([
            dbc.Tabs([
                dbc.Tab(label="Nouvelle séance", tab_id="tab-new", children=[
                    html.Div([
                        html.Div("Enregistrement de séance", className="card-header"),
                        html.Div([
                            dbc.Row([
                                dbc.Col([dbc.Label("Cours *"), dcc.Dropdown(id="sel-cours-seance-resp", options=opts, placeholder="Sélectionner un cours")], width=5),
                                dbc.Col([dbc.Label("Date *"),  dbc.Input(id="inp-date-seance-resp", type="date", value=today)], width=3),
                                dbc.Col([dbc.Label("Durée (h) *"), dbc.Input(id="inp-duree-seance-resp", type="number", min=0.5, step=0.5)], width=2),
                                dbc.Col([dbc.Label("Thème abordé"), dbc.Input(id="inp-theme-seance-resp", placeholder="ex : Algèbre ch.1")], width=2),
                            ], className="mb-4"),

                            html.Div([
                                html.Div("Appel numérique — cocher les absents", style={
                                    "fontSize":"11px","fontWeight":"600","textTransform":"uppercase",
                                    "letterSpacing":"0.08em","color":"var(--grey-400)","marginBottom":"12px"
                                }),
                                html.Div(id="checklist-absents-resp"),
                            ], style={"background":"var(--off-white)","borderRadius":"8px","padding":"16px","marginBottom":"16px"}),

                            html.Div(id="seance-feedback-resp"),
                            dbc.Button("Enregistrer la séance", id="btn-save-seance-resp", color="primary"),
                        ], className="card-body"),
                    ], className="card mt-3"),
                ]),

                dbc.Tab(label="Historique", tab_id="tab-hist", children=[
                    html.Div([
                        html.Div("Historique des séances", className="card-header"),
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Filtrer par cours"),
                                    dcc.Dropdown(id="filter-hist-cours-resp",
                                                 options=[{"label":"Tous les cours","value":""}]+opts,
                                                 value="", clearable=False),
                                ], width=4),
                                dbc.Col([
                                    dbc.Label("Trier par"),
                                    dcc.RadioItems(id="sort-hist-resp",
                                                   options=[{"label":" Date","value":"date"},{"label":" Cours","value":"cours"}],
                                                   value="date", inline=True,
                                                   inputStyle={"marginRight":"5px","marginLeft":"14px"}),
                                ], width=4),
                                dbc.Col(dbc.Button("Actualiser", id="btn-refresh-hist-resp", color="secondary", outline=True, className="mt-4"), width=2),
                            ], className="mb-3"),
                            html.Div(id="hist-table-resp"),
                        ], className="card-body"),
                    ], className="card mt-3"),
                ]),
            ], active_tab="tab-new"),
        ], className="page-body"),
    ])


@callback(Output("checklist-absents-resp","children"), Input("sel-cours-seance-resp","value"))
def update_checklist(_):
    db = SessionLocal()
    try:
        students = db.query(Student).order_by(Student.nom).all()
        if not students:
            return dbc.Alert("Aucun étudiant enregistré.", color="info")
        return dbc.Checklist(
            id="absents-checklist-resp",
            options=[{"label": f"  {s.prenom} {s.nom}", "value": s.id} for s in students],
            value=[], switch=True,
        )
    finally:
        db.close()


@callback(
    Output("seance-feedback-resp","children"),
    Input("btn-save-seance-resp","n_clicks"),
    State("sel-cours-seance-resp","value"), State("inp-date-seance-resp","value"),
    State("inp-duree-seance-resp","value"), State("inp-theme-seance-resp","value"),
    State("absents-checklist-resp","value"),
    prevent_initial_call=True,
)
def save_seance(_, course_code, date_str, duree, theme, absents):
    if not course_code or not date_str or not duree:
        return dbc.Alert("Champs obligatoires manquants (*)", color="warning")
    db = SessionLocal()
    try:
        from datetime import datetime
        s = CourseSession(
            course_code=course_code,
            date=datetime.strptime(date_str, "%Y-%m-%d").date(),
            duree=float(duree),
            theme=theme.strip() if theme else None,
        )
        db.add(s); db.flush()
        nb = 0
        for sid in (absents or []):
            db.add(Attendance(id_session=s.id, id_student=sid)); nb += 1
        db.commit()
        return dbc.Alert(f"Séance enregistrée. {nb} absent(s) marqué(s).", color="success", dismissable=True)
    except Exception as e:
        db.rollback(); return dbc.Alert(f"Erreur : {e}", color="danger")
    finally:
        db.close()


@callback(
    Output("hist-table-resp","children"),
    Input("btn-refresh-hist-resp","n_clicks"),
    Input("filter-hist-cours-resp","value"),
    Input("sort-hist-resp","value"),
)
def update_hist(_, fc, sort):
    sessions = get_sessions(filter_course=fc or None, sort_by=sort)
    if not sessions:
        return dbc.Alert("Aucune séance enregistrée.", color="info")
    header = html.Thead(html.Tr([html.Th("Date"),html.Th("Cours"),html.Th("Durée"),html.Th("Thème"),html.Th("Absents")]))
    rows = [html.Tr([
        html.Td(s["date"]), html.Td(s["cours"]), html.Td(f"{s['duree']}h"),
        html.Td(s["theme"]),
        html.Td(dbc.Badge(str(s["absents"]), color="danger" if s["absents"]>0 else "success")),
    ]) for s in sessions]
    return dbc.Table([header, html.Tbody(rows)], striped=False, hover=True, responsive=True, bordered=False)
