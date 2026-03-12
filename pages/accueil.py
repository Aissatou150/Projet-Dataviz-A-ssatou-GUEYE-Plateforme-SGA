import dash
from dash import html
import dash_bootstrap_components as dbc
from database import SessionLocal
from models import Student, Course, Session as CS, Grade
import os

dash.register_page(__name__, path="/", title="Accueil — ENSAE Dakar")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG  = "/assets/img/"
VID  = "/assets/video/"

SLIDES = [
    ("/assets/img/diplome.jpg",     "Remise de diplômes"),
    ("/assets/img/diner.png",       "Diner de gala · Remise des awards"),
    ("/assets/img/culture.png",     "Diversité culturelle"),
    ("/assets/img/sport.jpg",       "Activités sportives"),
    ("/assets/img/integration.png", "Semaine d'intégration"),
    ("/assets/img/vie_ass1.jpg",    "Vie associative"),
    ("/assets/img/vie_ass2.jpg",    "Vie associative"),
    ("/assets/img/vie_ass3.jpg",    "Événements étudiants"),
    ("/assets/img/diversite.png",   "Diversité & inclusion"),
    ("/assets/img/integration_2.png","Intégration promo"),
]


def layout():
    print("[DEBUG] accueil.layout called")
    try:
        db = SessionLocal()
        try:
            nb_s = db.query(Student).count()
            nb_c = db.query(Course).count()
            nb_e = db.query(CS).count()
            nb_n = db.query(Grade).count()
            print(f"[DEBUG] accueil.layout counts: nb_s={nb_s}, nb_c={nb_c}, nb_e={nb_e}, nb_n={nb_n}")
        finally:
            db.close()
    except Exception as e:
        import traceback
        print("[ERROR] Exception in accueil.layout:", e)
        traceback.print_exc()
        return html.Div(f"Erreur dans accueil.layout: {e}")

    # Dupliquer les slides pour l'effet infini
    all_slides = SLIDES * 2
    slide_items = [
        html.Div([
            html.Img(src=src, alt=cap),
            html.Div(cap, className="slide-caption"),
        ], className="slide-item")
        for src, cap in all_slides
    ]

    # Vérifier si la vidéo directeur existe
    vid_directeur = os.path.join(BASE, "assets", "video", "directeur.mp4")
    has_video = os.path.exists(vid_directeur)

    video_block = html.Div([
        html.Div([
            html.Video(
                src=f"{VID}directeur.mp4",
                controls=True, preload="metadata",
                style={"width":"100%","height":"100%","objectFit":"cover"},
            ) if has_video else html.Div([
                html.Div("▶", style={
                    "width":"72px","height":"72px","borderRadius":"50%",
                    "background":"var(--mint)","display":"flex","alignItems":"center",
                    "justifyContent":"center","fontSize":"28px","color":"var(--dark)",
                    "boxShadow":"var(--shadow-mint)","marginBottom":"20px"
                }),
                html.Div([
                    html.Div("Message du Directeur",
                             style={"fontFamily":"'Syne',sans-serif","fontSize":"18px","fontWeight":"700","color":"var(--white)","marginBottom":"6px"}),
                    html.Div("Déposez le fichier directeur.mp4 dans assets/video/",
                             style={"fontSize":"13px","color":"rgba(255,255,255,0.40)"}),
                ]),
            ], className="video-placeholder"),
        ], className="video-wrap"),
    ], className="video-wrap")

    formations = [
        ("ISE","Ingénieurs Statisticiens Économistes","Formation d'élite de 4 ans. Économétrie, statistique mathématique, data science. Recrutés par la Banque Mondiale, le FMI et les INS.","var(--blue)"),
        ("ITS","Ingénieurs des Travaux Statistiques","3 ans de formation aux méthodes de collecte, traitement et diffusion de l'information statistique nationale.","var(--mint-dark)"),
        ("TSS","Techniciens Supérieurs de la Statistique","2 ans post-bac axés sur les enquêtes de terrain, la démographie et l'analyse descriptive.","var(--purple)"),
        ("ATS","Analystes Statisticiens","Formation professionnalisante de 1 an aux outils de production et contrôle qualité des données.","var(--green)"),
    ]

    reseau = [
        ("ANSD","Agence Nationale de la Statistique et de la Démographie — débouché principal des diplômés.","var(--blue)"),
        ("CAPESA","Conférence Africaine des Programmes d'Enseignement Supérieur en Statistique.","var(--mint-dark)"),
        ("ENSEA","École Nationale Supérieure de Statistique d'Abidjan — réseau FASEG.","var(--purple)"),
        ("ISSEA","Institut Sous-régional de Statistique et d'Économie Appliquée — Yaoundé.","var(--green)"),
        ("BM / FMI","Organisations internationales accueillant régulièrement les ISE.","var(--red,#EF4444)"),
    ]

    admission_steps = [
        ("01","Concours national","Concours annuel organisé par l'ENSAE. Ouvert aux bacheliers série C/D et aux étudiants de CPGE ou L2 Maths.","var(--blue)"),
        ("02","Dossier de candidature","Constituer un dossier complet : relevés de notes, lettre de motivation et pièces d'identité.","var(--mint-dark)"),
        ("03","Présélection","Pour certains cycles, une présélection sur dossier précède les épreuves écrites et orales.","var(--purple)"),
        ("04","Intégration","Les candidats retenus suivent une semaine d'intégration avant le démarrage officiel des cours.","var(--green)"),
    ]

    return html.Div([

        # ── HERO avec photo de fond
        html.Div([
            html.Div(className="hero-bg-overlay"),
            html.Div(style={
                "position":"absolute","inset":"0",
                "backgroundImage":"url(/assets/img/hero_bg.png)",
                "backgroundSize":"cover","backgroundPosition":"center",
                "filter":"brightness(0.28)","zIndex":"0",
            }),
            html.Div(className="hero-dots-dark"),
            html.Div(className="hero-deco-circle"),

            html.Div([
                html.Div([html.Span(className="tag-dot"),"ENSAE Dakar · École d'Excellence"],className="hero-tag"),
                html.H1([
                    "Former les ",html.Span("statisticiens",className="hl-mint"),html.Br(),
                    "de ",html.Span("l'Afrique de demain",className="hl-blue"),".",
                ],className="hero-h1"),
                html.P([
                    "L'",html.Strong("École Nationale de la Statistique et de l'Analyse Économique"),
                    " de Dakar forme depuis plus de 40 ans les cadres statisticiens du Sénégal et de toute l'Afrique subsaharienne.",
                ],className="hero-p"),
                html.Div([
                    html.A(["Découvrir l'ENSAE",html.Span(" →",className="cta-arrow")],href="/decouverte",className="btn-cta-mint"),
                    html.A("Accès plateforme",href="/login",className="btn-cta-outline"),
                ],className="hero-cta-row"),
            ],className="hero-content"),

            html.Div([
                html.Div("Promotion des AS en cours",className="hsc-title"),
                html.Div(str(nb_s) if nb_s else "150+",className="hsc-main"),
                html.Div("Étudiants inscrits · 2025–2026",className="hsc-sub"),
                html.Div(className="hsc-divider"),
                html.Div([
                    html.Div([html.Div(str(nb_c) if nb_c else "12",className="hsc-num"),html.Div("Cours",className="hsc-lbl")]),
                    html.Div([html.Div(str(nb_e) if nb_e else "60+",className="hsc-num"),html.Div("Séances",className="hsc-lbl")]),
                    html.Div([html.Div(str(nb_n) if nb_n else "—",className="hsc-num"),html.Div("Notes",className="hsc-lbl")]),
                ],className="hsc-grid"),
            ],className="hero-stats-card"),
        ],className="hero-section"),

        # ── STATS BAR
        html.Div([
            html.Div([html.Div("40+",className="pub-stat-num"),html.Div("Années d'existence",className="pub-stat-lbl")],className="pub-stat-item"),
            html.Div([html.Div("3000+",className="pub-stat-num"),html.Div("Diplômés en Afrique",className="pub-stat-lbl")],className="pub-stat-item"),
            html.Div([html.Div("15+",className="pub-stat-num"),html.Div("Pays représentés",className="pub-stat-lbl")],className="pub-stat-item"),
            html.Div([html.Div("95%",className="pub-stat-num"),html.Div("Taux d'insertion",className="pub-stat-lbl")],className="pub-stat-item"),
        ],className="pub-stats-bar"),

        # ── CARROUSEL
        html.Div([
            html.Div(slide_items, className="slider-track"),
        ], className="slider-section slider-track-wrap"),

        # ── VIDÉO DIRECTEUR
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([html.Div(className="pub-eyebrow-bar"),"Message de la direction"],className="pub-eyebrow mint-eye"),
                    html.H2("Le mot du Directeur",className="pub-h2 white"),
                    html.P("L'ENSAE Dakar s'engage chaque année à former une nouvelle génération de statisticiens de haut niveau, prêts à relever les défis de l'Afrique de demain. Notre mission : allier rigueur académique, ancrage institutionnel et ouverture internationale.",
                           className="pub-sub white",style={"marginBottom":"28px"}),
                    html.Div([
                        html.Div([
                            html.Div("M. Idrissa DIAGNE",style={"fontFamily":"'Syne',sans-serif","fontSize":"16px","fontWeight":"700","color":"var(--white)"}),
                            html.Div("Directeur · ENSAE Dakar",style={"fontSize":"12px","color":"rgba(15,252,190,0.65)","marginTop":"3px"}),
                        ]),
                    ], style={"display":"flex","alignItems":"center","gap":"16px","padding":"16px 20px","background":"rgba(255,255,255,0.06)","borderRadius":"var(--r)","border":"1px solid rgba(15,252,190,0.15)"}),
                ], md=5, style={"display":"flex","flexDirection":"column","justifyContent":"center"}),
                dbc.Col([video_block], md=7),
            ]),
        ], className="video-section", id="directeur"),

        # ── QUI FORMONS-NOUS
        html.Div([
            html.Div([html.Div(className="pub-eyebrow-bar"),"Nos filières"],className="pub-eyebrow"),
            html.H2("Qui formons-nous ?",className="pub-h2"),
            html.P("L'ENSAE forme plusieurs profils de cadres statisticiens répondant aux besoins des institutions publiques, des organisations internationales et du secteur privé.",className="pub-sub",style={"marginBottom":"40px"}),
            dbc.Row([
                dbc.Col(html.A([
                    html.Div(f[0],className="pub-card-icon",style={"--c":f[3]}),
                    html.Div(f[1],className="pub-card-title"),
                    html.Div(f[2],className="pub-card-desc"),
                ],href="/decouverte#cursus",className="pub-card h-100",style={"--c":f[3]}),
                md=6,lg=3,className="mb-4")
                for f in formations
            ]),
        ],className="pub-section white-bg"),

        # ── RÉSEAU
        html.Div([
            html.Div([html.Div(className="pub-eyebrow-bar"),"Notre réseau"],className="pub-eyebrow mint-eye"),
            html.H2("Un réseau africain solide",className="pub-h2 white",id="reseau"),
            html.P("Nos diplômés exercent dans les meilleures institutions nationales et internationales. L'ENSAE s'inscrit dans un réseau d'excellence qui couvre toute l'Afrique subsaharienne.",className="pub-sub white",style={"marginBottom":"36px"}),
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div(r[0][:3].upper(),className="pub-card-icon",style={"--c":r[2]}),
                    html.Div(r[0],className="pub-card-title"),
                    html.Div(r[1],className="pub-card-desc"),
                ],className="pub-card dark h-100",style={"--c":r[2]}),
                md=6,lg=4,className="mb-4")
                for r in reseau
            ]),
        ],className="pub-section dark-bg"),

        # ── ADMISSION
        html.Div([
            html.Div([html.Div(className="pub-eyebrow-bar"),"Rejoindre l'ENSAE"],className="pub-eyebrow"),
            html.H2("Comment intégrer l'ENSAE ?",className="pub-h2",id="admission"),
            html.P("L'entrée à l'ENSAE se fait principalement par voie de concours national. Chaque étape est conçue pour identifier les meilleurs talents statistiques du continent.",className="pub-sub",style={"marginBottom":"40px"}),
            dbc.Row([
                dbc.Col(html.Div([
                    html.Div(s[0],style={"fontFamily":"'Syne',sans-serif","fontSize":"44px","fontWeight":"800","color":s[3],"opacity":"0.18","lineHeight":"1","marginBottom":"12px"}),
                    html.Div(s[1],className="pub-card-title"),
                    html.Div(s[2],className="pub-card-desc"),
                ],className="pub-card h-100",style={"--c":s[3]}),
                md=6,lg=3,className="mb-4")
                for s in admission_steps
            ]),
            html.Div([
                html.A(["Accéder à la plateforme SGA",html.Span(" →",className="cta-arrow")],href="/login",className="btn-cta-mint",style={"marginTop":"16px"}),
            ]),
        ],className="pub-section off-bg"),

        # ── FOOTER
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Img(src="/assets/img/logo_ensae.png",style={"height":"38px","width":"auto"}),
                        html.Div("ENSAE Dakar",className="pub-footer-brand",style={"color":"var(--mint)"}),
                    ],className="pub-footer-logo"),
                    html.P("École Nationale de la Statistique et de l'Analyse Économique de Dakar — former l'excellence statistique africaine depuis 1981.",className="pub-footer-desc"),
                ],md=4),
                dbc.Col([
                    html.Div("Navigation",className="pub-footer-title"),
                    html.A("Accueil",href="/",className="pub-footer-link"),
                    html.A("Découverte",href="/decouverte",className="pub-footer-link"),
                    html.A("Plateforme SGA",href="/login",className="pub-footer-link"),
                ],md=3),
                dbc.Col([
                    html.Div("Liens officiels",className="pub-footer-title"),
                    html.A("Site ENSAE",href="https://www.ensae.sn",target="_blank",className="pub-footer-link"),
                    html.A("ANSD Sénégal",href="https://www.ansd.sn",target="_blank",className="pub-footer-link"),
                    html.A("CAPESA",href="http://www.capesa-stat.org",target="_blank",className="pub-footer-link"),
                ],md=3),
                dbc.Col([
                    html.Div("Contact",className="pub-footer-title"),
                    html.Div("Rue Diourbel · Dakar, Sénégal",className="pub-footer-desc"),
                    html.Div("ensae@ensae.sn",className="pub-footer-desc",style={"marginTop":"6px","color":"var(--mint)"}),
                ],md=2),
            ]),
            html.Div([
                html.Span("© 2025 ENSAE Dakar · Système de Gestion Académique",className="pub-footer-copy"),
                html.Span("SGA v3 · Projet Data Visualisation · AS3",className="pub-footer-copy"),
            ],className="pub-footer-bottom"),
        ],className="pub-footer"),
    ])
