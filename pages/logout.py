import dash
from dash import html, dcc, callback, Output, Input

dash.register_page(__name__, path="/logout", title="Déconnexion — SGA")


def layout():
    return html.Div([
        dcc.Location(id="logout-redirect", refresh=True),
        html.Div([
            html.Div("Déconnexion en cours…", style={
                "textAlign": "center", "color": "var(--grey-400)",
                "fontSize": "15px", "marginTop": "40px",
            }),
        ]),
    ])


@callback(
    Output("logout-redirect", "href"),
    Input("logout-redirect",  "pathname"),
)
def do_logout(pathname):
    return "/login"
