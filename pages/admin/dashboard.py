import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from collections import Counter
from database import SessionLocal
from models import Student, Course, Session as CS, Grade, User, Attendance

dash.register_page(__name__, path="/admin/dashboard", title="Dashboard Admin — SGA")


def kpi(val, label, color, sub=None):
    return html.Div([
        html.Div(str(val), className="kpi-val"),
        html.Div(label, className="kpi-lbl"),
        html.Div(sub, style={"fontSize": "11.5px", "color": "#9CA3AF", "marginTop": "4px"}) if sub else None,
    ], className="kpi-card", style={"--kpi-color": color})


def layout():
    return html.Div([html.Div(id="admin-dash-content")])


@callback(
    Output("admin-dash-content", "children"),
    Input("url", "pathname"),
    State("session-store", "data"),
)
def render(pathname, session):
    if pathname != "/admin/dashboard":
        return dash.no_update

    db = SessionLocal()
    try:
        nb_s        = db.query(Student).count()
        nb_c        = db.query(Course).count()
        nb_e        = db.query(CS).count()
        nb_n        = db.query(Grade).count()
        nb_u        = db.query(User).count()
        nb_abs      = db.query(Attendance).count()

        grades_raw  = db.query(Grade).all()
        if grades_raw:
            pts   = sum(g.note * g.coefficient for g in grades_raw)
            coeff = sum(g.coefficient for g in grades_raw)
            moy   = round(pts / coeff, 2) if coeff else 0
        else:
            moy = 0

        all_notes   = [g.note for g in grades_raw]
        students_recent = db.query(Student).order_by(Student.id.desc()).limit(6).all()
        recent_data = [{"nom": s.nom, "prenom": s.prenom, "classe": s.classe or "—"}
                       for s in students_recent]

        classes_ctr  = Counter(s.classe for s in db.query(Student).all() if s.classe)

        courses_raw  = db.query(Course).all()
        courses_data = []
        for c in courses_raw:
            sess  = db.query(CS).filter_by(course_code=c.code).all()
            done  = sum(s.duree for s in sess)
            pct   = min(int(done / c.volume_h * 100), 100) if c.volume_h else 0
            courses_data.append({"libelle": c.libelle, "done": done,
                                  "vol": c.volume_h, "pct": pct})
    finally:
        db.close()

    prenom = (session or {}).get("prenom", "Admin")

    # --- Gauge moyenne globale ---
    gc = "#10B981" if moy >= 10 else "#EF4444"
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=moy,
        number={"suffix": "/20", "font": {"size": 30, "color": gc}},
        gauge={
            "axis": {"range": [0, 20], "tickfont": {"size": 10}},
            "bar": {"color": gc, "thickness": 0.25},
            "bgcolor": "white", "borderwidth": 0,
            "steps": [
                {"range": [0,  10], "color": "rgba(239,68,68,0.07)"},
                {"range": [10, 14], "color": "rgba(16,185,129,0.07)"},
                {"range": [14, 20], "color": "rgba(16,185,129,0.16)"},
            ],
            "threshold": {"line": {"color": gc, "width": 3}, "thickness": 0.8, "value": moy},
        },
        title={"text": "Moyenne générale étudiants", "font": {"size": 12, "color": "#6B7280"}},
    ))
    fig_gauge.update_layout(
        height=220, margin=dict(t=30, b=10, l=20, r=20),
        paper_bgcolor="white", font=dict(family="Inter, sans-serif"),
    )

    # --- Histogramme distribution des notes ---
    if all_notes:
        fig_hist = go.Figure(go.Histogram(
            x=all_notes,
            nbinsx=20,
            marker_color="rgba(16,110,190,0.70)",
            marker_line=dict(color="white", width=0.8),
            hovertemplate="Note %{x:.0f} : %{y} évaluations<extra></extra>",
        ))
        fig_hist.add_vline(x=10, line_dash="dash", line_color="rgba(239,68,68,0.5)",
                           annotation_text="10/20", annotation_font_size=10)
        fig_hist.add_vline(x=moy, line_dash="dot", line_color=gc,
                           annotation_text=f"Moy. {moy}", annotation_font_size=10,
                           annotation_font_color=gc)
        fig_hist.update_layout(
            height=220, margin=dict(t=15, b=10, l=0, r=0),
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Inter, sans-serif"),
            yaxis=dict(gridcolor="#F3F4F6", tickfont=dict(size=10)),
            xaxis=dict(showgrid=False, tickfont=dict(size=10), title="Note /20",
                       title_font=dict(size=11)),
            bargap=0.05,
        )
    else:
        fig_hist = go.Figure()

    # --- Pie chart répartition par classe ---
    if classes_ctr:
        PALETTE = ["#1E6EBE", "#10B981", "#7C3AED", "#F59E0B", "#EF4444", "#06B6D4"]
        fig_pie = go.Figure(go.Pie(
            labels=list(classes_ctr.keys()),
            values=list(classes_ctr.values()),
            hole=0.55,
            marker=dict(colors=PALETTE[:len(classes_ctr)],
                        line=dict(color="white", width=2)),
            textinfo="label+percent",
            textfont=dict(size=11, family="Inter, sans-serif"),
            hovertemplate="%{label}: %{value} étudiant(s)<extra></extra>",
        ))
        fig_pie.update_layout(
            height=220, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="white", showlegend=False,
            font=dict(family="Inter, sans-serif"),
            annotations=[dict(text=f"{nb_s}<br><span>étudiants</span>",
                              x=0.5, y=0.5, font_size=16, showarrow=False,
                              font=dict(color="#1E6EBE", family="Inter, sans-serif"))],
        )
    else:
        fig_pie = go.Figure()

    # --- Course progress bars ---
    def prog_bar(c):
        color = "#10B981" if c["pct"] >= 75 else ("#F59E0B" if c["pct"] >= 40 else "#EF4444")
        return html.Div([
            html.Div([
                html.Span(c["libelle"], style={"fontWeight": "600", "fontSize": "13px"}),
                html.Span(f"{c['done']}h / {c['vol']}h",
                          style={"fontSize": "12px", "color": "#9CA3AF", "marginLeft": "auto"}),
            ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}),
            html.Div(html.Div(style={
                "height": "7px", "width": f"{c['pct']}%",
                "background": color, "borderRadius": "4px", "transition": "width 0.4s",
            }), style={"background": "#F3F4F6", "borderRadius": "4px"}),
        ], style={"marginBottom": "14px"})

    return html.Div([
        html.Div([
            html.H2("Tableau de bord"),
            html.Div(f"Vue d'ensemble · Connecté : {prenom}", className="page-sub"),
        ], className="page-header"),

        html.Div([
            dbc.Row([
                dbc.Col(kpi(nb_s, "Étudiants",     "#1E6EBE"),   md=3, className="mb-3"),
                dbc.Col(kpi(nb_c, "Cours",          "#10B981"),   md=3, className="mb-3"),
                dbc.Col(kpi(nb_e, "Séances",        "#7C3AED"),   md=3, className="mb-3"),
                dbc.Col(kpi(nb_n, "Notes saisies",  "#F59E0B"),   md=3, className="mb-3"),
                dbc.Col(kpi(nb_abs, "Absences",     "#EF4444"),   md=3, className="mb-3"),
                dbc.Col(kpi(f"{moy}/20", "Moy. générale", gc),    md=3, className="mb-3"),
                dbc.Col(kpi(nb_u, "Utilisateurs",   "#6B7280"),   md=3, className="mb-3"),
            ]),

            # Ligne 1 : Gauge + Histogramme + Pie
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
                        html.Div("Distribution des notes", className="card-header"),
                        html.Div(dcc.Graph(figure=fig_hist, config={"displayModeBar": False}),
                                 className="card-body"),
                    ], className="card card-accent-blue"),
                ], md=4),
                dbc.Col([
                    html.Div([
                        html.Div("Étudiants par classe", className="card-header"),
                        html.Div(dcc.Graph(figure=fig_pie, config={"displayModeBar": False}),
                                 className="card-body"),
                    ], className="card"),
                ], md=4),
            ], className="mb-4"),

            # Ligne 2 : Progression cours + Étudiants récents
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div("Progression des cours", className="card-header"),
                        html.Div(
                            [prog_bar(c) for c in courses_data] if courses_data
                            else html.Div("Aucun cours.", style={"color": "#9CA3AF"}),
                            className="card-body",
                        ),
                    ], className="card card-accent-blue"),
                ], md=7),
                dbc.Col([
                    html.Div([
                        html.Div("Étudiants récents", className="card-header"),
                        html.Div(
                            html.Table([
                                html.Thead(html.Tr([html.Th("Nom"), html.Th("Prénom"), html.Th("Classe")])),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(s["nom"], style={"fontWeight": "600"}),
                                        html.Td(s["prenom"]),
                                        html.Td(html.Span(s["classe"],
                                                          style={"background": "rgba(16,110,190,0.09)",
                                                                 "color": "#1E6EBE", "borderRadius": "20px",
                                                                 "padding": "2px 10px", "fontSize": "11px",
                                                                 "fontWeight": "600"})),
                                    ]) for s in recent_data
                                ]),
                            ], className="table"),
                            className="card-body", style={"padding": "0", "overflowX": "auto"},
                        ),
                    ], className="card card-accent-mint"),
                ], md=5),
            ]),
        ], className="page-body"),
    ])
