import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from database import SessionLocal
from models import Course, Session as CourseSession, Student, Attendance

dash.register_page(__name__, path='/admin/seances', title='Séances & Présences — Admin SGA')


def course_options():
    db = SessionLocal()
    try:
        return [{"label": f"{c.code} — {c.libelle}", "value": c.code}
                for c in db.query(Course).all()]
    finally:
        db.close()


def build_history(filter_course=None):
    db = SessionLocal()
    try:
        q = db.query(CourseSession).join(Course)
        if filter_course:
            q = q.filter(CourseSession.course_code == filter_course)
        sessions = q.order_by(CourseSession.date.desc()).all()

        if not sessions:
            return dbc.Alert("Aucune séance enregistrée.", color="info")

        rows = []
        for s in sessions:
            # Récupérer les absents avec leurs noms
            absences = (db.query(Attendance, Student)
                        .join(Student, Attendance.id_student == Student.id)
                        .filter(Attendance.id_session == s.id)
                        .all())

            nb_abs = sum(1 for a, _ in absences if a.type_abs == "absence")
            nb_ret = sum(1 for a, _ in absences if a.type_abs == "retard")

            # Liste des absents/retards
            abs_list = html.Div([
                html.Span(
                    f"{st.prenom} {st.nom} {'(R)' if a.type_abs=='retard' else ''}",
                    style={
                        "display":"inline-block","fontSize":"11.5px",
                        "background":"rgba(239,68,68,0.09)" if a.type_abs=="absence" else "rgba(245,158,11,0.10)",
                        "color":"var(--red)" if a.type_abs=="absence" else "var(--amber)",
                        "padding":"2px 8px","borderRadius":"20px","margin":"2px",
                        "fontWeight":"500",
                    }
                )
                for a, st in absences
            ]) if absences else html.Span("Tous présents ✓",
                                          style={"fontSize":"12px","color":"var(--green)","fontWeight":"600"})

            rows.append(html.Tr([
                html.Td(str(s.date), style={"fontWeight":"600","whiteSpace":"nowrap"}),
                html.Td(f"{s.course_code} — {s.course.libelle}",
                        style={"fontSize":"13px"}),
                html.Td(f"{s.duree}h", style={"textAlign":"center"}),
                html.Td(s.theme or "—", style={"color":"var(--grey-400)","fontSize":"12.5px"}),
                html.Td([
                    dbc.Badge(f"{nb_abs} abs", color="danger", className="me-1") if nb_abs else None,
                    dbc.Badge(f"{nb_ret} ret", color="warning") if nb_ret else None,
                    dbc.Badge("Complet", color="success") if not absences else None,
                ], style={"whiteSpace":"nowrap"}),
                html.Td(abs_list, style={"maxWidth":"320px"}),
            ]))

        return dbc.Table(
            [html.Thead(html.Tr([
                html.Th("Date"), html.Th("Cours"),
                html.Th("Durée", style={"textAlign":"center"}),
                html.Th("Thème"), html.Th("Bilan"), html.Th("Absents / Retards"),
            ])), html.Tbody(rows)],
            striped=False, hover=True, responsive=True, bordered=False
        )
    finally:
        db.close()


def layout():
    opts = course_options()
    return html.Div([
        html.Div([
            html.H2("Historique des séances"),
            html.Div("Suivi des présences et absences par séance", className="page-sub"),
        ], className="page-header"),

        html.Div([
            html.Div([
                html.Div("Filtres", className="card-header"),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Filtrer par cours"),
                            dcc.Dropdown(
                                id="filter-hist-cours-admin",
                                options=[{"label": "Tous les cours", "value": ""}] + opts,
                                value="", clearable=False,
                            ),
                        ], width=5),
                        dbc.Col([
                            dbc.Label("\u00a0"),
                            html.Div(
                                dbc.Button("Actualiser", id="btn-refresh-hist-admin",
                                           color="secondary", outline=True),
                            ),
                        ], width=2, style={"display":"flex","alignItems":"flex-end"}),
                    ]),
                ], className="card-body"),
            ], className="card mb-4"),

            html.Div([
                html.Div("Séances & présences", className="card-header"),
                html.Div(
                    html.Div(id="hist-table-admin", children=build_history()),
                    className="card-body p-0",
                ),
            ], className="card"),
        ], className="page-body"),
    ])


@callback(
    Output("hist-table-admin", "children"),
    Input("btn-refresh-hist-admin", "n_clicks"),
    Input("filter-hist-cours-admin", "value"),
)
def update_hist(_, fc):
    return build_history(filter_course=fc or None)
