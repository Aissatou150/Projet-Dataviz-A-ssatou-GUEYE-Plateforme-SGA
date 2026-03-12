import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

from models import init_db
from database import migrate_from_excel, seed_users, seed_demo_data, get_user

os.makedirs("data", exist_ok=True)
os.makedirs("assets/img", exist_ok=True)
os.makedirs("assets/cours", exist_ok=True)

init_db()
migrate_from_excel("./data/db.xlsx")
seed_users()
seed_demo_data()

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=["/assets/bootstrap.min.css"],
    suppress_callback_exceptions=True,
    title="SGA · ENSAE Dakar",
    update_title=None,
)

import pages.accueil
import pages.decouverte
import pages.login
import pages.admin.dashboard
import pages.admin.cours
import pages.admin.seances
import pages.admin.etudiants
import pages.admin.notes
import pages.admin.analyse
import pages.admin.pdf_export
import pages.responsable.dashboard
import pages.responsable.cours
import pages.responsable.seances
import pages.responsable.etudiants
import pages.responsable.notes
import pages.responsable.analyse
import pages.etudiant.dashboard
import pages.etudiant.notes
import pages.etudiant.absences
import pages.etudiant.cours

import pages.profil
import pages.logout


def logo_or_text():
    lp = os.path.join(BASE_DIR,"assets","img","logo_ensae.png")
    if os.path.exists(lp):
        return html.Img(src="/assets/img/logo_ensae.png",style={"height":"40px","width":"auto"})
    return html.Div("ENSAE",style={"fontFamily":"'Inter',sans-serif","fontSize":"20px","fontWeight":"800","color":"var(--mint)"})


def pub_navbar():
    return html.Div([
        html.A([logo_or_text(),html.Div([
            html.Div("ENSAE Dakar",className="brand-title"),
            html.Div("École Nationale de la Statistique",className="brand-sub"),
        ],className="pub-brand-text")],href="/",className="pub-brand"),
        html.Div([
            html.A("Accueil",href="/",className="pub-nav-link"),
            html.A("Découverte",href="/decouverte",className="pub-nav-link"),
        ],className="pub-nav-links"),
        html.A("Plateforme SGA",href="/login",className="btn-login"),
    ],className="pub-navbar")


def app_navbar(role,nom,prenom):
    initiales=f"{(prenom or 'U')[0]}{(nom or '')[0]}".upper()
    if role=="admin":
        links=[
            html.Div([html.Button("Administration",className="app-nav-btn"),html.Div([
                html.A("Tableau de bord",href="/admin/dashboard"),
                html.A("Étudiants",href="/admin/etudiants"),
                html.A("Cours",href="/admin/cours"),
                html.A("Séances",href="/admin/seances"),
                html.A("Notes",href="/admin/notes"),
            ],className="app-nav-dropdown")],className="app-nav-item"),
            html.Div([html.Button("Analyses & PDF",className="app-nav-btn"),html.Div([
                html.A("Analyse de données",href="/admin/analyse"),
                html.A("Export bulletins",href="/admin/pdf-export"),
            ],className="app-nav-dropdown")],className="app-nav-item"),
        ]
        badge=html.Span("Admin",className="role-badge admin")
    elif role=="responsable":
        links=[html.Div([html.Button("Gestion",className="app-nav-btn"),html.Div([
            html.A("Tableau de bord",href="/responsable/dashboard"),
            html.A("Étudiants",href="/responsable/etudiants"),
            html.A("Cours",href="/responsable/cours"),
            html.A("Séances & Appel",href="/responsable/seances"),
            html.A("Notes",href="/responsable/notes"),
            html.A("Analyse",href="/responsable/analyse"),
        ],className="app-nav-dropdown")],className="app-nav-item")]
        badge=html.Span("Responsable",className="role-badge responsable")
    else:
        links=[
            html.A("Tableau de bord",href="/etudiant/dashboard",className="app-nav-btn"),
            html.A("Mes notes",href="/etudiant/notes",className="app-nav-btn"),
            html.A("Mes absences",href="/etudiant/absences",className="app-nav-btn"),
            html.A("Mes cours",href="/etudiant/cours",className="app-nav-btn"),
        ]
        badge=html.Span("Étudiant",className="role-badge etudiant")
    return html.Div([
        html.A([logo_or_text(),html.Div([
            html.Div("SGA · ENSAE",className="app-brand-title"),
            html.Div("Gestion Académique",className="app-brand-sub"),
        ])],href="/",className="app-brand"),
        html.Div(links,className="app-nav-links"),
        html.Div([badge,
            html.Div([html.Div(initiales,className="user-avatar"),html.Span(f"{prenom} {nom}",className="user-label")],className="user-chip"),
            html.A("Déconnexion",href="/logout",className="btn-logout"),
        ],className="app-navbar-right"),
    ],className="app-navbar")


app.layout=html.Div([
    dcc.Location(id="url",refresh=False),
    dcc.Store(id="session-store",storage_type="session"),
    html.Div(id="navbar-container"),
    html.Div(dash.page_container,className="main-content",id="page-content"),
])


@app.callback(
    Output("navbar-container","children"),
    Input("url","pathname"),
    State("session-store","data"),
)
def update_navbar(pathname, session):
    if pathname in ["/", "/decouverte", "/login", "/logout", ""] or pathname is None:
        return pub_navbar()
    if not session or not session.get("role"):
        return pub_navbar()
    return app_navbar(session.get("role",""), session.get("nom",""), session.get("prenom",""))


if __name__=="__main__":
    app.run(debug=True,host="127.0.0.1",port=8050)
