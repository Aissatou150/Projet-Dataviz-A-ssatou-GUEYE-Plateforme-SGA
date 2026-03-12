import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from database import SessionLocal
from models import Student, Grade, Course, Attendance, Session as CourseSession
import io, base64
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
from datetime import date
dash.register_page(__name__, path='/admin/pdf-export', title='PDF Export — Admin SGA')


BLUE  = colors.HexColor("#2C4A6E")
GREEN = colors.HexColor("#1B7A4A")
GOLD  = colors.HexColor("#C8963E")
RED   = colors.HexColor("#C0392B")
GREY  = colors.HexColor("#9AA5B4")
LIGHT = colors.HexColor("#F5F7FA")


def student_options():
    db = SessionLocal()
    try:
        return [{"label":f"{s.prenom} {s.nom}","value":s.id} for s in db.query(Student).order_by(Student.nom).all()]
    finally:
        db.close()


def layout():
    return html.Div([
        html.Div([
            html.H2("Export PDF"),
            html.Div("Génération de bulletins de notes individuels", className="page-sub"),
        ], className="page-header"),

        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div("Bulletin de notes individuel", className="card-header"),
                        html.Div([
                            html.P("Sélectionnez un étudiant pour générer son bulletin de notes au format PDF.", style={"color":"var(--grey-400)","fontSize":"13px","marginBottom":"20px"}),
                            dbc.Label("Étudiant"),
                            dcc.Dropdown(id="sel-etud-pdf", options=student_options(), placeholder="Choisir un étudiant"),
                            html.Div(style={"height":"16px"}),
                            dbc.Button("Générer le bulletin PDF", id="btn-gen-pdf", color="primary", className="w-100"),
                            html.Div(id="pdf-feedback", className="mt-3"),
                            dcc.Download(id="download-pdf"),
                        ], className="card-body"),
                    ], className="card"),
                ], width=12, lg=5),
            ]),
        ], className="page-body"),
    ])


@callback(
    Output("download-pdf","data"), Output("pdf-feedback","children"),
    Input("btn-gen-pdf","n_clicks"), State("sel-etud-pdf","value"),
    prevent_initial_call=True,
)
def gen_pdf(_, sid):
    if not sid:
        return dash.no_update, dbc.Alert("Veuillez sélectionner un étudiant.", color="warning")
    db = SessionLocal()
    try:
        s        = db.query(Student).filter_by(id=int(sid)).first()
        grades   = db.query(Grade).filter_by(id_student=s.id).all()
        absences = db.query(Attendance).filter_by(id_student=s.id).count()
        total_s  = db.query(CourseSession).count()
        taux     = round(absences / total_s * 100, 1) if total_s > 0 else 0

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm,   bottomMargin=2*cm)

        story = []

        # En-tête institution
        story.append(Paragraph(
            "<b>ÉCOLE NATIONALE DE LA STATISTIQUE ET DE L'ANALYSE ÉCONOMIQUE</b>",
            ParagraphStyle("inst", fontName="Helvetica-Bold", fontSize=11,
                           alignment=1, textColor=BLUE, spaceAfter=2)
        ))
        story.append(Paragraph(
            "Système de Gestion Académique",
            ParagraphStyle("sub", fontName="Helvetica", fontSize=9,
                           alignment=1, textColor=GREY, spaceAfter=16)
        ))

        # Ligne décorative
        story.append(Table([[""]], colWidths=[17*cm],
                           style=[("LINEBELOW",(0,0),(0,0),2,BLUE),
                                  ("LINEBELOW",(0,0),(0,0),0.5,GOLD)]))
        story.append(Spacer(1, 0.4*cm))

        # Titre bulletin
        story.append(Paragraph(
            "BULLETIN DE NOTES",
            ParagraphStyle("titre", fontName="Helvetica-Bold", fontSize=16,
                           alignment=1, textColor=BLUE, spaceAfter=16)
        ))

        # Infos étudiant
        info = [
            [Paragraph("<b>NOM & PRÉNOM</b>", ParagraphStyle("lbl",fontName="Helvetica-Bold",fontSize=8,textColor=GREY)),
             Paragraph(f"{s.prenom} {s.nom}", ParagraphStyle("val",fontName="Helvetica",fontSize=10,textColor=colors.HexColor("#1E2A3A"))),
             Paragraph("<b>IDENTIFIANT</b>", ParagraphStyle("lbl",fontName="Helvetica-Bold",fontSize=8,textColor=GREY)),
             Paragraph(str(s.id), ParagraphStyle("val",fontName="Helvetica",fontSize=10))],
            [Paragraph("<b>EMAIL</b>", ParagraphStyle("lbl",fontName="Helvetica-Bold",fontSize=8,textColor=GREY)),
             Paragraph(s.email or "—", ParagraphStyle("val",fontName="Helvetica",fontSize=10)),
             Paragraph("<b>DATE DE NAISSANCE</b>", ParagraphStyle("lbl",fontName="Helvetica-Bold",fontSize=8,textColor=GREY)),
             Paragraph(str(s.dob) if s.dob else "—", ParagraphStyle("val",fontName="Helvetica",fontSize=10))],
            [Paragraph("<b>ABSENCES</b>", ParagraphStyle("lbl",fontName="Helvetica-Bold",fontSize=8,textColor=GREY)),
             Paragraph(f"{absences} séance(s)", ParagraphStyle("val",fontName="Helvetica",fontSize=10)),
             Paragraph("<b>TAUX D'ABSENCE</b>", ParagraphStyle("lbl",fontName="Helvetica-Bold",fontSize=8,textColor=GREY)),
             Paragraph(f"{taux} %", ParagraphStyle("val",fontName="Helvetica",fontSize=10))],
        ]
        t_info = Table(info, colWidths=[4*cm, 5.5*cm, 4*cm, 3.5*cm])
        t_info.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,-1), LIGHT),
            ("GRID",       (0,0),(-1,-1), 0.5, colors.HexColor("#DDE2EA")),
            ("PADDING",    (0,0),(-1,-1), 7),
            ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ]))
        story.append(t_info)
        story.append(Spacer(1, 0.5*cm))

        # Tableau des notes
        story.append(Paragraph("RÉSULTATS PAR MATIÈRE",
                                ParagraphStyle("h2",fontName="Helvetica-Bold",fontSize=9,
                                               textColor=GREY,spaceBefore=8,spaceAfter=8,
                                               letterSpacing=1.5)))

        if grades:
            total_pts   = sum(g.note * g.coefficient for g in grades)
            total_coeff = sum(g.coefficient for g in grades)
            moyenne     = round(total_pts / total_coeff, 2) if total_coeff > 0 else 0

            header_row = [
                Paragraph("<b>CODE</b>",    ParagraphStyle("th",fontName="Helvetica-Bold",fontSize=9,textColor=colors.white,alignment=1)),
                Paragraph("<b>MATIÈRE</b>", ParagraphStyle("th",fontName="Helvetica-Bold",fontSize=9,textColor=colors.white)),
                Paragraph("<b>NOTE /20</b>",ParagraphStyle("th",fontName="Helvetica-Bold",fontSize=9,textColor=colors.white,alignment=1)),
                Paragraph("<b>COEFF</b>",   ParagraphStyle("th",fontName="Helvetica-Bold",fontSize=9,textColor=colors.white,alignment=1)),
                Paragraph("<b>POINTS</b>",  ParagraphStyle("th",fontName="Helvetica-Bold",fontSize=9,textColor=colors.white,alignment=1)),
            ]
            data_rows = [header_row]
            row_styles = [
                ("BACKGROUND", (0,0),(-1,0), BLUE),
                ("GRID",       (0,0),(-1,-1), 0.5, colors.HexColor("#DDE2EA")),
                ("PADDING",    (0,0),(-1,-1), 7),
                ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
            ]
            for i, g in enumerate(grades, 1):
                c = db.query(Course).filter_by(code=g.course_code).first()
                libelle = c.libelle if c else g.course_code
                note_color = GREEN if g.note >= 10 else RED
                row_bg = colors.HexColor("#F0F9F4") if g.note >= 10 else colors.HexColor("#FDF0EF")
                data_rows.append([
                    Paragraph(g.course_code, ParagraphStyle("td",fontName="Helvetica-Bold",fontSize=9,textColor=BLUE,alignment=1)),
                    Paragraph(libelle,       ParagraphStyle("td",fontName="Helvetica",fontSize=9)),
                    Paragraph(f"{g.note}/20",ParagraphStyle("td",fontName="Helvetica-Bold",fontSize=10,textColor=note_color,alignment=1)),
                    Paragraph(str(g.coefficient), ParagraphStyle("td",fontName="Helvetica",fontSize=9,alignment=1)),
                    Paragraph(str(round(g.note*g.coefficient,2)), ParagraphStyle("td",fontName="Helvetica",fontSize=9,alignment=1)),
                ])
                row_styles.append(("BACKGROUND",(0,i),(-1,i), row_bg))

            moy_color = GREEN if moyenne >= 10 else RED
            data_rows.append([
                Paragraph("", ParagraphStyle("td")),
                Paragraph("<b>MOYENNE GÉNÉRALE</b>", ParagraphStyle("td",fontName="Helvetica-Bold",fontSize=9,textColor=BLUE)),
                Paragraph(f"<b>{moyenne}/20</b>", ParagraphStyle("td",fontName="Helvetica-Bold",fontSize=11,textColor=moy_color,alignment=1)),
                Paragraph("", ParagraphStyle("td")),
                Paragraph("", ParagraphStyle("td")),
            ])
            row_styles.append(("BACKGROUND",(0,-1),(-1,-1), LIGHT))
            row_styles.append(("LINEABOVE",  (0,-1),(-1,-1), 1.5, BLUE))

            t_grades = Table(data_rows, colWidths=[2.5*cm, 6.5*cm, 3*cm, 2.5*cm, 2.5*cm])
            t_grades.setStyle(TableStyle(row_styles))
            story.append(t_grades)
        else:
            story.append(Paragraph("Aucune note enregistrée.", ParagraphStyle("nd",fontName="Helvetica",fontSize=10,textColor=GREY)))

        story.append(Spacer(1, 1.5*cm))
        story.append(Paragraph(
            f"Document généré le {date.today().strftime('%d/%m/%Y')} — ENSAE Dakar · Système de Gestion Académique",
            ParagraphStyle("footer",fontName="Helvetica",fontSize=8,textColor=GREY,alignment=2)
        ))

        doc.build(story)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        return (
            dict(content=b64, filename=f"bulletin_{s.nom}_{s.prenom}.pdf",
                 base64=True, type="application/pdf"),
            dbc.Alert(f"Bulletin PDF généré pour {s.prenom} {s.nom}.", color="success", dismissable=True),
        )
    except Exception as e:
        return dash.no_update, dbc.Alert(f"Erreur : {e}", color="danger")
    finally:
        db.close()
