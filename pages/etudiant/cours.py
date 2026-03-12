import dash
from dash import html
import dash_bootstrap_components as dbc
import os

dash.register_page(__name__, path="/etudiant/cours", title="Mes cours — SGA")

COURS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets", "cours"
)

EXTENSIONS = {
    ".pdf":  ("PDF",  "#EF4444"),
    ".ppt":  ("PPT",  "#D97706"),
    ".pptx": ("PPTX", "#D97706"),
    ".doc":  ("DOC",  "#2563EB"),
    ".docx": ("DOCX", "#2563EB"),
    ".xlsx": ("XLSX", "#059669"),
    ".xls":  ("XLS",  "#059669"),
}


def list_files():
    if not os.path.exists(COURS_DIR):
        return []
    files = []
    for fname in sorted(os.listdir(COURS_DIR)):
        ext = os.path.splitext(fname)[1].lower()
        if ext in EXTENSIONS:
            files.append(fname)
    return files


def file_card(fname):
    ext  = os.path.splitext(fname)[1].lower()
    label, color = EXTENSIONS.get(ext, (ext.upper(), "#6B8FAF"))
    name = os.path.splitext(fname)[0]
    url  = f"/assets/cours/{fname}"
    icon = "📊" if ext in (".ppt",".pptx") else "📄" if ext == ".pdf" else "📎"
    return dbc.Col(
        html.A(
            html.Div([
                html.Div([
                    html.Span(icon, style={"fontSize":"24px"}),
                    html.Span(label, style={
                        "fontSize":"10px","fontWeight":"700",
                        "background":color,"color":"white",
                        "padding":"2px 8px","borderRadius":"20px",
                        "marginLeft":"8px",
                    }),
                ], style={"display":"flex","alignItems":"center","marginBottom":"10px"}),
                html.Div(name, style={
                    "fontSize":"13.5px","fontWeight":"600",
                    "color":"var(--text)","lineHeight":"1.4",
                }),
                html.Div("Cliquer pour ouvrir", style={
                    "fontSize":"11.5px","color":"var(--grey-400)","marginTop":"6px",
                }),
            ], className="card card-accent-blue", style={
                "borderTop":f"3px solid {color}","padding":"20px",
                "height":"100%","cursor":"pointer",
            }),
            href=url, target="_blank",
            style={"display":"block","height":"100%"},
        ),
        md=6, lg=4, className="mb-4"
    )


def layout():
    files = list_files()

    content = dbc.Row([file_card(f) for f in files]) if files else html.Div([
        html.Div("Aucun support disponible pour le moment.",
                 style={"fontWeight":"600","marginBottom":"6px"}),
        html.Div("Les supports seront déposés par vos enseignants.",
                 style={"fontSize":"13px","color":"var(--grey-400)"}),
    ], style={
        "textAlign":"center","padding":"56px 32px",
        "background":"var(--white)","borderRadius":"var(--r-lg)",
        "border":"1px solid var(--grey-200)",
    })

    return html.Div([
        html.Div([
            html.Div([
                html.H2("Mes cours"),
                html.Div(
                    f"{len(files)} support(s) disponible(s)" if files else "Aucun support disponible",
                    className="page-sub"
                ),
            ]),
        ], className="page-header"),
        html.Div(content, className="page-body"),
    ])
