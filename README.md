# Space Invaders — voir l'intérieur du modèle

Épisode « IA × jeu vidéo » : une IA joue à Space Invaders, et on **visualise en
direct son réseau de neurones** qui décide. Fil rouge (essai) : elle ne voit pas
d'aliens, elle voit des **nombres** — décide-t-elle vraiment, ou empile-t-elle des
chiffres ? Et le jeu, conçu pour accélérer sans fin, finit toujours par la déborder.

## Le jeu (`env.py`)
Space Invaders headless en numpy, fidèle : formation qui balaie / descend /
**accélère** quand il reste moins d'aliens, tirs ennemis, **bunkers destructibles**
qui bloquent les tirs, invasion. Vitesse des projectiles **constante** (seuls les
aliens accélèrent).

## L'agent (`agent.py`, `train_bc.py`, `evolve.py`)
Petit MLP **[10, 9, 9, 4]** — assez petit pour qu'on voie *dedans*. Entrées
interprétables : `cible G/D`, `bloqué`, `bombe G/D` (menace + imminence),
`canon`, `abri`, `menace`, `vies`, `vitesse` → 4 actions `GAUCHE/DROITE/TIR/RIEN`.
Entraîné par **behavior cloning** d'une stratégie experte, puis affiné par
**neuroévolution**. Leçon clé : la perception (ce qu'on lui donne à voir) compte
plus que la taille du réseau — donner les tirs ennemis correctement l'a fait
passer de ~0,5 à ~2,6 vagues nettoyées (jusqu'à 7).

## Le rendu (`build.py`, via [studio](https://github.com/Gwyrm/studio))
Compo 9:16 « arcade CRT × instrument » : le jeu en haut, le **réseau qui s'allume**
en bas (primitive `motion.neural_net`). Voix off commentée + captions. Montage en
**temps réel**.

```bash
python train_bc.py && python evolve.py 35   # entraîne -> best.npz
python render_agent.py                       # aperçu agent + réseau
python build.py                              # montage final (voix requise dans runs/voice)
```
