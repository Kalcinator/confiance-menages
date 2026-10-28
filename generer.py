# /// script
# requires-python = ">=3.10"
# ///
"""Parse la série Insee 001587668 (texte lire-web) et écrit la page HTML autonome.

Les repères (reperes.json, à côté du modèle) sont insérés dans le modèle ; chaque date doit exister dans la série.
"""
import json, re, sys
from pathlib import Path

raw, out, modele = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
M = {"Janvier":1,"Février":2,"Mars":3,"Avril":4,"Mai":5,"Juin":6,"Juillet":7,"Août":8,"Septembre":9,"Octobre":10,"Novembre":11,"Décembre":12}
rows = {}
for l in raw.read_text(encoding="utf-8").splitlines():
    m = re.match(r"\| (\d{4}) \| (\w+) \| (?:\(\w\) )?(\d+) \|", l)
    if m and m.group(2) in M:
        rows[(int(m.group(1)), M[m.group(2)])] = int(m.group(3))
keys = sorted(rows)
# contrôles : mensuel continu, bornes, valeurs clés
assert keys[0] == (1972, 10) and keys[-1] == (2026, 10), (keys[0], keys[-1])
exp = [(y, m) for y in range(1972, 2027) for m in range(1, 13) if (1972, 10) <= (y, m) <= (2026, 10)]
assert keys == exp, "mois manquants"
assert rows[(2026,10)] == 80 and rows[(2026,9)] == 85 and rows[(2013,6)] == 80
assert min(v for k, v in rows.items() if k > (2013, 6)) == 80 and rows[(2026,10)] == 80
assert all(v > 80 for k, v in rows.items() if (2013, 6) < k < (2026, 10)), "un mois entre 2013-06 et 2026-10 est <= 80"
data = [[y, m, rows[(y, m)]] for y, m in keys]

# repères : chaque date doit exister dans la série
reperes = json.loads((modele.parent / "reperes.json").read_text(encoding="utf-8"))
for r in reperes:
    assert (r["mois"][0], r["mois"][1]) in rows, f"repère absent de la série : {r['mois']}"

# écart minimal entre repères à 390 px, avec la formule de la page :
# largeur 390 - 2 x 16 (main) - 2 x 12 (carte) - 2 (bordures) = 332 ; marges gauche 36, droite 44 (petit écran)
W, ml, mr = 390 - 2*16 - 2*12 - 2, 36, 44
T = lambda y, m: y + (m-1)/12
x0, x1 = T(1972, 10), T(2026, 10)
xs = sorted(ml + (T(*r["mois"]) - x0)/(x1 - x0)*(W-ml-mr) for r in reperes)
gap = min(b-a for a, b in zip(xs, xs[1:]))
labels = gap >= 18
print(f"repères : {len(reperes)} ; écart minimal à 390 px : {gap:.1f} px ; numéros sur la courbe : {'oui' if labels else 'non, détail dans la liste'}")

tpl = modele.read_text(encoding="utf-8")
assert "__DATA__" in tpl and "__REP__" in tpl and "__LABELS__" in tpl, "modèle incomplet"
html = (tpl.replace("__DATA__", json.dumps(data, separators=(",", ":")))
           .replace("__REP__", json.dumps(reperes, ensure_ascii=False, separators=(",", ":")))
           .replace("__LABELS__", "true" if labels else "false"))
out.write_text(html, encoding="utf-8")
print(len(data), "points ; min", min(rows.values()), "max", max(rows.values()))
