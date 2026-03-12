import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from database import SessionLocal
from models import Student, Grade

dash.register_page(__name__, path="/etudiant/notes", title="Mes notes — SGA")


def layout():
    return html.Div([html.Div(id="etud-notes-content")])


@callback(
    Output("etud-notes-content", "children"),
    Input("url", "pathname"),
    State("session-store", "data"),
)
def render(pathname, session):
    if pathname != "/etudiant/notes":
        return dash.no_update

    student_id = (session or {}).get("student_id")
    db = SessionLocal()
    try:
        student = (db.query(Student).filter_by(id=student_id).first()
                   if student_id else db.query(Student).first())
        if not student:
            return html.Div("Étudiant non trouvé.", className="page-body")

        nom_complet = f"{student.prenom} {student.nom}"
        grades_raw  = db.query(Grade).filter_by(id_student=student.id).all()
        grades_data = [{
            "note":      g.note,
            "coeff":     g.coefficient,
            "type_eval": g.type_eval or "devoir",
            "cours":     g.course.libelle if g.course else g.course_code,
        } for g in grades_raw]
    finally:
        db.close()

    if not grades_data:
        return html.Div([
            html.Div([html.H2("Mes notes"), html.Div("Aucune note disponible.", className="page-sub")],
                     className="page-header"),
            html.Div("Aucune note enregistrée pour votre profil.",
                     style={"color": "#6B7280", "textAlign": "center", "padding": "60px"},
                     className="page-body"),
        ])

    pts   = sum(g["note"] * g["coeff"] for g in grades_data)
    coeff = sum(g["coeff"] for g in grades_data)
    moy   = round(pts / coeff, 2) if coeff else 0
    admis = sum(1 for g in grades_data if g["note"] >= 10)

    # --- Gauge moyenne ---
    gc = "#10B981" if moy >= 10 else "#EF4444"
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=moy,
        number={"suffix": "/20", "font": {"size": 30, "color": gc}},
        gauge={
            "axis": {"range": [0, 20], "tickfont": {"size": 10}},
            "bar": {"color": gc, "thickness": 0.26},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  10], "color": "rgba(239,68,68,0.07)"},
                {"range": [10, 14], "color": "rgba(16,185,129,0.07)"},
                {"range": [14, 20], "color": "rgba(16,185,129,0.16)"},
            ],
            "threshold": {"line": {"color": gc, "width": 3}, "thickness": 0.8, "value": moy},
        },
        title={"text": "Moyenne pondérée", "font": {"size": 12, "color": "#6B7280"}},
    ))
    fig_gauge.update_layout(
        height=210, margin=dict(t=30, b=5, l=20, r=20),
        paper_bgcolor="white", font=dict(family="Inter, sans-serif"),
    )

    # --- Bar chart notes ---
    matieres = [g["cours"] for g in grades_data]
    notes    = [g["note"]  for g in grades_data]
    bar_colors = ["rgba(16,185,129,0.85)" if n >= 10 else "rgba(239,68,68,0.82)" for n in notes]
    fig_bar = go.Figure(go.Bar(
        x=matieres, y=notes,
        marker_color=bar_colors,
        text=[f"{n}" for n in notes], textposition="outside",
        textfont=dict(size=11),
    ))
    fig_bar.add_hline(y=10, line_dash="dash", line_color="rgba(107,114,128,0.35)",
                      annotation_text="Barre 10/20", annotation_font_size=10)
    fig_bar.update_layout(
        height=210, margin=dict(t=10, b=10, l=0, r=0),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter, sans-serif"),
        yaxis=dict(range=[0, 24], gridcolor="#F3F4F6", tickfont=dict(size=10)),
        xaxis=dict(showgrid=False, tickfont=dict(size=9)),
        showlegend=False,
    )

    type_badge = {
        "devoir": ("Devoir", "rgba(16,110,190,0.09)", "#1E6EBE"),
        "examen": ("Examen", "rgba(124,58,237,0.09)", "#7C3AED"),
        "partiel": ("Partiel", "rgba(245,158,11,0.09)", "#D97706"),
    }

    def badge(t):
        label, bg, color = type_badge.get(t, (t.capitalize(), "#F3F4F6", "#6B7280"))
        return html.Span(label, style={
            "background": bg, "color": color, "borderRadius": "20px",
            "padding": "2px 10px", "fontSize": "11px", "fontWeight": "600",
        })

    rows = [html.Tr([
        html.Td(g["cours"], style={"fontWeight": "600"}),
        html.Td(badge(g["type_eval"])),
        html.Td(html.Span(f"{g['note']}/20", style={
            "fontWeight": "700",
            "color": "#10B981" if g["note"] >= 10 else "#EF4444",
        })),
        html.Td(g["coeff"]),
        html.Td(html.Span(
            "Admis" if g["note"] >= 10 else "Ajourné",
            className="badge bg-success" if g["note"] >= 10 else "badge bg-danger",
        )),
    ]) for g in grades_data]

    return html.Div([
        html.Div([
            html.H2("Mes notes & évaluations"),
            html.Div(f"Étudiant : {nom_complet}", className="page-sub"),
        ], className="page-header"),

        html.Div([
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div(f"{moy}/20", className="kpi-val"),
                    html.Div("Moyenne générale", className="kpi-lbl"),
                ], className="kpi-card",
                   style={"--kpi-color": "#10B981" if moy >= 10 else "#EF4444"}), md=4, className="mb-3"),
                dbc.Col(html.Div([
                    html.Div(str(admis), className="kpi-val"),
                    html.Div("Matières admises", className="kpi-lbl"),
                ], className="kpi-card", style={"--kpi-color": "#10B981"}), md=4, className="mb-3"),
                dbc.Col(html.Div([
                    html.Div(str(len(grades_data) - admis), className="kpi-val"),
                    html.Div("Matières à repasser", className="kpi-lbl"),
                ], className="kpi-card", style={"--kpi-color": "#EF4444"}), md=4, className="mb-3"),
            ]),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div("Gauge — Moyenne", className="card-header"),
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
                ], md=8),
            ], className="mb-4"),

            html.Div([
                html.Div("Détail des évaluations", className="card-header"),
                html.Div(
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th("Matière"), html.Th("Type"), html.Th("Note"),
                            html.Th("Coeff"), html.Th("Mention"),
                        ])),
                        html.Tbody(rows),
                    ], className="table"),
                    className="card-body", style={"padding": "0", "overflowX": "auto"},
                ),
            ], className="card card-accent-blue"),
        ], className="page-body"),
    ])
