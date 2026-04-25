from fpdf import FPDF
from datetime import datetime
import os

FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_I = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"

PAD = 4  # inner horizontal padding in mm — replaces leading spaces in strings


class RapportAquaterra(FPDF):
    def header(self):
        self.set_fill_color(46, 125, 50)
        self.rect(0, 0, 210, 22, "F")
        self.set_font("DjB", "", 14)
        self.set_text_color(255, 255, 255)
        self.set_xy(0, 6)
        self.cell(0, 12, "  AQUATERRA - Rapport d'Analyse Agricole", align="L")
        self.set_text_color(0, 0, 0)
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("DjI", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(
            0, 10,
            f"Aquaterra | Transition Ecologique & Dynamique Culturelle | Page {self.page_no()}",
            align="C",
        )

    def section(self, titre, couleur=(46, 125, 50)):
        self.ln(4)
        self.set_fill_color(*couleur)
        self.set_font("DjB", "", 11)
        self.set_text_color(255, 255, 255)
        self.cell(0, 9, f"  {titre}", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def info(self, label, valeur):
        self.set_font("DjB", "", 10)
        self.set_text_color(60, 60, 60)
        self.cell(70, 7, f"  {label} :", new_x="RIGHT", new_y="TOP")
        self.set_font("Dj", "", 10)
        self.set_text_color(30, 80, 30)
        self.cell(0, 7, str(valeur), new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)

    def _padded_multicell(self, text, line_h=6, font=None, color=None, bg=None):
        """
        Render wrapping text with PAD mm inner padding on each side.

        Root cause of the original bug: leading spaces inside multi_cell strings
        eat into the available wrap width without reducing the declared cell width,
        so fpdf2 overflows text and clips it at the cell boundary.
        Fix: offset x by PAD and shrink the cell width by 2*PAD instead.
        """
        if font:
            self.set_font(*font)
        if color:
            self.set_text_color(*color)
        if bg:
            self.set_fill_color(*bg)
        self.set_x(self.l_margin + PAD)
        self.multi_cell(
            self.epw - 2 * PAD, line_h, text,
            fill=bool(bg), new_x="LMARGIN", new_y="NEXT",
        )

    def bloc(self, titre, conseil, education="", bg=(232, 245, 233)):
        self._padded_multicell(
            titre, line_h=7,
            font=("DjB", "", 10), color=(30, 80, 30), bg=bg,
        )
        self._padded_multicell(
            f"Conseil : {conseil}", line_h=6,
            font=("Dj", "", 10), color=(40, 40, 40), bg=bg,
        )
        if education:
            self._padded_multicell(
                f"Info : {education}", line_h=6,
                font=("DjI", "", 9), color=(70, 100, 70), bg=bg,
            )
        self.set_text_color(0, 0, 0)
        self.ln(3)


def generer_rapport(data, analyse, nom_fichier=None):
    if nom_fichier is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_fichier = f"rapports/rapport_aquaterra_{ts}.pdf"

    folder = os.path.dirname(nom_fichier)
    if folder:
        os.makedirs(folder, exist_ok=True)

    pdf = RapportAquaterra()
    pdf.set_margins(15, 15, 15)
    pdf.add_font("Dj",  "", FONT_R)
    pdf.add_font("DjB", "", FONT_B)
    pdf.add_font("DjI", "", FONT_I)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.set_font("Dj", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, f"Date d'analyse : {data.get('timestamp', '')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Profil du champ : {data.get('profil', 'Standard')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # 1. Capteurs
    pdf.section("1. Donnees des Capteurs")
    for label, val in [
        ("Temperature",     f"{data['temperature']} C"),
        ("Humidite du sol", f"{data['humidity']} %"),
        ("pH du sol",       str(data['ph'])),
        ("Precipitations",  f"{data['rainfall']} mm"),
        ("Azote (N)",       str(data['N'])),
        ("Phosphore (P)",   str(data['P'])),
        ("Potassium (K)",   str(data['K'])),
    ]:
        pdf.info(label, val)

    # 2. Irrigation
    pdf.section("2. Analyse de l'Irrigation")
    irr = analyse["irrigation"]
    clr = {
        "CRITIQUE": (220, 53,  69),
        "BAS":      (255, 140,   0),
        "OPTIMAL":  ( 40, 167,  69),
        "EXCES":    ( 23, 162, 184),
    }
    pdf.set_font("DjB", "", 11)
    pdf.set_text_color(*clr.get(irr["statut"], (100, 100, 100)))
    pdf.cell(0, 8, f"  Statut : {irr['statut']}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    if irr["litres"] > 0:
        pdf.info("Volume requis", f"{irr['litres']} L/m2")
    bg_irr = (
        (255, 235, 238) if irr["statut"] == "CRITIQUE" else
        (255, 243, 224) if irr["statut"] == "BAS" else
        (232, 245, 233)
    )
    pdf.bloc("Conseil d'irrigation", irr["conseil"], irr["education"], bg=bg_irr)

    # 3. pH
    pdf.section("3. Analyse du pH du Sol")
    ph = analyse["ph"]
    pdf.set_font("DjB", "", 11)
    pdf.set_text_color(*clr.get(ph["statut"], (100, 100, 100)))
    pdf.cell(0, 8, f"  Statut : {ph['statut']}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    bg_ph = (255, 243, 224) if ph["statut"] in ["ACIDE", "ALCALIN"] else (232, 245, 233)
    pdf.bloc("Conseil pH", ph["conseil"], ph["education"], bg=bg_ph)

    # 4. Nutriments
    pdf.section("4. Analyse des Nutriments")
    for n in analyse["nutriments"]:
        bg_n = (255, 243, 224) if n["statut"] == "BAS" else (232, 245, 233)
        pdf.bloc(
            f"{n['nutriment']} - Valeur : {n['valeur']} - Statut : {n['statut']}",
            n["conseil"], n["education"], bg=bg_n,
        )

    # 5. Culture
    pdf.section("5. Culture Recommandee par l'IA")
    culture = analyse["culture"]
    pdf.set_font("DjB", "", 14)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 10, f"  {culture['culture_fr'].upper()}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Dj", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 7, f"  Niveau de confiance : {culture['confiance']}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # 6. Guide éducatif
    pdf.section("6. Guide Educatif - Comprendre Votre Sol", couleur=(21, 101, 192))
    guides = [
        (
            "Pourquoi l'humidite est-elle importante ?",
            "L'eau transporte les nutriments dans la plante. Sans eau, la photosynthese s'arrete "
            "et la plante entre en stress. Maintenir un sol a 50-70% d'humidite garantit une "
            "croissance optimale.",
        ),
        (
            "Le role du pH dans la nutrition vegetale",
            "Le pH conditionne la solubilite des elements nutritifs. Hors de la zone 5.5-7.5, "
            "des nutriments deviennent indisponibles meme s'ils sont presents dans le sol en "
            "grande quantite.",
        ),
        (
            "NPK : les trois piliers de la fertilite",
            "L'Azote (N) construit les proteines et la chlorophylle. Le Phosphore (P) developpe "
            "les racines et transfert l'energie (ATP). Le Potassium (K) regule les echanges "
            "cellulaires et renforce les defenses naturelles.",
        ),
        (
            "L'intelligence artificielle au service de l'agriculture",
            "Le modele Aquaterra a ete entraine sur des milliers de donnees agricoles. Il "
            "identifie des correlations invisibles a l'oeil humain et formule des recommandations "
            "basees sur des preuves scientifiques.",
        ),
    ]
    for titre_g, texte_g in guides:
        pdf._padded_multicell(
            titre_g, line_h=7,
            font=("DjB", "", 10), color=(21, 101, 192),
        )
        pdf._padded_multicell(
            texte_g, line_h=6,
            font=("Dj", "", 9), color=(50, 50, 50),
        )
        pdf.ln(3)

    pdf.output(nom_fichier)
    return nom_fichier
