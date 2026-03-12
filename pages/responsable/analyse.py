import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import dash
import plotly.graph_objects as go
from database import SessionLocal
from models import Grade, Course
dash.register_page(__name__, path='/responsable/analyse', title='analyse — Responsable SGA')




def layout():
    return html.Div([
        html.Div([
            html.H2("Analyse de données"),
            html.Div("Distribution des notes, moyennes par matière et taux de réussite", className="page-sub"),
        ], className="page-header"),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div("Distribution des notes", className="card-header"),
                            html.Div(dcc.Graph(id="graph-histo-resp", config={"displayModeBar":False}), className="card-body"),
                    ], className="card"),
                ], width=12, lg=6, className="mb-4"),
                dbc.Col([
                    html.Div([
                        html.Div("Moyenne par matière", className="card-header"),
                        html.Div(dcc.Graph(id="graph-moy-resp", config={"displayModeBar":False}), className="card-body"),
                    ], className="card"),
                ], width=12, lg=6, className="mb-4"),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div("Répartition admis / refusés par matière", className="card-header"),
                        html.Div(dcc.Graph(id="graph-rate-resp", config={"displayModeBar":False}), className="card-body"),
                    ], className="card"),
                ], width=12),
            ]),
        ], className="page-body"),
        dcc.Interval(id="analyse-interval", interval=30000, n_intervals=0),
    ])


def _empty(msg):
    fig = go.Figure()
    fig.update_layout(height=260, plot_bgcolor="white", paper_bgcolor="white",
                      annotations=[dict(text=msg, showarrow=False, font=dict(size=14, color="#9AA5B4"))])
    return fig


FONT = dict(family="Outfit, sans-serif", size=12, color="#2D3748")


@callback(
    Output("graph-histo-resp","figure"),
    Output("graph-moy-resp","figure"),
    Output("graph-rate-resp","figure"),
    Input("analyse-interval","n_intervals"),
)
def update(_):
    db = SessionLocal()
    try:
        grades  = db.query(Grade).all()
        courses = db.query(Course).all()

        # Histogramme
        notes = [g.note for g in grades]
        if notes:
            fig_h = go.Figure(go.Histogram(x=notes, nbinsx=10, marker_color="#2C4A6E",
                                           xbins=dict(start=0, end=20, size=2)))
            fig_h.update_layout(
                xaxis_title="Note /20", yaxis_title="Nb étudiants",
                plot_bgcolor="white", paper_bgcolor="white", height=260,
                margin=dict(t=10,b=30,l=10,r=10), font=FONT,
                xaxis=dict(gridcolor="#EEF1F5"), yaxis=dict(gridcolor="#EEF1F5"),
                shapes=[dict(type="line",x0=10,x1=10,y0=0,y1=1,yref="paper",
                             line=dict(color="#C8963E",dash="dash",width=1.5))],
            )
        else:
            fig_h = _empty("Aucune note disponible")

        # Moyennes
        avgs = []
        for c in courses:
            ns = [g.note for g in grades if g.course_code == c.code]
            if ns: avgs.append({"label":c.libelle[:20], "val":round(sum(ns)/len(ns),2)})
        if avgs:
            fig_m = go.Figure(go.Bar(
                x=[d["label"] for d in avgs], y=[d["val"] for d in avgs],
                marker_color=["#1B7A4A" if d["val"]>=10 else "#C0392B" for d in avgs],
                text=[str(d["val"]) for d in avgs], textposition="outside",
            ))
            fig_m.update_layout(
                yaxis=dict(range=[0,22], title="Moyenne /20", gridcolor="#EEF1F5"),
                plot_bgcolor="white", paper_bgcolor="white", height=260,
                margin=dict(t=10,b=30,l=10,r=10), font=FONT,
                shapes=[dict(type="line",y0=10,y1=10,x0=-0.5,x1=len(avgs)-0.5,
                             line=dict(color="#C8963E",dash="dash",width=1.5))],
            )
        else:
            fig_m = _empty("Aucune donnée")

        # Taux réussite
        data_r = []
        for c in courses:
            ns = [g.note for g in grades if g.course_code == c.code]
            if ns: data_r.append({"label":c.libelle[:20],"ok":sum(1 for n in ns if n>=10),"ko":sum(1 for n in ns if n<10)})
        if data_r:
            fig_r = go.Figure()
            fig_r.add_trace(go.Bar(name="Admis ≥ 10",   x=[d["label"] for d in data_r], y=[d["ok"] for d in data_r], marker_color="#1B7A4A"))
            fig_r.add_trace(go.Bar(name="Refusés < 10", x=[d["label"] for d in data_r], y=[d["ko"] for d in data_r], marker_color="#C0392B"))
            fig_r.update_layout(barmode="group", yaxis_title="Nombre d'étudiants",
                                 plot_bgcolor="white", paper_bgcolor="white", height=280,
                                 margin=dict(t=10,b=30,l=10,r=10), font=FONT,
                                 yaxis=dict(gridcolor="#EEF1F5"),
                                 legend=dict(orientation="h",yanchor="bottom",y=1.02))
        else:
            fig_r = _empty("Aucune donnée")

        return fig_h, fig_m, fig_r
    finally:
        db.close()
