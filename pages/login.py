import dash
from dash import html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
from database import get_user

dash.register_page(__name__, path="/login", title="Connexion — SGA · ENSAE")

DEMO_ACCOUNTS = [
    ("Admin",       "admin",        "admin123"),
    ("Responsable", "responsable1", "resp123"),
    ("Étudiant 1",  "etudiant1",    "etud123"),
]


def layout():
    return html.Div([
        html.Div(className="login-bg"),
        html.Div(className="login-dots"),

        html.Div([
            html.Div([
                html.Img(src="/assets/img/logo_ensae.png",
                         style={"height":"52px","width":"auto"}),
            ],className="login-logo"),

            html.Div("ENSAE Dakar · SGA",className="login-school"),
            html.H2("Connexion",className="login-title"),
            html.P("Identifiez-vous pour accéder à votre espace.",className="login-sub"),

            # Sélecteur de profil (indicatif)
            html.Div([
                html.Button("Administration",id="tab-admin",  className="role-tab active", n_clicks=0),
                html.Button("Responsable",   id="tab-resp",   className="role-tab",        n_clicks=0),
                html.Button("Étudiant",      id="tab-etud",   className="role-tab",        n_clicks=0),
            ],className="role-tabs"),

            html.Div(id="login-error"),

            html.Div([
                html.Label("Identifiant", className="login-label"),
                dcc.Input(id="login-username", type="text",  placeholder="ex: admin",
                          className="login-input", debounce=False,
                          style={"marginBottom":"16px"}),
            ]),
            html.Div([
                html.Label("Mot de passe", className="login-label"),
                dcc.Input(id="login-password", type="password", placeholder="••••••••",
                          className="login-input"),
            ], style={"marginBottom":"20px"}),

            html.Button("Se connecter",id="btn-login",className="btn-login-submit",n_clicks=0),

            # Comptes de démo
            html.Div([
                html.Div("Comptes de démonstration :", style={
                    "fontSize":"11px","fontWeight":"700","color":"rgba(255,255,255,0.30)",
                    "textTransform":"uppercase","letterSpacing":"0.09em","marginBottom":"10px","marginTop":"20px"
                }),
                *[html.Div([
                    html.Span(f"{nom} — ",style={"color":"rgba(255,255,255,0.40)","fontSize":"12px"}),
                    html.Code(f"{u} / {p}",style={
                        "fontSize":"11.5px","color":"var(--mint)",
                        "background":"rgba(15,252,190,0.08)","padding":"2px 7px","borderRadius":"5px"
                    }),
                ],style={"marginBottom":"5px"}) for nom,u,p in DEMO_ACCOUNTS]
            ]),

            html.A("← Retour à l'accueil",href="/",className="login-back"),
            dcc.Location(id="login-redirect", refresh=True),
        ],className="login-card"),
    ],className="login-page")


@callback(
    Output("login-username", "value"),
    Output("login-password", "value"),
    Output("tab-admin",      "className"),
    Output("tab-resp",       "className"),
    Output("tab-etud",       "className"),
    Input("tab-admin", "n_clicks"),
    Input("tab-resp",  "n_clicks"),
    Input("tab-etud",  "n_clicks"),
    prevent_initial_call=True,
)
def switch_tab(n_admin, n_resp, n_etud):
    tid = ctx.triggered_id
    active, normal = "role-tab active", "role-tab"
    if tid == "tab-admin":
        return "admin",        "admin123", active, normal, normal
    elif tid == "tab-resp":
        return "responsable1", "resp123",  normal, active, normal
    else:
        return "etudiant1",    "etud123",  normal, normal, active


@callback(
    Output("login-error",    "children"),
    Output("login-redirect", "href"),
    Output("session-store",  "data"),
    Input("btn-login","n_clicks"),
    State("login-username","value"),
    State("login-password","value"),
    State("session-store","data"),
    prevent_initial_call=True,
)
def do_login(n, username, password, session):
    if not n:
        return "", dash.no_update, dash.no_update
    if not username or not password:
        return html.Div("Veuillez remplir tous les champs.",className="login-error"), dash.no_update, dash.no_update

    user = get_user(username.strip(), password.strip())
    if not user:
        return html.Div("Identifiants incorrects. Vérifiez votre nom d'utilisateur et mot de passe.",className="login-error"), dash.no_update, dash.no_update

    role = user["role"]
    new_session = {**user}

    if role == "admin":
        redirect = "/admin/dashboard"
    elif role == "responsable":
        redirect = "/responsable/dashboard"
    else:
        redirect = "/etudiant/dashboard"

    return "", redirect, new_session
