"""
Script de génération du rapport de documentation PDF pour la plateforme SGA · ENSAE Dakar v3
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import BalancedColumns
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import os
from datetime import datetime

# ─── Palette ENSAE ────────────────────────────────────────────────────────────
BLUE      = HexColor("#106EBE")
MINT      = HexColor("#0FFCBE")
DARK      = HexColor("#0A1628")
WHITE     = colors.white
GRAY_LIGHT= HexColor("#F1F5F9")
GRAY_MID  = HexColor("#94A3B8")
GRAY_DARK = HexColor("#334155")
GREEN     = HexColor("#10B981")
AMBER     = HexColor("#F59E0B")
RED       = HexColor("#EF4444")
PURPLE    = HexColor("#7C3AED")
NAVY      = HexColor("#1E3A5F")

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "documentation_SGA_ENSAE.pdf")

# ─── Numérotation des pages ────────────────────────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        page_num = self._pageNumber
        if page_num == 1:
            return  # Pas de numéro sur la page de garde
        self.saveState()
        # Barre de pied de page
        self.setFillColor(DARK)
        self.rect(0, 0, A4[0], 28, fill=1, stroke=0)
        # Texte gauche
        self.setFillColor(GRAY_MID)
        self.setFont("Helvetica", 7)
        self.drawString(1.5*cm, 10, "SGA · ENSAE Dakar — Documentation Technique v3")
        # Numéro de page
        self.setFillColor(WHITE)
        self.setFont("Helvetica-Bold", 8)
        self.drawRightString(A4[0] - 1.5*cm, 10, f"Page {page_num} / {page_count}")
        # Trait coloré
        self.setStrokeColor(BLUE)
        self.setLineWidth(2)
        self.line(0, 28, A4[0], 28)
        self.restoreState()


# ─── Styles ───────────────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName="Helvetica-Bold",
            fontSize=32,
            textColor=WHITE,
            leading=38,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            fontName="Helvetica",
            fontSize=14,
            textColor=MINT,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta",
            fontName="Helvetica",
            fontSize=10,
            textColor=GRAY_MID,
            leading=14,
            alignment=TA_CENTER,
        ),
        "chapter": ParagraphStyle(
            "chapter",
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=WHITE,
            leading=22,
            spaceBefore=0,
            spaceAfter=10,
            backColor=BLUE,
            borderPad=(8, 14, 8, 14),
            leftIndent=-1.5*cm,
            rightIndent=-1.5*cm,
        ),
        "section": ParagraphStyle(
            "section",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=BLUE,
            leading=16,
            spaceBefore=14,
            spaceAfter=4,
            borderPad=0,
        ),
        "subsection": ParagraphStyle(
            "subsection",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            textColor=NAVY,
            leading=14,
            spaceBefore=8,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=GRAY_DARK,
            leading=14,
            spaceBefore=2,
            spaceAfter=4,
            alignment=TA_JUSTIFY,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=GRAY_DARK,
            leading=13,
            spaceBefore=1,
            spaceAfter=1,
            leftIndent=14,
            bulletIndent=4,
        ),
        "code": ParagraphStyle(
            "code",
            fontName="Courier",
            fontSize=8,
            textColor=HexColor("#1E293B"),
            leading=12,
            leftIndent=10,
            backColor=HexColor("#F8FAFC"),
            borderColor=HexColor("#CBD5E1"),
            borderWidth=0.5,
            borderPad=6,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            textColor=WHITE,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=GRAY_DARK,
        ),
        "caption": ParagraphStyle(
            "caption",
            fontName="Helvetica-Oblique",
            fontSize=8,
            textColor=GRAY_MID,
            alignment=TA_CENTER,
            spaceBefore=2,
            spaceAfter=6,
        ),
        "toc_entry": ParagraphStyle(
            "toc_entry",
            fontName="Helvetica",
            fontSize=10,
            textColor=GRAY_DARK,
            leading=16,
            leftIndent=0,
        ),
        "toc_sub": ParagraphStyle(
            "toc_sub",
            fontName="Helvetica",
            fontSize=9,
            textColor=GRAY_MID,
            leading=14,
            leftIndent=16,
        ),
        "highlight": ParagraphStyle(
            "highlight",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=DARK,
            leading=14,
            backColor=HexColor("#EFF6FF"),
            borderColor=BLUE,
            borderWidth=1,
            borderPad=8,
            spaceBefore=4,
            spaceAfter=6,
        ),
        "badge_blue": ParagraphStyle(
            "badge_blue",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=WHITE,
            backColor=BLUE,
            borderPad=3,
            alignment=TA_CENTER,
        ),
    }
    return styles


# ─── Utilitaires ──────────────────────────────────────────────────────────────
def chapter_block(title, styles):
    """Entête de chapitre avec fond bleu pleine largeur."""
    return [
        Spacer(1, 0.4*cm),
        Paragraph(f"  {title}", styles["chapter"]),
        Spacer(1, 0.3*cm),
    ]

def section_block(title, styles):
    return [
        Paragraph(title, styles["section"]),
        HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=4),
    ]

def subsection_block(title, styles):
    return [Paragraph(f"▸  {title}", styles["subsection"])]

def bullet_item(text, styles, level=0):
    indent = 14 + level * 10
    s = ParagraphStyle(
        "bitem", parent=styles["bullet"],
        leftIndent=indent, bulletIndent=indent - 10,
    )
    return Paragraph(f"• {text}", s)

def info_box(text, styles, color=None):
    if color is None:
        color = BLUE
    s = ParagraphStyle(
        "ib", parent=styles["highlight"],
        backColor=HexColor("#EFF6FF") if color == BLUE else HexColor("#F0FDF4"),
        borderColor=color,
    )
    return Paragraph(text, s)

def make_table(headers, rows, col_widths=None, stripe=True):
    data = [headers] + rows
    if col_widths is None:
        col_widths = [A4[0] / len(headers) - 2*cm / len(headers)] * len(headers)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 8.5),
        ("ALIGN",      (0, 0), (-1, 0), "CENTER"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",   (0, 1), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_LIGHT] if stripe else [WHITE]),
        ("GRID",       (0, 0), (-1, -1), 0.4, HexColor("#CBD5E1")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t

def color_tag(text, bg, fg=WHITE):
    """Petite étiquette colorée inline."""
    return f'<font color="#{bg.hexval()[1:]}" ><b> {text} </b></font>'


# ─── PAGE DE GARDE ────────────────────────────────────────────────────────────
def cover_page(styles):
    story = []

    # Fond sombre simulé par un grand rectangle de couleur (via canvas override)
    # On crée un spacer pour décaler le contenu
    story.append(Spacer(1, 3.5*cm))

    # Logo / sigle
    logo_style = ParagraphStyle(
        "logo_txt", fontName="Helvetica-Bold", fontSize=48,
        textColor=MINT, alignment=TA_CENTER, leading=52,
    )
    story.append(Paragraph("SGA", logo_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="60%", thickness=3, color=MINT, spaceAfter=10,
                             hAlign="CENTER"))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Système de Gestion Académique", styles["cover_title"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("ENSAE Dakar — Version 3", styles["cover_subtitle"]))
    story.append(Spacer(1, 1.2*cm))

    # Encadré description
    desc_style = ParagraphStyle(
        "cov_desc", fontName="Helvetica", fontSize=11,
        textColor=HexColor("#CBD5E1"), alignment=TA_CENTER, leading=16,
    )
    story.append(Paragraph(
        "Documentation technique et fonctionnelle complète<br/>"
        "Plateforme de gestion académique multi-rôles<br/>"
        "avec tableaux de bord interactifs et visualisation de données",
        desc_style
    ))
    story.append(Spacer(1, 2*cm))

    # Métadonnées
    story.append(HRFlowable(width="40%", thickness=1, color=GRAY_MID,
                             hAlign="CENTER", spaceAfter=8))
    story.append(Paragraph(f"Version 3.0  ·  Dakar, {datetime.now().strftime('%B %Y')}",
                            styles["cover_meta"]))
    story.append(Paragraph(
        "École Nationale de la Statistique et de l'Analyse Économique",
        styles["cover_meta"]
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Fait le " + "11.03.2026",
                            styles["cover_meta"]))
    
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Auteurs",
        styles["cover_meta"]
    ))    
    story.append(Paragraph(
        "Aïssatou GUEYE : aissatoug15@gmail.com",
        styles["cover_meta"]
    ))
    story.append(Paragraph(
        "KASSI MAMADOU Maxwell : kmaxmamadou2902@gmail.com",
        styles["cover_meta"]
    ))
    story.append(Paragraph(
        "Analystes Statisticiens en fin de formation ",
        styles["cover_meta"]
    ))
    
    story.append(PageBreak())
    return story


# ─── TABLE DES MATIÈRES ───────────────────────────────────────────────────────
def toc_page(styles):
    story = []
    story += chapter_block("Table des matières", styles)
    story.append(Spacer(1, 0.3*cm))

    chapters = [
        ("1.", "Vue d'ensemble de la plateforme", [
            ("1.1", "Présentation générale"),
            ("1.2", "Objectifs du système"),
            ("1.3", "Environnement technologique"),
        ]),
        ("2.", "Architecture du projet", [
            ("2.1", "Structure des fichiers et dossiers"),
            ("2.2", "Flux de démarrage de l'application"),
            ("2.3", "Gestion des routes et des pages"),
        ]),
        ("3.", "Modèle de données", [
            ("3.1", "Schéma de la base de données"),
            ("3.2", "Description des tables"),
            ("3.3", "Relations entre les entités"),
        ]),
        ("4.", "Fonctionnalités par rôle", [
            ("4.1", "Pages publiques"),
            ("4.2", "Espace Administrateur"),
            ("4.3", "Espace Responsable"),
            ("4.4", "Espace Étudiant"),
        ]),
        ("5.", "Interface utilisateur & Design system", [
            ("5.1", "Palette de couleurs ENSAE"),
            ("5.2", "Typographie et composants"),
            ("5.3", "Navigation et responsive"),
        ]),
        ("6.", "Sécurité et authentification", [
            ("6.1", "Mécanisme d'authentification"),
            ("6.2", "Contrôle d'accès par rôle (RBAC)"),
            ("6.3", "Gestion des sessions"),
        ]),
        ("7.", "Flux de données et cas d'usage", [
            ("7.1", "Import/Export Excel des notes"),
            ("7.2", "Génération de bulletins PDF"),
            ("7.3", "Gestion des présences"),
        ]),
        ("8.", "Comptes de démonstration & déploiement", [
            ("8.1", "Comptes par défaut"),
            ("8.2", "Données de démonstration générées"),
            ("8.3", "Installation et démarrage"),
            ("8.4", "Liens de la plateforme"),
        ]),
    ]

    for num, title, subs in chapters:
        entry = f'<b><font color="#106EBE">{num}</font></b>  {title}'
        story.append(Paragraph(entry, styles["toc_entry"]))
        for snum, stitle in subs:
            story.append(Paragraph(f"{snum}  {stitle}", styles["toc_sub"]))
        story.append(Spacer(1, 3))

    story.append(PageBreak())
    return story


# ─── CHAPITRE 1 : Vue d'ensemble ──────────────────────────────────────────────
def chapter1(styles):
    story = []
    story += chapter_block("1. Vue d'ensemble de la plateforme", styles)

    # 1.1
    story += section_block("1.1 Présentation générale", styles)
    story.append(Paragraph(
        "SGA (Système de Gestion Académique) est une plateforme web moderne conçue pour "
        "l'ENSAE Dakar (École Nationale de la Statistique et de l'Analyse Économique du Sénégal). "
        "Il s'agit de la troisième version du système, réalisée dans le cadre d'un projet de "
        "data visualisation avancée.",
        styles["body"]
    ))
    story.append(Paragraph(
        "La plateforme permet une gestion complète du cursus académique : suivi des étudiants, "
        "gestion des notes, des absences, des cours et des séances pédagogiques, le tout dans une "
        "interface moderne et responsive. Elle s'adresse à trois types d'utilisateurs : "
        "les administrateurs, les responsables de cours et les étudiants.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(info_box(
        "<b>Contexte :</b> Projet académique de data visualisation avancée — AS3 2025/2026, "
        "Semestre 1, ENSAE Dakar. La plateforme est entièrement développée en Python "
        "avec le framework Dash/Plotly.",
        styles
    ))

    # 1.2
    story += section_block("1.2 Objectifs du système", styles)
    objectifs = [
        "Centraliser la gestion académique (étudiants, cours, notes, présences) dans un seul portail.",
        "Fournir des tableaux de bord interactifs avec visualisations de données pour chaque rôle.",
        "Automatiser la saisie des notes via import/export Excel et la génération de bulletins PDF.",
        "Garantir un contrôle d'accès strict selon les rôles (Administrateur, Responsable, Étudiant).",
        "Offrir une expérience utilisateur moderne et responsive aux couleurs de l'ENSAE.",
        "Permettre un déploiement rapide avec des données de démonstration réalistes pré-chargées.",
    ]
    for o in objectifs:
        story.append(bullet_item(o, styles))
    story.append(Spacer(1, 0.3*cm))

    # 1.3
    story += section_block("1.3 Environnement technologique", styles)

    headers = ["Catégorie", "Technologie", "Version", "Rôle"]
    rows = [
        ["Framework web",    "Dash (Plotly)",           "2.14+",  "Interface, routing, callbacks"],
        ["UI Components",    "Dash Bootstrap Components","1.5+",   "Composants Bootstrap responsive"],
        ["Base de données",  "SQLite + SQLAlchemy",     "2.0+",   "Persistance ORM"],
        ["Visualisation",    "Plotly",                  "5.18+",  "Graphiques interactifs"],
        ["Données",          "Pandas",                  "2.0+",   "Manipulation, import/export"],
        ["Export PDF",       "ReportLab",               "4.0+",   "Génération bulletins/docs"],
        ["Excel",            "openpyxl",                "3.1+",   "Lecture/écriture .xlsx"],
        ["Serveur web",      "Flask (via Dash)",        "-",      "Serveur HTTP intégré"],
        ["Langage",          "Python",                  "3.10+",  "Langage principal"],
        ["Style",            "CSS personnalisé",        "-",      "Charte graphique ENSAE"],
    ]
    col_w = [3.5*cm, 4.5*cm, 2*cm, 7*cm]
    story.append(make_table(headers, rows, col_w))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Tableau 1 — Pile technologique de la plateforme SGA", styles["caption"]
    ))

    story.append(PageBreak())
    return story


# ─── CHAPITRE 2 : Architecture ────────────────────────────────────────────────
def chapter2(styles):
    story = []
    story += chapter_block("2. Architecture du projet", styles)

    story += section_block("2.1 Structure des fichiers et dossiers", styles)
    story.append(Paragraph(
        "Le projet adopte une architecture modulaire basée sur le système de pages de Dash "
        "(use_pages=True). Chaque page est un module Python indépendant avec ses propres "
        "callbacks. La séparation est claire entre les couches données, logique métier et présentation.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.2*cm))

    tree = [
        "sga_v3/",
        "├── app.py               # Point d'entrée — config Dash, navbar dynamique",
        "├── models.py            # Modèles SQLAlchemy (7 tables ORM)",
        "├── database.py          # Init DB, migrations, seed, requêtes utilisateurs",
        "├── requirements.txt     # Dépendances Python",
        "├── generate_doc.py      # Script de génération de cette documentation",
        "│",
        "├── assets/",
        "│   ├── style.css        # Design system complet (charte ENSAE)",
        "│   ├── bootstrap.min.css",
        "│   ├── img/             # Images statiques (logo, photos)",
        "│   ├── cours/           # PDFs des cours classés par code matière",
        "│   └── video/           # Vidéos institutionnelles (director.mp4, ensae.mp4)",
        "│",
        "├── data/",
        "│   ├── sga.db           # Base SQLite",
        "│   └── db.xlsx          # Template d'import Excel (optionnel)",
        "│",
        "└── pages/",
        "    ├── accueil.py       # Page d'accueil publique",
        "    ├── decouverte.py    # Page découverte institutionnelle",
        "    ├── login.py         # Authentification",
        "    ├── logout.py        # Déconnexion",
        "    ├── profil.py        # Profil utilisateur",
        "    ├── shared.py        # Composants réutilisables",
        "    ├── admin/           # Pages espace Administrateur (7 modules)",
        "    ├── responsable/     # Pages espace Responsable (6 modules)",
        "    └── etudiant/        # Pages espace Étudiant (4 modules)",
    ]
    tree_style = ParagraphStyle(
        "tree", fontName="Courier", fontSize=7.5, textColor=GRAY_DARK,
        leading=11, backColor=HexColor("#F8FAFC"), borderColor=HexColor("#CBD5E1"),
        borderWidth=0.5, borderPad=8,
    )
    story.append(Paragraph("<br/>".join(t.replace(" ", "&nbsp;").replace("<", "&lt;") for t in tree),
                           tree_style))
    story.append(Spacer(1, 0.3*cm))

    story += section_block("2.2 Flux de démarrage de l'application", styles)
    story.append(Paragraph(
        "Au lancement, app.py exécute une séquence d'initialisation garantissant que la base "
        "de données est prête et que des données de démonstration sont disponibles.",
        styles["body"]
    ))

    steps = [
        ("1", "init_db()", "Création des tables SQLAlchemy si inexistantes (CREATE TABLE IF NOT EXISTS)"),
        ("2", "migrate_from_excel()", "Import optionnel depuis data/db.xlsx si le fichier existe"),
        ("3", "seed_users()", "Création des comptes par défaut (admin, responsable1, etudiant1)"),
        ("4", "seed_demo_data()", "Génération de 40 étudiants fictifs, 8 cours, séances et notes réalistes"),
        ("5", "app.run_server()", "Démarrage du serveur Dash sur localhost:8050"),
    ]
    headers = ["Étape", "Fonction", "Description"]
    rows = [[s, f, d] for s, f, d in steps]
    story.append(make_table(headers, rows, [1.2*cm, 4.5*cm, 11.3*cm]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Tableau 2 — Séquence d'initialisation", styles["caption"]))

    story += section_block("2.3 Gestion des routes et des pages", styles)
    story.append(Paragraph(
        "Dash gère le routing côté client via dcc.Location. Chaque fichier dans pages/ "
        "déclare son URL avec @dash.register_page(). La navbar est rendue dynamiquement "
        "selon le rôle stocké dans le dcc.Store de session.",
        styles["body"]
    ))

    routes = [
        ["/",                    "Public",        "Page d'accueil avec statistiques en temps réel"],
        ["/decouverte",          "Public",        "Programmes, débouchés, contacts institutionnels"],
        ["/login",               "Public",        "Formulaire d'authentification avec sélection de rôle"],
        ["/logout",              "Auth",          "Déconnexion et redirection vers /"],
        ["/profil",              "Auth",          "Gestion du profil utilisateur connecté"],
        ["/admin/dashboard",     "Admin",         "Vue d'ensemble KPIs + graphiques analytiques"],
        ["/admin/etudiants",     "Admin",         "CRUD complet des étudiants"],
        ["/admin/cours",         "Admin",         "Gestion des matières et cours"],
        ["/admin/seances",       "Admin",         "Planification et suivi des séances"],
        ["/admin/notes",         "Admin",         "Saisie, import Excel et consultation des notes"],
        ["/admin/analyse",       "Admin",         "Analyses statistiques avancées"],
        ["/admin/pdf",           "Admin",         "Export bulletins et attestations PDF"],
        ["/responsable/dashboard","Responsable",  "Tableau de bord responsable de cours"],
        ["/responsable/etudiants","Responsable",  "Liste des étudiants du cours"],
        ["/responsable/cours",   "Responsable",   "Gestion du contenu pédagogique"],
        ["/responsable/seances", "Responsable",   "Saisie présences et séances"],
        ["/responsable/notes",   "Responsable",   "Saisie et visualisation des notes"],
        ["/responsable/analyse", "Responsable",   "Analyse des performances"],
        ["/etudiant/dashboard",  "Étudiant",      "Tableau de bord personnel"],
        ["/etudiant/notes",      "Étudiant",      "Consultation des notes par matière"],
        ["/etudiant/absences",   "Étudiant",      "Historique des absences/retards"],
        ["/etudiant/cours",      "Étudiant",      "Accès aux supports de cours (PDF)"],
    ]
    headers = ["Route URL", "Accès", "Description"]
    col_w = [5.5*cm, 2.8*cm, 8.7*cm]
    story.append(make_table(headers, routes, col_w))
    story.append(Paragraph("Tableau 3 — Récapitulatif de toutes les routes", styles["caption"]))

    story.append(PageBreak())
    return story


# ─── CHAPITRE 3 : Modèle de données ──────────────────────────────────────────
def chapter3(styles):
    story = []
    story += chapter_block("3. Modèle de données", styles)

    story += section_block("3.1 Schéma de la base de données", styles)
    story.append(Paragraph(
        "La base de données SQLite comporte 7 tables liées par des clés étrangères. "
        "SQLAlchemy gère les relations avec suppression en cascade (cascade='all, delete'). "
        "Le fichier de base de données est situé à data/sga.db.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.2*cm))

    # Diagramme textuel ASCII des relations
    schema_lines = [
        "  users ──────────────────────────────── students",
        "    │ student_id (FK, nullable)              │",
        "    │                          ┌─────────────┤",
        "    │                          │             │",
        "    │                       grades      attendance",
        "    │                          │             │",
        "    │                     course_code   id_session",
        "    │                          │             │",
        "    └──────────────────── courses ─────── sessions",
        "                              │",
        "                          course_pdfs",
    ]
    schema_style = ParagraphStyle(
        "schema", fontName="Courier", fontSize=8, textColor=NAVY,
        leading=12, backColor=HexColor("#EFF6FF"), borderColor=BLUE,
        borderWidth=1, borderPad=10, alignment=TA_LEFT,
    )
    story.append(Paragraph(
        "<br/>".join(l.replace(" ", "&nbsp;") for l in schema_lines), schema_style
    ))
    story.append(Paragraph("Figure 1 — Diagramme des relations entre tables", styles["caption"]))

    story += section_block("3.2 Description des tables", styles)

    tables_desc = [
        ("users", [
            ("id",         "INTEGER", "PK, auto-incrément"),
            ("username",   "TEXT",    "Identifiant unique de connexion"),
            ("password_h", "TEXT",    "Mot de passe haché SHA-256"),
            ("role",       "TEXT",    "admin | responsable | etudiant"),
            ("nom",        "TEXT",    "Nom de famille"),
            ("prenom",     "TEXT",    "Prénom"),
            ("student_id", "INTEGER", "FK → students.id (nullable)"),
        ]),
        ("students", [
            ("id",     "INTEGER", "PK, auto-incrément"),
            ("nom",    "TEXT",    "Nom de famille"),
            ("prenom", "TEXT",    "Prénom"),
            ("email",  "TEXT",    "Email unique (format prenom.nom@ensae.sn)"),
            ("dob",    "DATE",    "Date de naissance"),
            ("classe", "TEXT",    "Classe : ISE1, ISE2, ITS1, TSS1, ATS1..."),
        ]),
        ("courses", [
            ("code",      "TEXT",    "PK — Code matière (ex. MATH101)"),
            ("libelle",   "TEXT",    "Intitulé du cours"),
            ("volume_h",  "INTEGER", "Volume horaire total"),
            ("enseignant","TEXT",    "Nom de l'enseignant responsable"),
            ("classe",    "TEXT",    "Classe cible"),
        ]),
        ("sessions", [
            ("id",          "INTEGER", "PK, auto-incrément"),
            ("course_code", "TEXT",    "FK → courses.code"),
            ("date",        "DATE",    "Date de la séance"),
            ("duree",       "FLOAT",   "Durée en heures (1.5, 2.0, 3.0...)"),
            ("theme",       "TEXT",    "Thème / chapitre de la séance"),
            ("type_seance", "TEXT",    "Type : cours, TD, TP..."),
        ]),
        ("attendance", [
            ("id_session", "INTEGER", "PK composée + FK → sessions.id"),
            ("id_student", "INTEGER", "PK composée + FK → students.id"),
            ("type_abs",   "TEXT",    "absence | retard"),
        ]),
        ("grades", [
            ("id",          "INTEGER", "PK, auto-incrément"),
            ("id_student",  "INTEGER", "FK → students.id"),
            ("course_code", "TEXT",    "FK → courses.code"),
            ("note",        "FLOAT",   "Note sur 20"),
            ("coefficient", "FLOAT",   "Coefficient (1.0, 1.5, 2.0)"),
            ("type_eval",   "TEXT",    "devoir | examen | partiel"),
        ]),
        ("course_pdfs", [
            ("id",          "INTEGER", "PK, auto-incrément"),
            ("course_code", "TEXT",    "FK → courses.code"),
            ("titre",       "TEXT",    "Titre du document PDF"),
            ("filename",    "TEXT",    "Chemin relatif du fichier"),
        ]),
    ]

    for table_name, fields in tables_desc:
        story += subsection_block(f"Table : {table_name}", styles)
        headers = ["Colonne", "Type", "Description"]
        rows = [[f, t, d] for f, t, d in fields]
        story.append(make_table(headers, rows, [4*cm, 2.5*cm, 10.5*cm]))
        story.append(Spacer(1, 0.15*cm))

    story += section_block("3.3 Relations entre les entités", styles)
    relations = [
        ["users → students",    "ManyToOne", "Un utilisateur étudiant est lié à un enregistrement student"],
        ["students → grades",   "OneToMany", "Un étudiant peut avoir plusieurs notes (cascade delete)"],
        ["students → attendance","OneToMany","Un étudiant peut avoir plusieurs entrées de présence"],
        ["courses → sessions",  "OneToMany", "Un cours comporte plusieurs séances"],
        ["courses → grades",    "OneToMany", "Un cours comporte plusieurs notes"],
        ["courses → course_pdfs","OneToMany","Un cours peut avoir plusieurs documents PDF associés"],
        ["sessions → attendance","OneToMany","Chaque séance génère des entrées de présence"],
    ]
    story.append(make_table(
        ["Relation", "Type", "Description"],
        relations,
        [4.5*cm, 2.5*cm, 10*cm]
    ))
    story.append(Paragraph("Tableau 4 — Relations entre les tables", styles["caption"]))

    story.append(PageBreak())
    return story


# ─── CHAPITRE 4 : Fonctionnalités par rôle ────────────────────────────────────
def chapter4(styles):
    story = []
    story += chapter_block("4. Fonctionnalités par rôle", styles)

    story += section_block("4.1 Pages publiques (sans authentification)", styles)
    story.append(Paragraph(
        "Deux pages sont accessibles sans connexion, offrant une vitrine institutionnelle "
        "complète de l'ENSAE.",
        styles["body"]
    ))

    story += subsection_block("Page d'accueil (/)", styles)
    pub_features = [
        "Section héro avec statistiques en temps réel extraites de la base de données (nb étudiants, cours, séances...)",
        "Carrousel de photos de la vie étudiante à l'ENSAE",
        "Vidéo du message du directeur (director.mp4 intégré)",
        "Présentation des programmes : ISE, ITS, TSS, ATS avec descriptifs",
        "Étapes du processus d'admission",
        "Réseau de partenaires institutionnels",
    ]
    for f in pub_features:
        story.append(bullet_item(f, styles))

    story += subsection_block("Page Découverte (/decouverte)", styles)
    for f in [
        "Informations détaillées sur chaque programme de formation",
        "Débouchés professionnels et secteurs d'emploi",
        "Réseau des anciens élèves (Alumni)",
        "Informations de contact de l'institution",
    ]:
        story.append(bullet_item(f, styles))

    story.append(Spacer(1, 0.3*cm))
    story += section_block("4.2 Espace Administrateur", styles)
    story.append(Paragraph(
        "L'administrateur dispose d'un contrôle total sur le système. Il accède à l'ensemble "
        "des données, peut créer/modifier/supprimer tous les enregistrements et exporter les données.",
        styles["body"]
    ))

    admin_modules = [
        ("Dashboard (/admin/dashboard)", [
            "Cartes KPI : total étudiants, cours, séances, notes, absences, utilisateurs",
            "Jauge de la moyenne générale (code couleur : vert ≥ 12, amber ≥ 10, rouge < 10)",
            "Histogramme de la distribution des notes",
            "Graphique en anneau : répartition des étudiants par classe",
            "Barres de progression par cours (heures réalisées vs volume total)",
            "Tableau des derniers étudiants inscrits",
        ]),
        ("Gestion Étudiants (/admin/etudiants)", [
            "Liste complète des étudiants en tableau filtrable",
            "Ajout d'étudiant via modal avec formulaire validé",
            "Modification des informations (nom, prénom, email, classe, date de naissance)",
            "Suppression avec cascade (notes et présences associées supprimées)",
            "Fiche individuelle : moyenne générale, absences, détail des notes par matière",
        ]),
        ("Gestion Cours (/admin/cours)", [
            "Création de cours : code, intitulé, volume horaire, enseignant, classe",
            "Modification et suppression des cours",
            "Visualisation des cours par classe",
        ]),
        ("Gestion Séances (/admin/seances)", [
            "Planification de séances : date, durée, thème, type (cours/TD/TP)",
            "Saisie des présences par séance (sélection des absents/retardataires)",
            "Historique complet des séances par cours",
        ]),
        ("Gestion Notes (/admin/notes)", [
            "Téléchargement d'un modèle Excel pré-rempli avec les étudiants du cours",
            "Import d'un fichier Excel de notes (colonnes : ID, Nom, Prénom, Note, Coefficient)",
            "Saisie directe dans un tableau interactif",
            "Filtrage par cours et type d'évaluation",
        ]),
        ("Analyse (/admin/analyse)", [
            "Statistiques descriptives par matière (min, max, moyenne, écart-type)",
            "Analyse de la progression au fil des séances",
            "Comparaisons inter-classes",
        ]),
        ("Export PDF (/admin/pdf)", [
            "Génération de bulletins de notes individuels (format A4)",
            "Création d'attestations de scolarité",
            "Export via ReportLab",
        ]),
    ]

    for mod_title, features in admin_modules:
        story += subsection_block(mod_title, styles)
        for f in features:
            story.append(bullet_item(f, styles))
        story.append(Spacer(1, 0.1*cm))

    story += section_block("4.3 Espace Responsable", styles)
    story.append(Paragraph(
        "Le responsable de cours dispose d'un accès similaire à celui de l'administrateur, "
        "mais restreint aux cours et étudiants de sa classe. Il peut saisir les présences et notes.",
        styles["body"]
    ))
    resp_modules = [
        "Dashboard filtré sur ses cours avec KPIs personnels",
        "Liste des étudiants inscrits dans ses cours",
        "Gestion du contenu pédagogique (supports de cours, PDFs)",
        "Saisie des présences par séance",
        "Saisie et visualisation des notes de ses étudiants",
        "Analyse des performances des étudiants de ses cours",
    ]
    for m in resp_modules:
        story.append(bullet_item(m, styles))

    story.append(Spacer(1, 0.2*cm))
    story += section_block("4.4 Espace Étudiant", styles)
    story.append(Paragraph(
        "L'espace étudiant est une vue en lecture seule de ses données personnelles académiques. "
        "L'étudiant peut consulter ses résultats et accéder aux ressources pédagogiques.",
        styles["body"]
    ))

    etud_modules = [
        ("Dashboard personnel (/etudiant/dashboard)", [
            "Message d'accueil personnalisé avec nom et classe",
            "KPI : moyenne générale, matières validées (≥10), absences, retards",
            "Jauge de la moyenne personnelle (code couleur)",
            "Graphique à barres des notes par matière",
            "Liens rapides vers les pages de détail",
        ]),
        ("Mes Notes (/etudiant/notes)", [
            "Détail complet des notes par matière et par type d'évaluation",
            "Coefficients affichés, indicateur de validation (vert/rouge)",
        ]),
        ("Mes Absences (/etudiant/absences)", [
            "Historique chronologique des absences et retards",
            "Vue par séance : date, cours, thème, type d'absence",
        ]),
        ("Mes Cours (/etudiant/cours)", [
            "Accès aux supports PDF organisés par matière",
            "Téléchargement direct des documents pédagogiques",
        ]),
    ]
    for mod_title, features in etud_modules:
        story += subsection_block(mod_title, styles)
        for f in features:
            story.append(bullet_item(f, styles))

    story.append(PageBreak())
    return story


# ─── CHAPITRE 5 : Design System ───────────────────────────────────────────────
def chapter5(styles):
    story = []
    story += chapter_block("5. Interface utilisateur & Design system", styles)

    story += section_block("5.1 Palette de couleurs ENSAE", styles)
    story.append(Paragraph(
        "La charte graphique est définie dans assets/style.css et utilise les couleurs "
        "officielles de l'ENSAE Dakar, avec une esthétique moderne style 'dark tech'.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.2*cm))

    color_data = [
        ["Primary Blue",  "#106EBE", "Accents principaux, en-têtes, boutons d'action"],
        ["Mint Green",    "#0FFCBE", "Survols, indicateurs actifs, éléments interactifs"],
        ["Dark Navy",     "#0A1628", "Fond principal, navbar, footer"],
        ["Success Green", "#10B981", "Notes validées (≥10), statuts positifs"],
        ["Amber Warning", "#F59E0B", "Avertissements, progression moyenne (40–75%)"],
        ["Error Red",     "#EF4444", "Notes échec (<10), alertes, suppressions"],
        ["Purple",        "#7C3AED", "Indicateurs statistiques, visualisations secondaires"],
        ["Gray Light",    "#F1F5F9", "Fond des cartes, lignes alternées dans les tableaux"],
    ]
    headers = ["Nom", "Valeur Hex", "Utilisation"]
    story.append(make_table(headers, color_data, [4*cm, 3*cm, 10*cm]))
    story.append(Paragraph("Tableau 5 — Palette de couleurs", styles["caption"]))

    story += section_block("5.2 Typographie et composants", styles)
    typo = [
        ("Police principale", "Inter (Google Fonts)", "Moderne, lisible, open-source"),
        ("Tailles de texte", "11px – 44px",           "Hiérarchie typographique claire"),
        ("Espacement lettres", "Variable par taille", "Ajustements pour les titres"),
        ("Cartes KPI",        "Dash Bootstrap Card",  "Icône + valeur + libellé, bordure colorée"),
        ("Modals CRUD",       "dbc.Modal",            "Formulaires ajout/modification/suppression"),
        ("Graphiques",        "Plotly Express/GO",    "Jauges, histogrammes, barres, anneau"),
        ("Badges/étiquettes", "dbc.Badge",            "Rôles, classes, statuts"),
        ("Barres de progression","dbc.Progress",      "Avancement cours, taux de réussite"),
        ("Navigation dropdown","HTML + CSS hover",    "Menus déroulants au survol"),
    ]
    story.append(make_table(["Élément", "Technologie", "Description"],
                            typo, [4*cm, 4.5*cm, 8.5*cm]))
    story.append(Paragraph("Tableau 6 — Composants UI principaux", styles["caption"]))

    story += section_block("5.3 Navigation et responsive", styles)
    nav_points = [
        "Navbar fixe en haut (hauteur 74px), fond dark navy, logo SGA à gauche",
        "Mode public : liens Accueil, Découverte, Admission + bouton Connexion",
        "Mode connecté : menu adapté au rôle + puce utilisateur (initiales + badge rôle)",
        "Menus déroulants par hover CSS (transition 0.26s cubic-bezier) pour les sections multi-pages",
        "Grille Bootstrap responsive (12 colonnes) — 1 colonne mobile, 3-4 colonnes desktop",
        "Effets glassmorphism sur les cartes : backdrop-filter blur pour la profondeur visuelle",
        "Transitions CSS fluides (0.2s ease) sur les états hover/focus des éléments interactifs",
    ]
    for p in nav_points:
        story.append(bullet_item(p, styles))

    story.append(PageBreak())
    return story


# ─── CHAPITRE 6 : Sécurité ────────────────────────────────────────────────────
def chapter6(styles):
    story = []
    story += chapter_block("6. Sécurité et authentification", styles)

    story += section_block("6.1 Mécanisme d'authentification", styles)
    story.append(Paragraph(
        "L'authentification est gérée par un formulaire sur la page /login. "
        "Les mots de passe sont hachés avec SHA-256 avant stockage. "
        "La vérification compare le haché saisi au haché stocké.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.15*cm))

    auth_steps = [
        ["1", "L'utilisateur saisit son identifiant et mot de passe sur /login"],
        ["2", "Le callback Python applique hashlib.sha256() sur le mot de passe saisi"],
        ["3", "Requête SQLAlchemy : SELECT * FROM users WHERE username=? AND password_h=?"],
        ["4", "Si correspondance : remplissage du dcc.Store de session (id, role, nom, student_id)"],
        ["5", "Redirection vers le dashboard correspondant au rôle"],
        ["6", "Si échec : affichage d'un message d'erreur inline"],
    ]
    story.append(make_table(["Étape", "Action"], auth_steps, [1.5*cm, 15.5*cm]))
    story.append(Paragraph("Tableau 7 — Flux d'authentification", styles["caption"]))

    story += section_block("6.2 Contrôle d'accès par rôle (RBAC)", styles)
    story.append(Paragraph(
        "Chaque page protégée vérifie le rôle dans le dcc.Store de session au début de son callback. "
        "Si le rôle ne correspond pas, l'utilisateur est redirigé vers /login. "
        "Trois niveaux d'accès sont définis :",
        styles["body"]
    ))

    rbac = [
        ["admin",       "Accès total — lecture, écriture, suppression sur toutes les données"],
        ["responsable", "Accès limité à ses cours — saisie notes et présences uniquement"],
        ["etudiant",    "Accès lecture seule — uniquement ses propres données personnelles"],
    ]
    story.append(make_table(["Rôle", "Droits d'accès"], rbac, [3*cm, 14*cm]))
    story.append(Paragraph("Tableau 8 — Niveaux d'accès par rôle", styles["caption"]))

    story += section_block("6.3 Gestion des sessions", styles)
    session_points = [
        "dcc.Store(id='session-store', storage_type='session') : stockage côté client dans le sessionStorage du navigateur",
        "Données stockées : {id, username, role, nom, prenom, student_id}",
        "La session est effacée lors de la déconnexion (/logout → store vidé → redirect /)",
        "Aucun cookie serveur : la gestion de l'état est entièrement côté client via Dash Store",
        "Limite : pas de timeout automatique de session (amélioration possible)",
    ]
    for p in session_points:
        story.append(bullet_item(p, styles))

    story.append(info_box(
        "<b>Note de sécurité :</b> En environnement de production, il serait recommandé d'utiliser "
        "Flask-Login avec des sessions serveur sécurisées, HTTPS obligatoire, et des tokens CSRF "
        "pour les formulaires de modification.",
        styles, color=AMBER
    ))

    story.append(PageBreak())
    return story


# ─── CHAPITRE 7 : Flux de données ─────────────────────────────────────────────
def chapter7(styles):
    story = []
    story += chapter_block("7. Flux de données et cas d'usage", styles)

    story += section_block("7.1 Import/Export Excel des notes", styles)
    story.append(Paragraph(
        "La plateforme propose un workflow complet pour la saisie des notes via Excel, "
        "particulièrement utile pour les responsables gérant de nombreux étudiants.",
        styles["body"]
    ))

    story += subsection_block("Export du modèle", styles)
    story.append(Paragraph(
        "L'administrateur ou le responsable sélectionne un cours. Le système génère automatiquement "
        "un fichier .xlsx via openpyxl avec les colonnes : ID, Nom, Prénom (pré-remplis avec les "
        "étudiants du cours), Note, Coefficient (à renseigner). Ce fichier est téléchargeable "
        "directement depuis l'interface.",
        styles["body"]
    ))

    story += subsection_block("Import des notes complétées", styles)
    story.append(Paragraph(
        "Après saisie des notes dans Excel, le fichier est importé via un composant dcc.Upload. "
        "Pandas lit le fichier, valide les colonnes, et insère les enregistrements dans la table "
        "grades. Les doublons sont gérés par vérification préalable.",
        styles["body"]
    ))

    story += section_block("7.2 Génération de bulletins PDF", styles)
    story.append(Paragraph(
        "La page /admin/pdf utilise ReportLab pour générer des bulletins de notes personnalisés. "
        "Le bulletin contient : identité de l'étudiant, tableau des notes par matière, "
        "moyennes calculées, statistiques d'absences, et le cachet de l'ENSAE.",
        styles["body"]
    ))

    pdf_steps = [
        ["1", "Sélection de l'étudiant dans la liste déroulante"],
        ["2", "Récupération des données : notes, absences, informations étudiant via SQLAlchemy"],
        ["3", "Calcul de la moyenne pondérée (Σ note × coefficient / Σ coefficients)"],
        ["4", "Construction du document ReportLab (SimpleDocTemplate, tableaux, paragraphes)"],
        ["5", "Envoi du fichier PDF en réponse HTTP (dcc.send_bytes)"],
    ]
    story.append(make_table(["Étape", "Action"], pdf_steps, [1.5*cm, 15.5*cm]))
    story.append(Paragraph("Tableau 9 — Flux de génération PDF", styles["caption"]))

    story += section_block("7.3 Gestion des présences", styles)
    story.append(Paragraph(
        "La gestion des présences est liée aux séances. Pour chaque séance créée, "
        "l'enseignant peut marquer les étudiants absents ou en retard.",
        styles["body"]
    ))

    attendance_flow = [
        "Création d'une séance (cours, date, durée, thème) → enregistrement dans sessions",
        "L'interface affiche la liste des étudiants du cours concerné",
        "Sélection des absents/retardataires via checklist ou dropdown",
        "Enregistrement dans attendance (id_session, id_student, type_abs)",
        "Les statistiques sont recalculées en temps réel dans les dashboards",
        "Les étudiants voient leurs absences sur /etudiant/absences",
    ]
    for f in attendance_flow:
        story.append(bullet_item(f, styles))

    story.append(Spacer(1, 0.3*cm))
    story.append(info_box(
        "<b>Calcul de la moyenne pondérée :</b> "
        "La moyenne est calculée par la formule : "
        "Σ(note × coefficient) / Σ(coefficients). "
        "Les coefficients par défaut sont : Devoir = 1.0, Partiel = 1.5, Examen = 2.0.",
        styles
    ))

    story.append(PageBreak())
    return story


# ─── CHAPITRE 8 : Déploiement ─────────────────────────────────────────────────
def chapter8(styles):
    story = []
    story += chapter_block("8. Comptes de démonstration & déploiement", styles)

    story += section_block("8.1 Comptes par défaut", styles)
    story.append(Paragraph(
        "Au premier démarrage, database.py crée automatiquement trois comptes de démonstration "
        "permettant de tester l'ensemble des fonctionnalités de la plateforme.",
        styles["body"]
    ))
    story.append(Spacer(1, 0.15*cm))

    accounts = [
        ["admin",        "admin123",  "admin",       "/admin/dashboard",        "  Suivi et controle "],
        ["responsable1", "resp123",   "responsable", "/responsable/dashboard",  "Accès cours assignés"],
        ["etudiant1",    "etud123",   "etudiant",    "/etudiant/dashboard",     "Accès données personnelles"],
    ]
    headers = ["Identifiant", "Mot de passe", "Rôle", "Page d'accueil", "Description"]
    story.append(make_table(headers, accounts, [3*cm, 3*cm, 3*cm, 4.5*cm, 3.5*cm]))
    story.append(Paragraph("Tableau 10 — Comptes de démonstration", styles["caption"]))

    story += section_block("8.2 Données de démonstration générées", styles)
    story.append(Paragraph(
        "La fonction seed_demo_data() génère un jeu de données réaliste pour tester toutes "
        "les fonctionnalités de la plateforme sans avoir à saisir manuellement des données.",
        styles["body"]
    ))

    demo_data = [
        ["Étudiants",    "40",          "Noms sénégalais réalistes, classes ISE1/ISE2/ITS1/TSS1"],
        ["Cours",        "8",           "Mathématiques, Statistiques, Informatique, Économie, etc."],
        ["Séances",      "4–8 / cours", "Dates aléatoires, durées variées (1.5h, 2h, 3h)"],
        ["Absences",     "10–20%",      "Taux aléatoire par séance, mix absence/retard"],
        ["Notes",        "1–2 / étud.", "Distribution gaussienne (μ=12.5, σ=3.5), borné 0–20"],
        ["Comptes étud.","40+",         "etud_2 à etud_41, mot de passe : etud123"],
    ]
    story.append(make_table(
        ["Donnée", "Quantité", "Détails de génération"],
        demo_data, [3.5*cm, 3*cm, 10.5*cm]
    ))
    story.append(Paragraph("Tableau 11 — Données de démonstration", styles["caption"]))

    story += section_block("8.3 Installation et démarrage", styles)

    install_code = [
        "# 1. Cloner ou décompresser le projet",
        "cd sga_v3",
        "",
        "# 2. Créer un environnement virtuel (recommandé)",
        "python -m venv venv",
        "source venv/bin/activate       # Linux/Mac",
        "venv\\Scripts\\activate          # Windows",
        "",
        "# 3. Installer les dépendances",
        "pip install -r requirements.txt",
        "",
        "# 4. Lancer l'application",
        "python app.py",
        "",
        "# 5. Ouvrir dans le navigateur",
        "# → http://localhost:8050",
    ]
    code_style = ParagraphStyle(
        "install", fontName="Courier", fontSize=8, textColor=HexColor("#1E293B"),
        leading=12, backColor=HexColor("#F8FAFC"), borderColor=HexColor("#CBD5E1"),
        borderWidth=0.5, borderPad=10,
    )
    story.append(Paragraph(
        "<br/>".join(l.replace(" ", "&nbsp;") if l else "&nbsp;" for l in install_code),
        code_style
    ))
    story.append(Spacer(1, 0.2*cm))

    config_info = [
        ["Mode",          "Debug (development)"],
        ["Host",          "127.0.0.1 (localhost)"],
        ["Port",          "8050"],
        ["Base de données","SQLite → data/sga.db (créé automatiquement)"],
        ["Fichiers statiques","assets/ (servi automatiquement par Dash)"],
        ["Dossiers auto-créés","data/, assets/img/, assets/cours/"],
    ]
    story.append(make_table(
        ["Paramètre", "Valeur"],
        config_info, [5*cm, 12*cm]
    ))
    story.append(Paragraph("Tableau 12 — Configuration de l'application", styles["caption"]))

    story.append(Spacer(1, 0.4*cm))
    story += section_block("8.4 Liens de la plateforme", styles)

    links_data = [
        ["Plateforme déployée", "https://projet-dataviz-aissatou-gueye-plateforme.onrender.com/"],
        ["Dépôt GitHub",        "https://github.com/Aissatou150/Projet-Dataviz-A-ssatou-GUEYE-Plateforme-SGA/tree/main"],
    ]
    story.append(make_table(["Ressource", "URL"], links_data, [4.5*cm, 12.5*cm]))

    story.append(PageBreak())
    return story


# ─── PAGE DE GARDE : fond sombre (rendu via on_first_page) ────────────────────
def on_first_page(canvas_obj, doc):
    canvas_obj.saveState()
    w, h = A4
    # Fond dégradé simulé (deux rectangles)
    canvas_obj.setFillColor(DARK)
    canvas_obj.rect(0, 0, w, h, fill=1, stroke=0)
    # Bande décorative en bas
    canvas_obj.setFillColor(BLUE)
    canvas_obj.rect(0, 0, w, 0.8*cm, fill=1, stroke=0)
    # Trait mint
    canvas_obj.setStrokeColor(MINT)
    canvas_obj.setLineWidth(3)
    canvas_obj.line(0, 0.8*cm, w, 0.8*cm)
    # Bande déco en haut
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, h - 1.5*cm, w, 1.5*cm, fill=1, stroke=0)
    canvas_obj.setStrokeColor(BLUE)
    canvas_obj.setLineWidth(2)
    canvas_obj.line(0, h - 1.5*cm, w, h - 1.5*cm)
    # Texte header
    canvas_obj.setFillColor(GRAY_MID)
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawCentredString(w/2, h - 0.9*cm, "ENSAE Dakar  ·  École Nationale de la Statistique et de l'Analyse Économique")
    canvas_obj.restoreState()

def on_later_pages(canvas_obj, doc):
    canvas_obj.saveState()
    w, h = A4
    # Header avec bandeau
    canvas_obj.setFillColor(DARK)
    canvas_obj.rect(0, h - 1.2*cm, w, 1.2*cm, fill=1, stroke=0)
    canvas_obj.setStrokeColor(BLUE)
    canvas_obj.setLineWidth(1.5)
    canvas_obj.line(0, h - 1.2*cm, w, h - 1.2*cm)
    canvas_obj.setFillColor(GRAY_MID)
    canvas_obj.setFont("Helvetica", 7.5)
    canvas_obj.drawString(1.5*cm, h - 0.75*cm, "SGA · ENSAE Dakar")
    canvas_obj.setFillColor(WHITE)
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.drawRightString(w - 1.5*cm, h - 0.75*cm, "Documentation Technique v3")
    canvas_obj.restoreState()


# ─── ASSEMBLAGE FINAL ─────────────────────────────────────────────────────────
def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=1.8*cm,
        bottomMargin=1.5*cm,
        title="Documentation SGA · ENSAE Dakar v3",
        author="SGA Platform",
        subject="Documentation technique et fonctionnelle",
        creator="ReportLab via generate_doc.py",
    )

    styles = build_styles()
    story = []

    story += cover_page(styles)
    story += toc_page(styles)
    story += chapter1(styles)
    story += chapter2(styles)
    story += chapter3(styles)
    story += chapter4(styles)
    story += chapter5(styles)
    story += chapter6(styles)
    story += chapter7(styles)
    story += chapter8(styles)
    doc.build(
        story,
        onFirstPage=on_first_page,
        onLaterPages=on_later_pages,
        canvasmaker=NumberedCanvas,
    )

    print(f"[OK] Documentation generee : {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    build_pdf()
