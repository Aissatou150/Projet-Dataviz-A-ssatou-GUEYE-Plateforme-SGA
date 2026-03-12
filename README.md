# SGA · ENSAE Dakar v3

Système de Gestion Académique moderne pour l’ENSAE Dakar — gestion des étudiants, cours, notes, absences, et plus, avec interface Dash et SQLAlchemy.

---

## 🚀 Installation & Lancement

1. Cloner le dépôt et se placer dans le dossier :
   ```bash
   git clone ...
   cd sga_v3
   ```
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancer l’application :
   ```bash
   python app.py
   ```
4. Ouvrir [http://localhost:8050](http://localhost:8050)

---

## 👤 Comptes de démonstration

| Profil       | Identifiant | Mot de passe |
|--------------|------------|--------------|
| Admin        | admin      | admin123     |
| Responsable  | responsable1 | resp123     |
| Étudiant     | etudiant1  | etud123      |

---

## 📁 Structure du projet

```
sga_v3/
├── app.py           # Point d’entrée Dash, navbar dynamique
├── models.py        # Modèles SQLAlchemy (ORM)
├── database.py      # Connexion DB, seed, migration
├── requirements.txt
├── README.md
├── assets/
│   ├── style.css    # Thème et design
│   ├── img/         # Images ENSAE
│   ├── video/       # Vidéos MP4 (accueil, découverte)
│   └── cours/       # PDF de cours par matière
├── data/
│   └── db.xlsx      # (optionnel) Migration Excel
└── pages/
    ├── accueil.py
    ├── decouverte.py
    ├── login.py
    ├── shared.py
    ├── admin/         # Espace admin (dashboard, étudiants, etc.)
    ├── responsable/   # Espace responsable
    └── etudiant/      # Espace étudiant
```

---

## 🎬 Ajouter vos vidéos MP4

Déposez vos fichiers dans `assets/video/` :

| Fichier                      | Page            | Description                  |
|------------------------------|-----------------|------------------------------|
| directeur.mp4                | Accueil         | Message du Directeur         |
| ensae.mp4                    | Découverte      | Présentation de l’ENSAE      |

---

## 📚 Ajouter des cours PDF

1. Créez un dossier avec le code du cours :
   `assets/cours/MATH101/`
2. Placez-y vos PDF :
   `assets/cours/MATH101/Chapitre1.pdf`
3. Les étudiants y accèdent via « Mes cours ».

---

## 🎨 Couleurs du design

- Bleu ENSAE : `#106EBE`
- Menthe : `#0FFCBE`
- Noir profond : `#0A1628`
- Blanc : `#FFFFFF`

---

## 🛠️ Fonctionnalités principales

- Authentification 3 profils (admin, responsable, étudiant)
- Gestion étudiants/cours/notes/absences
- Import/Export Excel (admin)
- Analyse de données et export PDF (admin)
- Ajout de vidéos et PDF sans code
- Interface responsive et moderne (Dash + Bootstrap)

---

## 🤝 Contribuer

Pull requests bienvenues !

---

© ENSAE Dakar — Projet pédagogique, 2026


Par 
- Aissatou GUEYE Analyste statisticienne en fin de formation
- Kassi mamadou maxwell Analyste statisticien en fin de formation