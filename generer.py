# /// script
# requires-python = ">=3.10"
# ///
"""Parse la série Insee 001587668 (texte lire-web) et écrit la page HTML autonome."""
import json, re, sys
from pathlib import Path

raw, out = Path(sys.argv[1]), Path(sys.argv[2])
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
tpl = Path(sys.argv[3]).read_text(encoding="utf-8")
out.write_text(tpl.replace("__DATA__", json.dumps(data, separators=(",", ":"))), encoding="utf-8")
print(len(data), "points ; min", min(rows.values()), "max", max(rows.values()))
