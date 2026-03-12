import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from database import SessionLocal
from models import Student, Attendance, Session as CS

dash.register_page(__name__, path="/etudiant/absences", title="Mes absences — SGA")


def layout():
    return html.Div([html.Div(id="etud-abs-content")])


@callback(
    Output("etud-abs-content", "children"),
    Input("url", "pathname"),
    State("session-store", "data"),
)
def render(pathname, session):
    if pathname != "/etudiant/absences":
        return dash.no_update

    student_id = (session or {}).get("student_id")
    db = SessionLocal()
    try:
        student = (db.query(Student).filter_by(id=student_id).first()
                   if student_id else db.query(Student).first())
        if not student:
            return html.Div("Étudiant non trouvé.", className="page-body")

        nom_complet   = f"{student.prenom} {student.nom}"
        total_sessions = db.query(CS).count()

        atts = db.query(Attendance).filter_by(id_student=student.id).all()
        att_data = []
        for a in atts:
            sess = a.session
            att_data.append({
                "type": a.type_abs,
                "date":  str(sess.date)  if sess else "—",
                "cours": sess.course.libelle if sess and sess.course else "—",
                "theme": sess.theme       if sess else "—",
                "duree": f"{sess.duree}h" if sess else "—",
            })
    finally:
        db.close()

    nb_abs = sum(1 for a in att_data if a["type"] == "absence")
    nb_ret = sum(1 for a in att_data if a["type"] == "retard")
    nb_ok  = max(0, total_sessions - nb_abs - nb_ret)
    taux   = round(nb_abs / total_sessions * 100, 1) if total_sessions else 0

    # --- Donut chart présences ---
    fig_donut = go.Figure(go.Pie(
        labels=["Présent", "Absent", "Retard"],
        values=[nb_ok, nb_abs, nb_ret],
        hole=0.62,
        marker=dict(colors=["#10B981", "#EF4444", "#F59E0B"],
                    line=dict(color="white", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, family="Inter, sans-serif"),
        hovertemplate="%{label}: %{value} séance(s)<extra></extra>",
    ))
    fig_donut.update_layout(
        height=210, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="white",
        showlegend=False,
        annotations=[dict(text=f"{100 - taux:.0f}%<br><span style='font-size:10px'>présence</span>",
                          x=0.5, y=0.5, font_size=18, showarrow=False,
                          font=dict(color="#10B981", family="Inter, sans-serif"))],
    )

    # --- Gauge taux d'absentéisme ---
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=taux,
        number={"suffix": "%", "font": {"size": 28,
                "color": "#EF4444" if taux > 20 else "#10B981"}},
        gauge={
            "axis": {"range": [0, 50], "tickfont": {"size": 10}},
            "bar": {"color": "#EF4444" if taux > 20 else "#10B981", "thickness": 0.25},
            "bgcolor": "white", "borderwidth": 0,
            "steps": [
                {"range": [0,  15], "color": "rgba(16,185,129,0.08)"},
                {"range": [15, 25], "color": "rgba(245,158,11,0.08)"},
                {"range": [25, 50], "color": "rgba(239,68,68,0.08)"},
            ],
        },
        title={"text": "Taux d'absentéisme", "font": {"size": 12, "color": "#6B7280"}},
    ))
    fig_gauge.update_layout(
        height=210, margin=dict(t=30, b=5, l=20, r=20),
        paper_bgcolor="white", font=dict(family="Inter, sans-serif"),
    )

    def statut_badge(t):
        if t == "absence":
            return html.Span("Absent",
                              style={"background": "rgba(239,68,68,0.09)", "color": "#EF4444",
                                     "borderRadius": "20px", "padding": "2px 10px",
                                     "fontSize": "11px", "fontWeight": "600"})
        return html.Span("Retard",
                          style={"background": "rgba(245,158,11,0.09)", "color": "#D97706",
                                 "borderRadius": "20px", "padding": "2px 10px",
                                 "fontSize": "11px", "fontWeight": "600"})

    rows = [html.Tr([
        html.Td(a["date"], style={"fontWeight": "600", "whiteSpace": "nowrap"}),
        html.Td(a["cours"], style={"fontWeight": "500"}),
        html.Td(a["theme"], style={"color": "#6B7280", "fontSize": "12.5px"}),
        html.Td(a["duree"]),
        html.Td(statut_badge(a["type"])),
    ]) for a in att_data] or [
        html.Tr([html.Td("Aucune absence enregistrée.", colSpan=5,
                          style={"textAlign": "center", "color": "#6B7280", "padding": "24px"})])
    ]

    return html.Div([
        html.Div([
            html.H2("Mes absences & retards"),
            html.Div(f"Étudiant : {nom_complet}", className="page-sub"),
        ], className="page-header"),

        html.Div([
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div(str(nb_abs), className="kpi-val"),
                    html.Div("Absences", className="kpi-lbl"),
                ], className="kpi-card", style={"--kpi-color": "#EF4444"}), md=3, className="mb-3"),
                dbc.Col(html.Div([
                    html.Div(str(nb_ret), className="kpi-val"),
                    html.Div("Retards", className="kpi-lbl"),
                ], className="kpi-card", style={"--kpi-color": "#F59E0B"}), md=3, className="mb-3"),
                dbc.Col(html.Div([
                    html.Div(str(total_sessions), className="kpi-val"),
                    html.Div("Séances totales", className="kpi-lbl"),
                ], className="kpi-card", style={"--kpi-color": "#1E6EBE"}), md=3, className="mb-3"),
                dbc.Col(html.Div([
                    html.Div(f"{taux}%", className="kpi-val"),
                    html.Div("Taux d'absentéisme", className="kpi-lbl"),
                ], className="kpi-card",
                   style={"--kpi-color": "#EF4444" if taux > 20 else "#10B981"}), md=3, className="mb-3"),
            ]),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div("Répartition des présences", className="card-header"),
                        html.Div(dcc.Graph(figure=fig_donut, config={"displayModeBar": False}),
                                 className="card-body"),
                    ], className="card card-accent-mint"),
                ], md=5),
                dbc.Col([
                    html.Div([
                        html.Div("Gauge absentéisme", className="card-header"),
                        html.Div(dcc.Graph(figure=fig_gauge, config={"displayModeBar": False}),
                                 className="card-body"),
                    ], className="card card-accent-blue"),
                ], md=4),
                dbc.Col([
                    html.Div([
                        html.Div("Rappel", className="card-header"),
                        html.Div([
                            html.Strong("Note : ", style={"color": "#D97706"}),
                            html.Span(
                                "Toute absence non justifiée peut entraîner des sanctions académiques. "
                                "Contactez votre responsable de classe pour toute justification.",
                                style={"fontSize": "13px", "color": "#92400E"},
                            ),
                        ], className="card-body",
                           style={"background": "rgba(245,158,11,0.06)",
                                  "borderLeft": "3px solid #F59E0B"}),
                    ], className="card"),
                ], md=3),
            ], className="mb-4"),

            html.Div([
                html.Div("Historique des absences et retards", className="card-header"),
                html.Div(
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th("Date"), html.Th("Cours"), html.Th("Thème"),
                            html.Th("Durée"), html.Th("Statut"),
                        ])),
                        html.Tbody(rows),
                    ], className="table"),
                    className="card-body", style={"padding": "0", "overflowX": "auto"},
                ),
            ], className="card card-accent-blue"),
        ], className="page-body"),
    ])
