"""Voix off COMMENTÉE (TTS-safe) — calée sur la vraie partie (temps réel, endgame).
Angle : on lui a donné un TOUT PETIT cerveau → elle n'est pas performante, MAIS on
voit qu'elle a compris une chose concrète : éviter les tirs. Le jeu accélère et
finit par la dépasser. Adaptations mots-pièges : « IA » → « intelligence
artificielle », chiffres en lettres, pas d'em-dash. Caption affichée = ce texte.
"""
SEGMENTS = [
    # 0-6s : hook — l'accélération (honnête), pas « truqué »
    ("hook0", "Ce jeu accélère jusqu'à ce que tu perdes. Alors j'ai lâché une intelligence artificielle dessus."),
    # 6-15s : ce qu'elle voit + le petit cerveau
    ("reveal1", "Elle ne voit pas d'aliens. Elle voit ceci. Dix nombres, soixante fois par seconde. "
                "Et je lui ai donné un tout petit cerveau."),
    # 15-23s : la SEULE chose que ce petit cerveau a comprise = éviter les tirs
    ("obs2", "Ce cerveau minuscule a compris une chose. Éviter les tirs. "
             "Regarde-la. Elle les voit venir, à gauche, à droite, et elle se décale."),
    # 23-31s : le nugget accélération, la vitesse monte à l'écran
    ("twist3", "Mais le jeu accélère. Moins il reste d'aliens, plus ça va vite. C'est le piège."),
    # 31-38s : l'interrogation d'auteur
    ("quest4", "Alors quand elle esquive, pile au bon moment, est-ce qu'elle a compris ? "
               "Ou est-ce qu'un nombre a juste dépassé un autre ?"),
    # 38-46s : la nuance honnête — pas performante, mais elle tient
    ("tension5", "Elle n'est pas très forte. Son cerveau est minuscule. "
                 "Mais elle tient. Une esquive après l'autre."),
    # 47-56s : une poignée (7->5) ; les ALIENS accélèrent (0.89, presque max) — PAS de scrolling
    ("last6", "Il n'en reste qu'une poignée. Mais ils foncent, presque à pleine vitesse maintenant. "
              "Et elle esquive encore, à ce rythme."),
    # 57-68s : les derniers (5->3) descendent trop bas → INVASION → bascule + chute (BOUCLE le hook)
    ("final7", "Et à la fin, les derniers descendent trop bas, trop vite. Elle n'a jamais été forte. "
               "Elle avait juste compris qu'il fallait éviter les tirs. Alors dis-moi : elle joue, ou elle calcule ?"),
]
