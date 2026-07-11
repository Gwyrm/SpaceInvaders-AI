"""Voix off COMMENTÉE (TTS-safe) — calée sur la vraie partie seed 4 (temps réel).
Chaque beat commente ce qui se passe à l'écran à cet instant (voir timeline).
Adaptations mots-pièges : « IA » → « intelligence artificielle », chiffres en
lettres, pas d'em-dash. Le texte affiché en caption = ce texte (audio-sync).
"""
SEGMENTS = [
    # 0-6s : hook
    ("hook0", "Ce jeu est truqué pour que tu perdes. Alors j'ai lâché une intelligence artificielle dessus."),
    # 6-15s : ce qu'elle voit
    ("reveal1", "Elle joue à Space Invaders. Mais elle ne voit pas d'aliens. "
                "Elle voit ceci. Dix nombres, et un choix, soixante fois par seconde."),
    # 15-22s : commente son skill — elle esquive (le déclic des tirs ennemis en entrée)
    ("obs2", "Regarde-la esquiver. Elle voit les tirs arriver, à gauche, à droite. "
             "Et elle se décale, pile à temps."),
    # 22-31s : le nugget, la vitesse monte à l'écran
    ("twist3", "Mais il y a un piège. Ce chiffre, la vitesse, monte. "
               "Plus elle gagne, plus le jeu accélère. Exprès."),
    # 31-38s : l'interrogation
    ("quest4", "Alors quand elle se décale, pile au bon moment, est-ce qu'elle a compris ? "
               "Ou est-ce qu'un nombre a juste dépassé un autre ?"),
    # 38-46s : la tension (une seule vie, ça accélère) — robuste au timing
    ("tension5", "Une seule vie, maintenant. Et le jeu ne fait qu'accélérer. "
                 "Elle ne panique pas. Elle ne sait pas paniquer."),
    # 46-53s : le dernier alien (~49s), vitesse max
    ("last6", "Plus qu'un seul alien. Le jeu est à fond, maintenant. "
              "Elle ne ralentit pas. Elle ne peut pas."),
    # 53-61s : la vitesse la dépasse → invasion → bascule + chute
    ("final7", "Et la vitesse finit par la dépasser. Elle n'a jamais su qu'elle jouait. "
               "Ni qu'elle allait perdre. Et si c'était cela, jouer ?"),
]
