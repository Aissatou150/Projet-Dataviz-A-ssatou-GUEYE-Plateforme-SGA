import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash
from database import SessionLocal
from models import Course, Student, Grade
import pandas as pd, base64, io
dash.register_page(__name__, path='/admin/notes', title='Notes — Admin SGA')




def course_options():
    db = SessionLocal()
    try:
        return [{"label":f"{c.code} — {c.libelle}","value":c.code} for c in db.query(Course).all()]
    finally:
        db.close()


def layout():
    opts = course_options()
    return html.Div([
        html.Div([
            html.H2("Notes & Évaluations"),
            html.Div("Génération de templates, import et consultation des notes", className="page-sub"),
        ], className="page-header"),

        html.Div([
            dbc.Tabs([
                dbc.Tab(label="Télécharger template", tab_id="tab-dl", children=[
                    html.Div([
                        html.Div("Étape 1 — Générer le fichier de saisie", className="card-header"),
                        html.Div([
                            html.P("Sélectionnez un cours pour générer un fichier Excel pré-rempli avec la liste des étudiants. Complétez la colonne Note puis importez le fichier.", style={"color":"var(--grey-400)","fontSize":"13px","marginBottom":"20px"}),
                            dbc.Row([
                                dbc.Col([dbc.Label("Cours"), dcc.Dropdown(id="sel-cours-notes", options=opts, placeholder="Sélectionner un cours")], width=5),
                                dbc.Col([dbc.Label("\u00a0"), dbc.Button("Générer le template", id="btn-gen-template", color="success", className="w-100")], width=3),
                            ]),
                            html.Div(id="dl-feedback", className="mt-3"),
                            dcc.Download(id="download-template"),
                        ], className="card-body"),
                    ], className="card mt-3"),
                ]),

                dbc.Tab(label="Importer les notes", tab_id="tab-ul", children=[
                    html.Div([
                        html.Div("Étape 3 — Importer le fichier complété", className="card-header"),
                        html.Div([
                            html.P(["Le fichier doit contenir : ", html.Strong("ID, Nom, Prénom, Note, Coefficient (optionnel)")], style={"color":"var(--grey-400)","fontSize":"13px","marginBottom":"16px"}),
                            dbc.Row([
                                dbc.Col([dbc.Label("Cours concerné"), dcc.Dropdown(id="sel-cours-upload", options=opts, placeholder="Sélectionner")], width=5),
                                dbc.Col([dbc.Label("\u00a0"), dbc.Checklist(id="chk-overwrite", options=[{"label":" Écraser les notes existantes","value":"overwrite"}], value=[], inline=True)], width=4),
                            ], className="mb-3"),
                            dcc.Upload(
                                id="upload-notes",
                                children=html.Div([
                                    html.Div("Déposer le fichier Excel ici", style={"fontWeight":"500","color":"var(--blue)","marginBottom":"4px"}),
                                    html.Div("ou cliquer pour parcourir", style={"fontSize":"12px","color":"var(--grey-400)"}),
                                ], style={"padding":"32px","textAlign":"center"}),
                                style={"borderWidth":"2px","borderStyle":"dashed","borderRadius":"8px",
                                       "borderColor":"var(--grey-200)","cursor":"pointer","background":"var(--off-white)"},
                                accept=".xlsx,.xls", multiple=False,
                            ),
                            html.Div(id="upload-notes-feedback", className="mt-3"),
                        ], className="card-body"),
                    ], className="card mt-3"),
                ]),

                dbc.Tab(label="Tableau des notes", tab_id="tab-tableau", children=[
                    html.Div([
                        html.Div("Consultation des notes", className="card-header"),
                        html.Div([
                            dbc.Row([
                                dbc.Col([dbc.Label("Filtrer par cours"), dcc.Dropdown(id="sel-cours-tableau", options=opts, placeholder="Tous les cours")], width=5),
                                dbc.Col([dbc.Label("\u00a0"), dbc.Button("Actualiser", id="btn-refresh-notes", color="secondary", outline=True)], width=3),
                            ], className="mb-3"),
                            html.Div(id="notes-tableau"),
                        ], className="card-body p-0" if True else "card-body"),
                    ], className="card mt-3"),
                ]),
            ], active_tab="tab-dl"),
        ], className="page-body"),
    ])


@callback(
    Output("download-template","data"), Output("dl-feedback","children"),
    Input("btn-gen-template","n_clicks"), State("sel-cours-notes","value"),
    prevent_initial_call=True,
)
def gen_template(_, code):
    if not code:
        return dash.no_update, dbc.Alert("Veuillez sélectionner un cours.", color="warning")
    db = SessionLocal()
    try:
        course   = db.query(Course).filter_by(code=code).first()
        students = db.query(Student).order_by(Student.nom).all()
        if not students:
            return dash.no_update, dbc.Alert("Aucun étudiant dans la base.", color="warning")
        df = pd.DataFrame([{"ID":s.id,"Nom":s.nom,"Prénom":s.prenom,"Note":"","Coefficient":1.0} for s in students])
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df.to_excel(w, index=False, sheet_name="Notes")
            for col in w.sheets["Notes"].columns:
                w.sheets["Notes"].column_dimensions[col[0].column_letter].width = 18
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        return (
            dict(content=b64, filename=f"notes_{code}.xlsx", base64=True,
                 type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            dbc.Alert(f"Template généré pour '{course.libelle}' ({len(students)} étudiants).", color="success", dismissable=True),
        )
    except Exception as e:
        return dash.no_update, dbc.Alert(f"Erreur : {e}", color="danger")
    finally:
        db.close()


@callback(
    Output("upload-notes-feedback","children"),
    Input("upload-notes","contents"),
    State("upload-notes","filename"), State("sel-cours-upload","value"), State("chk-overwrite","value"),
    prevent_initial_call=True,
)
def import_notes(contents, filename, course_code, overwrite):
    if not contents: return dash.no_update
    if not course_code: return dbc.Alert("Veuillez sélectionner le cours concerné.", color="warning")
    try:
        _, cs = contents.split(",")
        df = pd.read_excel(io.BytesIO(base64.b64decode(cs)))
        df.columns = df.columns.str.strip()
        missing = [c for c in ["ID","Note"] if c not in df.columns]
        if missing: return dbc.Alert(f"Colonnes manquantes : {', '.join(missing)}", color="danger")
        df = df.dropna(subset=["Note"])
        if df.empty: return dbc.Alert("Aucune note renseignée dans le fichier.", color="warning")
        db = SessionLocal()
        try:
            added, updated, errors = 0, 0, []
            for _, row in df.iterrows():
                try:
                    sid=int(row["ID"]); note=float(row["Note"])
                    coeff=float(row.get("Coefficient",1.0)) if not pd.isna(row.get("Coefficient",1.0)) else 1.0
                    if not (0 <= note <= 20): errors.append(f"Note invalide ({note}) pour ID={sid}"); continue
                    if not db.query(Student).filter_by(id=sid).first(): errors.append(f"Étudiant ID={sid} introuvable"); continue
                    ex = db.query(Grade).filter_by(id_student=sid, course_code=course_code).first()
                    if ex:
                        if "overwrite" in (overwrite or []): ex.note=note; ex.coefficient=coeff; updated+=1
                    else:
                        db.add(Grade(id_student=sid, course_code=course_code, note=note, coefficient=coeff)); added+=1
                except Exception as re: errors.append(str(re))
            db.commit()
            msgs = [dbc.Alert(f"{added} note(s) ajoutée(s), {updated} mise(s) à jour.", color="success")]
            if errors: msgs.append(dbc.Alert([html.Strong("Avertissements :"), html.Ul([html.Li(e) for e in errors])], color="warning"))
            return msgs
        except Exception as e:
            db.rollback(); return dbc.Alert(f"Erreur BDD : {e}", color="danger")
        finally:
            db.close()
    except Exception as e:
        return dbc.Alert(f"Fichier illisible ou corrompu : {e}", color="danger")


@callback(
    Output("notes-tableau","children"),
    Input("btn-refresh-notes","n_clicks"), Input("sel-cours-tableau","value"),
)
def update_tableau(_, code):
    db = SessionLocal()
    try:
        q = db.query(Grade, Student, Course).join(Student, Grade.id_student==Student.id).join(Course, Grade.course_code==Course.code)
        if code: q = q.filter(Grade.course_code==code)
        rows_data = q.order_by(Student.nom).all()
        if not rows_data: return dbc.Alert("Aucune note enregistrée.", color="info")
        header = html.Thead(html.Tr([html.Th("Étudiant"),html.Th("Cours"),html.Th("Note"),html.Th("Coefficient"),html.Th("Points")]))
        rows = [html.Tr([
            html.Td(f"{s.prenom} {s.nom}"),
            html.Td(f"{c.code} — {c.libelle}"),
            html.Td(dbc.Badge(f"{g.note}/20", color="success" if g.note>=10 else "danger")),
            html.Td(g.coefficient),
            html.Td(round(g.note*g.coefficient,2)),
        ]) for g,s,c in rows_data]
        return dbc.Table([header,html.Tbody(rows)], striped=False, hover=True, responsive=True, bordered=False)
    finally:
        db.close()
