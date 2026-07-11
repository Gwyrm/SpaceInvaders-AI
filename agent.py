"""MLP compact [7,9,9,4] (numpy) — l'agent qu'on ENTRAÎNE et qu'on VISUALISE.

`layer_acts()` renvoie les activations par couche (pour le viz réseau), `.W` les
matrices de poids (pour les connexions), `to_vector`/`from_vector` pour la
neuroévolution (202 paramètres). Sortie = softmax ; décision = argmax.
"""
import numpy as np

ARCH = [10, 9, 9, 4]
SHAPES = [(10, 9), (9, 9), (9, 4)]


def _softmax(z):
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


class MLP:
    def __init__(self, params=None, rng=None):
        if params is None:
            rng = rng or np.random.default_rng()
            self.from_vector(rng.normal(0, 0.5, self.n_params()))
        else:
            self.from_vector(np.asarray(params, dtype=float))

    @staticmethod
    def n_params():
        return sum(a * b + b for a, b in SHAPES)

    def from_vector(self, v):
        self.Wl, self.bl, i = [], [], 0
        for a, b in SHAPES:
            self.Wl.append(v[i:i + a * b].reshape(a, b)); i += a * b
            self.bl.append(v[i:i + b]); i += b
        return self

    def to_vector(self):
        out = []
        for Wm, bm in zip(self.Wl, self.bl):
            out.append(Wm.ravel()); out.append(bm)
        return np.concatenate(out)

    @property
    def W(self):
        return self.Wl

    def _forward(self, x):
        h1 = np.tanh(x @ self.Wl[0] + self.bl[0])
        h2 = np.tanh(h1 @ self.Wl[1] + self.bl[1])
        o = h2 @ self.Wl[2] + self.bl[2]
        return h1, h2, o

    def layer_acts(self, x):
        x = np.asarray(x, dtype=float)
        h1, h2, o = self._forward(x)
        return [x, (h1 + 1) / 2, (h2 + 1) / 2, _softmax(o)]

    def act(self, x):
        _, _, o = self._forward(np.asarray(x, dtype=float))
        return int(np.argmax(o))

    def save(self, path):
        np.savez(path, v=self.to_vector())

    @classmethod
    def load(cls, path):
        return cls(params=np.load(path)["v"])
