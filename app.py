from flask import Flask, render_template, request, send_file
from werkzeug.utils import safe_join
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import os
from time import time
import webbrowser
import threading
import sys
import json
from log import print_log
from graph import draw_footer, draw_thermal_plot, draw_header
import matplotlib.gridspec as gridspec
import matplotlib.image as mpimg


def load_config():
    path = resource_path("config.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

config = load_config()
APP_VERSION = config["version"]
APP_NAME = config["app_name"]
PORT = config["default_port"]
BROWSER_DELAY = config["default_browser_delay"]
TEST_MODE = config.get("test", False)
timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")




# Logo optionnel : placez un fichier 'static/logo.png' si vous en avez un.
# Sinon, laissez LOGO_PATH = None (le code gère l'absence de logo).
try:
    LOGO_PATH = resource_path("static/logo.png")
    if not os.path.exists(LOGO_PATH):
        LOGO_PATH = None
except Exception:
    LOGO_PATH = None


print_log(f"******************************************************************************", "TITLE")
print_log(f"******************************************************************************", "TITLE")
print_log(f"***********************  Démarrage de l'application   ************************", "TITLE")
print_log(f"***********************  NOM : {APP_NAME}       ************************", "TITLE")
print_log(f"***********************  VERSION : {APP_VERSION}              ************************", "TITLE")
print_log(f"***********************  DATE : {timestamp}   ************************", "TITLE")
print_log(f"***********************  TEST MODE : {TEST_MODE}             ************************", "TITLE")
print_log(f"******************************************************************************", "TITLE")
print_log(f"******************************************************************************", "TITLE")
app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static")
)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:PORT".replace("PORT", str(PORT)))


def hhmm_to_seconds(s):
    try:
        h, m = map(int, s.split(":"))
        return h * 3600 + m * 60
    except Exception:
        return 0


    
@app.route("/", methods=["GET", "POST"])
def index():
    global download_name_str
    image_generated = False
    if request.method == "POST":
        try:
            # Récupération des paramètres
            print_log(f"Génération du graphique", "INFO")
            date_str = request.form.get("date", datetime.today().strftime("%Y-%m-%d"))
            nom_client = request.form.get("nom_client")
            numero_commande = request.form.get("numero_commande")
            nom_four = request.form.get("nom_four")
            heure_depart_str = request.form[f"heure_depart"]    
            nb_courbes = int(request.form.get("nb_courbes", 1))
            start_time = datetime.strptime(heure_depart_str, "%H:%M")
            full_date = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=start_time.hour, minute=start_time.minute)
            colors = ['red', 'blue', 'green', 'orange', 'purple']
            fig = plt.figure(figsize=(12, 8)) #avant 12 5
            gs = gridspec.GridSpec(nrows=3, ncols=1, height_ratios=[1, 4, 0.6])  # 1 part header / 3 parts plot
            print_log(f"nom_client :  {nom_client}, numero_commande :  {numero_commande}, nom_four :  {nom_four}, date :  {date_str}, heure_depart :  {heure_depart_str}, nb_courbes :  {nb_courbes}", "INFO")
            ax_header = fig.add_subplot(gs[0])
            ax_plot = fig.add_subplot(gs[1])
            ax_footer = fig.add_subplot(gs[2])

            
            all_times_list = []
            all_temps_list = []
            labels_list = []

            
            for i in range(nb_courbes):
                temp_depart = int(request.form[f"temp_depart_{i}"])
                vitesse_montee = float(request.form[f"vitesse_montee_{i}"])
                temp_cible = int(request.form[f"temp_cible_{i}"])
                duree_palier_str = request.form[f"duree_palier_{i}"]
                vitesse_descente = float(request.form[f"vitesse_descente_{i}"])
                temp_fin = int(request.form[f"temp_fin_{i}"])
                name_str = request.form[f"name_{i}"]
                p1_temp_str   = request.form.get(f"temp_cible_1_palier_{i}", "").strip()
                p1_duree_str  = request.form.get(f"duree_maintien_1_palier_{i}", "").strip()
                p1_vitesse_str= request.form.get(f"vitesse_montee_1_palier_{i}", "").strip()
                has_p1 = bool(p1_temp_str) and bool(p1_duree_str) and bool(p1_vitesse_str)
                print_log(f"Création de la courbe {i+1}", "INFO")
                print_log(f"name :  {name_str}, temp_depart :  {temp_depart}, vitesse_montee :  {vitesse_montee}, duree_palier :  {duree_palier_str}, vitesse_descente :  {vitesse_descente},  temp_fin :  {temp_fin}", "INFO")

                # Parsing
                
                h, m = map(int, duree_palier_str.split(":"))
                palier_seconds = h * 3600 + m * 60
                
                if has_p1:
                    # ---------- Palier intermédiaire présent ----------
                    temp_cible_1       = int(p1_temp_str)
                    vitesse_montee_1   = float(p1_vitesse_str)

                    # Étape 1a - Montée jusqu'au 1er palier
                    delta1 = temp_cible_1 - temp_depart
                    duree1_sec = int((delta1 / max(vitesse_montee_1, 1e-9)) * 3600)
                    ramp1_times = [start_time + timedelta(seconds=t) for t in range(max(duree1_sec, 0))]
                    ramp1_base  = np.linspace(temp_depart, temp_cible_1, max(duree1_sec, 1))
                    ramp1_temps = ramp1_base + np.sin(np.linspace(0, 50 * np.pi, max(duree1_sec, 1)))

                    reach1_time = ramp1_times[-1] if ramp1_times else start_time

                    # Étape 1b - Palier 1 (maintien à temp_cible_1)
                    hold1_times = [reach1_time + timedelta(seconds=t) for t in range(palier_seconds)]
                    hold1_temps = temp_cible_1 + np.sin(np.linspace(0, 60 * np.pi, palier_seconds))

                    # Étape 1c - Montée finale jusqu'à temp_cible (avec vitesse_montee "finale")
                    delta2 = temp_cible - temp_cible_1
                    start2_time = hold1_times[-1] if hold1_times else reach1_time
                    duree2_sec  = int((delta2 / max(vitesse_montee, 1e-9)) * 3600)
                    ramp2_times = [start2_time + timedelta(seconds=t) for t in range(max(duree2_sec, 0))]
                    ramp2_base  = np.linspace(temp_cible_1, temp_cible, max(duree2_sec, 1))
                    ramp2_temps = ramp2_base + np.sin(np.linspace(0, 50 * np.pi, max(duree2_sec, 1)))

                    reach_final_time = ramp2_times[-1] if ramp2_times else start2_time

                    # Étape 2 - Palier final (maintien à temp_cible)
                    hold_times = [reach_final_time + timedelta(seconds=t) for t in range(palier_seconds)]
                    hold_temps = temp_cible + np.sin(np.linspace(0, 60 * np.pi, palier_seconds))

                    # Étape 3 - Descente
                    duree_descente_sec = int(((temp_cible - temp_fin) / max(vitesse_descente, 1e-9)) * 3600)
                    hold_end_time = hold_times[-1] if hold_times else reach_final_time
                    cool_times = [hold_end_time + timedelta(seconds=t) for t in range(max(duree_descente_sec, 0))]
                    cool_base  = np.linspace(temp_cible, temp_fin, max(duree_descente_sec, 1))
                    cool_temps = cool_base + np.sin(np.linspace(0, 40 * np.pi, max(duree_descente_sec, 1)))

                    # Agrégation (avec palier 1)
                    all_times = ramp1_times + hold1_times + ramp2_times + hold_times + cool_times
                    all_temps = np.concatenate([ramp1_temps, hold1_temps, ramp2_temps, hold_temps, cool_temps])

                else:
                    # Étape 1 - montée final 
                    delta_temp = temp_cible - temp_depart
                    duree_montee_sec = int((delta_temp / vitesse_montee) * 3600)
                    ramp_times = [start_time + timedelta(seconds=i) for i in range(duree_montee_sec)]
                    ramp_base = np.linspace(temp_depart, temp_cible, duree_montee_sec)
                    ramp_temps = ramp_base + np.sin(np.linspace(0, 50 * np.pi, duree_montee_sec))

                    # Étape 2 - palier final 
                    reach_temp_time = ramp_times[-1] if ramp_times else start_time
                    hold_times = [reach_temp_time + timedelta(seconds=i) for i in range(palier_seconds)]
                    hold_temps = temp_cible + np.sin(np.linspace(0, 60 * np.pi, palier_seconds))

                    # Étape 3 - descente
                    duree_descente_sec = int(((temp_cible - temp_fin) / vitesse_descente) * 3600)
                    hold_end_time = hold_times[-1] if hold_times else reach_temp_time
                    cool_times = [hold_end_time + timedelta(seconds=i) for i in range(duree_descente_sec)]
                    cool_base = np.linspace(temp_cible, temp_fin, duree_descente_sec)
                    cool_temps = cool_base + np.sin(np.linspace(0, 40 * np.pi, duree_descente_sec))

                    # Agrégation
                    all_times = ramp_times + hold_times + cool_times
                    all_temps = np.concatenate([ramp_temps, hold_temps, cool_temps])
                    label = f"{name_str} - "
                
                all_times_list.append(all_times)
                all_temps_list.append(all_temps)
                labels_list.append(request.form[f"name_{i}"])
                
            title_str = f"Cycle thermique - {nom_client} - {numero_commande} - {nom_four} - {full_date.strftime('%d/%m/%Y')} à {full_date.strftime('%H:%M')}"
            download_name_str = f"{nom_client}_{numero_commande}_{nom_four}_{full_date.strftime('%Y%m%d_%H%M%S')}"
           
            
            draw_header(ax_header, logo_path=LOGO_PATH)
            draw_thermal_plot(ax_plot, all_times_list, all_temps_list, labels_list, colors, title_str)
            draw_footer(ax_footer)
            fig.tight_layout()
            
            
            # Sauvegarde
            print_log(f"Création du dossier static si non existant", "WARN")
            os.makedirs("static", exist_ok=True)
            plt.savefig("static/output.png", dpi=300)
            plt.savefig("static/output.pdf", dpi=300)
            plt.close()
            
            print_log(f"Graphique {title_str} sauvegardé dans static/output", "INFO")
            image_generated = True
        except Exception as e:
            print(e)
            print_log(e, "ERROR")
            return f"Erreur : {str(e)}", 500

    return render_template(
    "index.html",
    image_generated=image_generated,
    timestamp=time(),
    app_name=APP_NAME,
    app_version=APP_VERSION,
    test_mode=TEST_MODE
    )

@app.route("/download/<filetype>")
def download_file(filetype):
    filename_on_disk = safe_join(app.static_folder, f"output.{filetype}")
    if download_name_str:
        download_name =  f"{download_name_str}.{filetype}"
    else:
        download_name = filename_on_disk
    print_log(f"Téléchargement du fichier {download_name}", "INFO")
    return send_file(filename_on_disk, as_attachment=True, download_name=download_name)




if __name__ == "__main__":
    threading.Timer(BROWSER_DELAY, open_browser).start()
    app.run(host="127.0.0.1", port=PORT)