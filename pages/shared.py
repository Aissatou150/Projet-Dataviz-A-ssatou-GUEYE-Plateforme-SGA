"""Composants partagés entre les profils."""
from dash import html, dcc
import dash_bootstrap_components as dbc


def redirect_if_no_session(session, required_role=None):
    """Redirige si pas de session ou mauvais rôle."""
    if not session or not session.get("role"):
        return dcc.Location(href="/login", id="redir-shared-1")
    if required_role and session.get("role") not in (required_role if isinstance(required_role, list) else [required_role]):
        return dcc.Location(href="/login", id="redir-shared-2")
    return None


def page_header(title, subtitle, actions=None):
    return html.Div([
        html.Div([
            html.H2(title),
            html.Div(subtitle, className="page-sub"),
        ]),
        html.Div(actions or []),
    ], className="page-header")


def kpi(val, label, color="var(--blue)"):
    return html.Div([
        html.Div(str(val), className="kpi-val"),
        html.Div(label,    className="kpi-lbl"),
    ], className="kpi-card", style={"--kpi-color": color})
