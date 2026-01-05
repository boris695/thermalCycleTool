
import os
from log import print_log
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


def draw_header(ax_header, logo_path=None, title_str=""):
    ax_header.axis("off")  # pas d'axes visibles
    ax_header.set_xlim(0, 1)
    ax_header.set_ylim(0, 1)

    # Logo (optionnel)
    if logo_path and os.path.exists(logo_path):
        try:
            img = mpimg.imread(logo_path)
            oi = OffsetImage(img, zoom=0.75)
            ab = AnnotationBbox(
                oi, (0.06, 0.92),
                frameon=False,
                xycoords=ax_header.transAxes,
                box_alignment=(0, 1)  # ancre le coin supérieur gauche du logo au point
            )
            ax_header.add_artist(ab)
        except Exception as e:
            print_log(f"Logo non exploitable: {e}", "WARN")

    # Lignes du template
    ax_header.text(0.50, 0.80, "FABRICATION DE FOND DE CUVE A CHAUD OU A FROID", fontsize=12, fontweight='bold', va='top', ha='left', transform=ax_header.transAxes)
    ax_header.text(0.50, 0.65, "RAITEMENT THERMIQUE", fontsize=12, fontweight='bold', va='top', ha='left', transform=ax_header.transAxes)
    ax_header.text(0.50, 0.50, "GRENAILLAGE, SABLAGE, PEINTURE INDUSTRIELLE", fontsize=12, fontweight='bold', va='top', ha='left', transform=ax_header.transAxes)
    
    # Ligne de séparation + titre du cycle
    #ax_header.axhline(y=0.20, xmin=0.02, xmax=0.98, color="#999999", linewidth=1.5)
  

def draw_thermal_plot(ax_plot, all_times, all_temps, labels, colors, title_str=""):
    """
    Dessine le graphe thermique dans l'axe 'ax_plot'.
    """
    import matplotlib.dates as mdates

    ax_plot.set_title(title_str, fontsize=14)
    for i, (times, temps) in enumerate(zip(all_times, all_temps)):
        ax_plot.plot(times, temps, color=colors[i % len(colors)], linewidth=0.9, label=labels[i])

    ax_plot.set_xlabel("Heure", fontsize=12)
    ax_plot.set_ylabel("Température (°C)", fontsize=12)
    ax_plot.grid(True)
    ax_plot.legend()
    ax_plot.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))


def draw_footer(ax_footer):
    """
    Footer en bas de page : ligne de séparation + 3 zones de texte (gauche/centre/droite).
    """
    ax_footer.axis("off")
    ax_footer.set_xlim(0, 1)
    ax_footer.set_ylim(0, 1)

    # Séparation
    #ax_footer.axhline(y=0.95, xmin=0.02, xmax=0.98, color="#999999", linewidth=1.2)

    # Texte (en axes coords)
    # Centre
    ax_footer.text(0.50, 0.80, "BENIERE PERRIN", fontsize=12, fontweight='bold', ha='center', va='top', transform=ax_footer.transAxes)
    ax_footer.text(0.50, 0.55, "Place Neyrand, BP12 - 42420 Lorette", fontsize=12, ha='center', va='top', transform=ax_footer.transAxes)
    ax_footer.text(0.50, 0.30, "42420 Lorette, France", fontsize=12, ha='center', va='top', transform=ax_footer.transAxes)
    
    y =0.05
    ax_footer.text(0.50, y, "    TEL : +33 (0) 4 77 73 24 75 / Email :", fontsize=12, ha='right', va='top', transform=ax_footer.transAxes)
    ax_footer.annotate(
    " contact@beniere-perrin.com",  # garde un espace initial pour l'écart visuel
    xy=(0.50, y), xytext=(0.50, y),
    xycoords=ax_footer.transAxes, textcoords=ax_footer.transAxes,
    ha='left', va='top',
    fontsize=12, color="#1a73e8",
    url="mailto:contact@beniere-perrin.com",
    annotation_clip=False
)

