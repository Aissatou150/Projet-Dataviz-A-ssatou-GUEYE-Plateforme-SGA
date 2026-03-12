import dash
from dash import html
import dash_bootstrap_components as dbc
import os

dash.register_page(__name__, path="/decouverte", title="Découverte — ENSAE Dakar")

VID = "/assets/video/"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def layout():
    vid_path = os.path.join(BASE, "assets", "video", "ensae.mp4")
    has_video = os.path.exists(vid_path)

    cycles = [
        ("ISE","Ingénieurs Statisticiens Économistes","var(--blue)","Cycle long de 4 ans post-CPGE ou L2 Maths/Éco. Formation d'élite combinant statistique mathématique, économétrie, informatique statistique et économie. Débouchés : Banque Mondiale, FMI, INS, grandes entreprises privées."),
        ("ITS","Ingénieurs des Travaux Statistiques","var(--mint-dark)","Cycle de 3 ans formant des techniciens supérieurs maîtrisant la collecte, le traitement et la diffusion des statistiques nationales. Débouchés principaux : ANSD, INS et directions statistiques ministérielles."),
        ("TSS","Techniciens Supérieurs de la Statistique","var(--purple)","Cycle de 2 ans post-baccalauréat. Formation axée sur les outils de la statistique descriptive, les enquêtes de terrain et la démographie. Profil opérationnel très demandé dans la fonction publique."),
        ("ATS","Analystes Statisticiens","var(--green)","Formation professionnalisante d'1 an. Maîtrise des questionnaires, de la saisie et du contrôle qualité des données. Déploiement rapide sur les enquêtes nationales de grande envergure."),
    ]

    asso = [
        ("/assets/img/sport.jpg",        "CFED",        "Football, basketball, athlétisme — COFEBE , Coupe du directeur .","var(--blue)"),
        ("/assets/img/culture.png",      "Diversité culturelle","Événements multiculturels célébrant la richesse des 15+ nationalités présentes sur le campus.","var(--mint-dark)"),
        ("/assets/img/diner.png",        "Diner de Gala",       "Soirée de gala annuelle — remise des awards étudiants, célébration de la promo sortante.","var(--purple)"),
        ("/assets/img/integration.png",  "Intégration",         "Semaine d'intégration des nouvelles promotions organisée par les étudiants.","var(--green)"),
        ("/assets/img/vie_ass1.jpg",     "Vie Associative",     "Clubs et associations animant le campus toute l'année académique.","var(--amber)"),
        ("/assets/img/vie_ass4.png",     "Événements",          "Conférences, hackathons et séminaires organisés par les étudiants.","var(--red,#EF4444)"),
    ]

    return html.Div([

        # ── HERO
        html.Div([
            html.Div(className="hero-bg-overlay"),
            html.Div(style={
                "position":"absolute","inset":"0",
                "backgroundImage":"url(/assets/img/diplome.jpg)",
                "backgroundSize":"cover","backgroundPosition":"center top",
                "filter":"brightness(0.22)","zIndex":"0",
            }),
            html.Div(className="hero-dots-dark"),
            html.Div([
                html.Div([html.Span(className="tag-dot"),"À la découverte de l'ENSAE"],className="hero-tag"),
                html.H1([
                    "40 ans d'",html.Span("excellence",className="hl-mint"),html.Br(),
                    "statistique en ",html.Span("Afrique",className="hl-blue"),".",
                ],className="hero-h1",style={"fontSize":"46px"}),
                html.P("Fondée en 1981, l'ENSAE Dakar est l'institution de référence pour la formation statistique en Afrique francophone subsaharienne. Une école publique d'excellence, ouverte sur le monde.",className="hero-p"),
                html.Div([
                    html.A(["Voir le cursus",html.Span(" →",className="cta-arrow")],href="#cursus",className="btn-cta-mint"),
                    html.A("Vie associative",href="#asso",className="btn-cta-outline"),
                ],className="hero-cta-row"),
            ],className="hero-content"),
        ],className="hero-section",style={"minHeight":"420px"}),

        # ── EN BREF
        html.Div([
            html.Div([html.Div(className="pub-eyebrow-bar"),"L'institution"],className="pub-eyebrow"),
            html.H2("L'ENSAE en bref",className="pub-h2"),
            dbc.Row([
                dbc.Col([
                    html.P([
                        "L'",html.Strong("École Nationale de la Statistique et de l'Analyse Économique"),
                        " (ENSAE) de Dakar est un ",html.Strong("établissement public d'enseignement supérieur"),
                        " placé sous la tutelle du Ministère de l'Économie et des Finances du Sénégal.",
                    ],style={"fontSize":"15px","fontWeight":"300","color":"var(--text-light)","lineHeight":"1.75","marginBottom":"16px"}),
                    html.P("Membre de la CAPESA, l'ENSAE délivre des diplômes reconnus dans toute la sous-région et accueille chaque année des étudiants venus de plus de 15 pays africains. Ses diplômés occupent des postes de cadres statisticiens dans les institutions nationales, les organisations internationales et le secteur privé.",
                           style={"fontSize":"15px","fontWeight":"300","color":"var(--text-light)","lineHeight":"1.75"}),
                ],md=7),
                dbc.Col([
                    dbc.Row([
                        dbc.Col(html.Div([
                            html.Div(v,style={"fontFamily":"'Syne',sans-serif","fontSize":"34px","fontWeight":"800","color":"var(--blue)","lineHeight":"1"}),
                            html.Div(l,style={"fontSize":"12px","fontWeight":"600","textTransform":"uppercase","letterSpacing":"0.09em","color":"var(--grey-400)","marginTop":"4px"}),
                        ],style={"background":"var(--white)","border":"1px solid var(--grey-200)","borderRadius":"16px","padding":"20px","textAlign":"center"}),
                        width=6,className="mb-3")
                        for v,l in [("1981","Création"),("15+","Pays"),("3000+","Diplômés"),("95%","Insertion")]
                    ]),
                ],md=5),
            ]),
        ],className="pub-section white-bg"),

        # ── CURSUS
        html.Div([
            html.Div([html.Div(className="pub-eyebrow-bar"),"Formation"],className="pub-eyebrow",id="cursus"),
            html.H2("Cursus & cycles de formation",className="pub-h2"),
            html.P("L'ENSAE propose quatre cycles couvrant différents niveaux de qualification, du technicien de terrain à l'ingénieur statisticien de haut niveau.",className="pub-sub",style={"marginBottom":"40px"}),
            html.Div([
                html.Div([
                    html.Div(className="cycle-dot"),
                    html.Div(c[0],className="cycle-badge"),
                    html.Div([
                        html.Div(c[1],className="cycle-title"),
                        html.Div(c[3],className="cycle-desc"),
                    ]),
                ],className="cycle-item")
                for c in cycles
            ],className="cycle-timeline",style={"maxWidth":"780px"}),
        ],className="pub-section off-bg"),

        # ── VIE ASSOCIATIVE avec photos
        html.Div([
            html.Div([html.Div(className="pub-eyebrow-bar"),"Vie étudiante"],className="pub-eyebrow mint-eye",id="asso"),
            html.H2("Vie associative",className="pub-h2 white"),
            html.P("Au-delà des cours, l'ENSAE cultive une vie étudiante riche et dynamique. Sport, culture, entrepreneuriat et réseau alumni — tout est là pour un épanouissement complet.",className="pub-sub white",style={"marginBottom":"36px"}),
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div(style={
                        "width":"100%","height":"180px","borderRadius":"12px 12px 0 0",
                        "overflow":"hidden",
                    },children=[
                        html.Img(src=a[0],alt=a[1],
                                 style={"width":"100%","height":"100%","objectFit":"cover","display":"block",
                                        "transition":"transform 0.5s ease"}),
                    ]),
                    html.Div([
                        html.Div(a[1],className="pub-card-title"),
                        html.Div(a[2],className="pub-card-desc"),
                    ],style={"padding":"20px"}),
                ],className="pub-card dark h-100",style={"--c":a[3],"padding":"0","overflow":"hidden"}),
                md=6,lg=4,className="mb-4")
                for a in asso
            ]),
        ],className="pub-section dark-bg"),

        # ── VIDÉO ENSAE
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([html.Div(className="pub-eyebrow-bar"),"Visite virtuelle"],className="pub-eyebrow mint-eye"),
                    html.H2("Découvrez l'ENSAE en vidéo",className="pub-h2 white"),
                    html.P("Parcourez les installations, les laboratoires et l'ambiance du campus de l'ENSAE Dakar à travers cette présentation filmée.",className="pub-sub white",style={"marginBottom":"28px"}),
                    html.Div([
                        html.A(["Voir le site officiel",html.Span(" →",className="cta-arrow")],
                               href="https://www.ensae.sn",target="_blank",className="btn-cta-mint"),
                    ]),
                ],md=4,style={"display":"flex","flexDirection":"column","justifyContent":"center"}),
                dbc.Col([
                    html.Div([
                        html.Video(
                            src=f"{VID}ensae.mp4",
                            controls=True, preload="metadata",
                            style={"width":"100%","height":"100%","objectFit":"cover"},
                        ) if has_video else html.Div([
                            html.Div("▶",style={
                                "width":"72px","height":"72px","borderRadius":"50%",
                                "background":"var(--mint)","display":"flex","alignItems":"center",
                                "justifyContent":"center","fontSize":"28px","color":"var(--dark)",
                                "boxShadow":"var(--shadow-mint)","marginBottom":"20px"
                            }),
                            html.Div([
                                html.Div("Présentation de l'ENSAE",style={"fontFamily":"'Syne',sans-serif","fontSize":"18px","fontWeight":"700","color":"var(--white)","marginBottom":"6px"}),
                                html.Div("Déposez ensae.mp4 dans assets/video/",style={"fontSize":"13px","color":"rgba(255,255,255,0.40)"}),
                            ]),
                        ],className="video-placeholder"),
                    ],className="video-wrap"),
                ],md=8),
            ]),
        ],className="video-section",id="video-ensae"),

        # ── LIENS OFFICIELS
        html.Div([
            html.Div([html.Div(className="pub-eyebrow-bar"),"Écosystème"],className="pub-eyebrow",id="reseau"),
            html.H2("Liens officiels & partenaires",className="pub-h2"),
            html.P("L'ENSAE s'inscrit dans un écosystème institutionnel fort au niveau national et continental.",className="pub-sub",style={"marginBottom":"40px"}),
            dbc.Row([
                dbc.Col(html.A([
                    html.Div(t[:3].upper(),className="pub-card-icon",style={"--c":col}),
                    html.Div(t,className="pub-card-title"),
                    html.Div(d,className="pub-card-desc"),
                    html.Div("Visiter le site →",className="pub-card-link",style={"--c":col}),
                ],href=lien,target="_blank",className="pub-card h-100",style={"--c":col}),
                md=6,lg=4,className="mb-4")
                for t,d,lien,col in [
                    ("Site ENSAE","Site officiel de l'École Nationale de la Statistique et de l'Analyse Économique de Dakar.","https://www.ensae.sn","var(--blue)"),
                    ("ANSD Sénégal","Agence Nationale de la Statistique et de la Démographie — principal employeur des diplômés.","https://www.ansd.sn","var(--mint-dark)"),
                    ("CAPESA","Conférence Africaine des Programmes d'Enseignement Supérieur et de Formation en Statistique.","http://www.capesa-stat.org","var(--purple)"),
                ]
            ]),
        ],className="pub-section white-bg"),

        # ── FOOTER
        html.Div([
            html.Div([
                html.Div([
                    html.Img(src="/assets/img/logo_ensae.png",style={"height":"38px","width":"auto"}),
                    html.Div("ENSAE Dakar",className="pub-footer-brand",style={"color":"var(--mint)"}),
                ],className="pub-footer-logo"),
                html.P("École Nationale de la Statistique et de l'Analyse Économique de Dakar.",className="pub-footer-desc"),
            ]),
            html.Div([
                html.Span("© 2025 ENSAE Dakar · SGA v3",className="pub-footer-copy"),
                html.A("Retour à l'accueil",href="/",className="pub-footer-copy",style={"color":"var(--mint)"}),
            ],className="pub-footer-bottom"),
        ],className="pub-footer"),
    ])
