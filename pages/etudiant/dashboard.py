import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from database import SessionLocal
from models import Student, Grade, Attendance, Session as CS, Course, User

dash.register_page(__name__, path="/etudiant/dashboard", title="Mon espace — SGA")


def layout():
    return html.Div([
        html.Div(id="etud-dash-content"),
    ])


@callback(
    Output("etud-dash-content", "children"),
    Input("url", "pathname"),
    State("session-store", "data"),
)
def render(pathname, session):
    if pathname != "/etudiant/dashboard":
        return dash.no_update

    # Résoudre l'étudiant connecté
    student_id = (session or {}).get("student_id")
    db = SessionLocal()
    try:
        if student_id:
            student = db.query(Student).filter_by(id=student_id).first()
        else:
            student = db.query(Student).first()
        if not student:
            return html.Div("Étudiant non trouvé.", className="page-body")

        sid = student.id
        nom_complet = f"{student.prenom} {student.nom}"
        classe = student.classe or "N/A"

        grades_raw = db.query(Grade).filter_by(id_student=sid).all()
        grades_data = [{
            "note": g.note,
            "coeff": g.coefficient,
            "cours": g.course.libelle if g.course else g.course_code,
        } for g in grades_raw]

        nb_abs = db.query(Attendance).filter_by(id_student=sid, type_abs="absence").count()
        nb_ret = db.query(Attendance).filter_by(id_student=sid, type_abs="retard").count()
        total_sess = db.query(CS).count()
    finally:
        db.close()

    # Moyenne générale
    if grades_data:
        pts   = sum(g["note"] * g["coeff"] for g in grades_data)
        coeff = sum(g["coeff"] for g in grades_data)
        moy   = round(pts / coeff, 2) if coeff else 0
    else:
        moy = 0

    admis = sum(1 for g in grades_data if g["note"] >= 10)

    # --- Gauge de moyenne ---
    gauge_color = "#10B981" if moy >= 10 else "#EF4444"
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=moy,
        number={"suffix": "/20", "font": {"size": 32, "color": gauge_color}},
        gauge={
            "axis": {"range": [0, 20], "tickfont": {"size": 11}},
            "bar": {"color": gauge_color, "thickness": 0.25},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  10], "color": "rgba(239,68,68,0.08)"},
                {"range": [10, 14], "color": "rgba(16,185,129,0.08)"},
                {"range": [14, 20], "color": "rgba(16,185,129,0.18)"},
            ],
            "threshold": {"line": {"color": gauge_color, "width": 3}, "thickness": 0.8, "value": moy},
        },
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Moyenne générale", "font": {"size": 13, "color": "#6B7280"}},
    ))
    fig_gauge.update_layout(
        height=220, margin=dict(t=30, b=10, l=20, r=20),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter, sans-serif"),
    )

    # --- Bar chart notes par matière ---
    if grades_data:
        matieres = [g["cours"] for g in grades_data]
        notes    = [g["note"]  for g in grades_data]
        colors   = ["rgba(16,185,129,0.85)" if n >= 10 else "rgba(239,68,68,0.85)" for n in notes]
        fig_bar = go.Figure(go.Bar(
            x=matieres, y=notes,
            marker_color=colors,
            text=[f"{n}" for n in notes], textposition="outside",
            textfont=dict(size=11, color="#374151"),
        ))
        fig_bar.add_hline(y=10, line_dash="dash", line_color="rgba(107,114,128,0.4)",
                          annotation_text="10/20", annotation_font_size=11)
        fig_bar.update_layout(
            height=220, margin=dict(t=10, b=10, l=0, r=0),
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Inter, sans-serif"),
            yaxis=dict(range=[0, 23], gridcolor="#F3F4F6", tickfont=dict(size=11)),
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            showlegend=False,
        )
    else:
        fig_bar = go.Figure()
        fig_bar.update_layout(height=220, paper_bgcolor="white")

    taux_abs = round(nb_abs / total_sess * 100, 1) if total_sess else 0

    return html.Div([
        html.Div([
            html.Div([
                html.H2(f"Bienvenue, {nom_complet}"),
                html.Div(f"Classe : {classe}  ·  Année 2025–2026", className="page-sub"),
            ]),
        ], className="page-header"),

        html.Div([
            # KPI row
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div(f"{moy}/20", className="kpi-val"),
                    html.Div("Moyenne générale", className="kpi-lbl"),
                ], className="kpi-card",
                   style={"--kpi-color": "#10B981" if moy >= 10 else "#EF4444"}), md=3, className="mb-3"),
                dbc.Col(html.Div([
                    html.Div(str(admis), className="kpi-val"),
                    html.Div("Matières admises", className="kpi-lbl"),
                ], className="kpi-card", style={"--kpi-color": "#10B981"}), md=3, className="mb-3"),
                dbc.Col(html.Div([
                    html.Div(str(nb_abs), className="kpi-val"),
                    html.Div("Absences", className="kpi-lbl"),
                ], className="kpi-card", style={"--kpi-color": "#EF4444"}), md=3, className="mb-3"),
                dbc.Col(html.Div([
                    html.Div(str(nb_ret), className="kpi-val"),
                    html.Div("Retards", className="kpi-lbl"),
                ], className="kpi-card", style={"--kpi-color": "#F59E0B"}), md=3, className="mb-3"),
            ]),

            # Gauge + Bar
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div("Moyenne générale", className="card-header"),
                        html.Div(dcc.Graph(figure=fig_gauge, config={"displayModeBar": False}),
                                 className="card-body"),
                    ], className="card card-accent-mint"),
                ], md=4),
                dbc.Col([
                    html.Div([
                        html.Div("Notes par matière", className="card-header"),
                        html.Div(dcc.Graph(figure=fig_bar, config={"displayModeBar": False}),
                                 className="card-body"),
                    ], className="card card-accent-blue"),
                ], md=5),
                dbc.Col([
                    html.Div([
                        html.Div("Accès rapide", className="card-header"),
                        html.Div([
                            html.A("Mes notes complètes →", href="/etudiant/notes", style={
                                "display": "block", "padding": "12px 16px", "borderRadius": "var(--r)",
                                "background": "rgba(16,110,190,0.07)", "color": "var(--blue)",
                                "fontWeight": "600", "fontSize": "13.5px", "marginBottom": "8px",
                            }),
                            html.A("Mes absences →", href="/etudiant/absences", style={
                                "display": "block", "padding": "12px 16px", "borderRadius": "var(--r)",
                                "background": "rgba(239,68,68,0.07)", "color": "#EF4444",
                                "fontWeight": "600", "fontSize": "13.5px", "marginBottom": "8px",
                            }),
                            html.A("Mes cours (PDF) →", href="/etudiant/cours", style={
                                "display": "block", "padding": "12px 16px", "borderRadius": "var(--r)",
                                "background": "rgba(16,185,129,0.08)", "color": "#059669",
                                "fontWeight": "600", "fontSize": "13.5px",
                            }),
                            html.Div([
                                html.Span(f"Taux d'absentéisme : ", style={"fontSize": "12px", "color": "#6B7280"}),
                                html.Span(f"{taux_abs}%", style={
                                    "fontWeight": "700", "fontSize": "13px",
                                    "color": "#EF4444" if taux_abs > 20 else "#10B981",
                                }),
                            ], style={"marginTop": "16px", "padding": "10px 16px",
                                      "background": "#F9FAFB", "borderRadius": "var(--r)"}),
                        ], className="card-body"),
                    ], className="card"),
                ], md=3),
            ]),
        ], className="page-body"),
    ])
