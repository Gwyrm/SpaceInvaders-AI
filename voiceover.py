"""Script + voix off — épisode « Space Invaders : voir l'intérieur du modèle ».

Structure en beats (studio.script) pour lint + timing, et SEGMENTS prêts pour le
TTS/montage. NB : version LISIBLE ici ; l'adaptation TTS (chiffres en lettres,
« IA » → « intelligence artificielle », pas d'em-dash) se fait à la génération voix.
"""
import sys
sys.path.insert(0, "/Users/pierre/Projets/tiktok-ia-playbook")
from studio.script import Script, Beat

SCRIPT = Script([
    Beat("hook", "Ce jeu est truqué pour que tu perdes. Alors j'ai lâché une IA dessus."),
    Beat("promise", "Elle joue à Space Invaders. Sauf qu'elle ne voit pas d'aliens. "
                    "Elle voit ça : neuf nombres, et un choix, soixante fois par seconde."),
    Beat("rise", "Où est la cible. Une bombe qui tombe. C'est tout. "
                 "Gauche, droite, feu : rien que des chiffres."),
    Beat("rise", "Quand elle se glisse pile sous un alien : elle a compris ? "
                 "Ou un nombre a juste dépassé un autre ?"),
    Beat("twist", "Parce que le piège, le voilà. Depuis 1978, ce jeu accélère à chaque "
                  "alien tué. Plus elle gagne, plus il va vite. Il n'a pas de fin."),
    Beat("rise", "Elle continue. Elle nettoie, ça accélère, encore, encore, "
                 "jusqu'à ce qu'elle décroche."),
    Beat("payoff", "Elle n'a pas paniqué. Elle ne savait pas qu'elle jouait. Ni qu'elle "
                   "allait perdre. Juste des nombres, transformés en gestes, jusqu'au dernier."),
    Beat("outro", "Et si c'était ça, jouer ?"),
])

SEGMENTS = [(f"{b.role}{i}", b.text) for i, b in enumerate(SCRIPT.beats)]

if __name__ == "__main__":
    SCRIPT.verify()
    print(f"~{SCRIPT.total_seconds:.0f}s de voix off · {len(SCRIPT.beats)} beats")
