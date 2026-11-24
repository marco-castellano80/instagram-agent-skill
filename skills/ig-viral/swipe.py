#!/usr/bin/env python3
"""
swipe.py - ordena los reels que has recogido según cuánto superaron a su
propia cuenta, pone nombre a la fórmula de gancho de cada uno y escribe el
archivo de referencias (swipe file).

La idea es una sola corrección: las visualizaciones brutas no son una prueba.
Una cuenta de 2.000.000 de seguidores que hace 400.000 tuvo un día tranquilo.
Una cuenta de 4.000 seguidores que hace 400.000 encontró algo. Esto ordena por
el múltiplo sobre la referencia de la propia cuenta, que es la única versión
de "se hizo viral" que te dice algo que puedas copiar.

La entrada es un archivo separado por tabuladores que rellenas mientras
navegas, un reel por fila, con una cabecera que nombra las columnas (en
español o en inglés):

    cuenta    seguidores   mediana   vistas    gancho
    @alguien  48000        11000     412000    nadie te dice que tus primeros 30 fracasan

`mediana` son las visualizaciones típicas recientes de esa cuenta y es la
mejor referencia. Si solo tienes `seguidores`, deja la mediana fuera y el
script lo dirá. `gancho` es la primera línea del reel, hablada o en pantalla,
con sus palabras. Las cifras admiten "412.000", "412,000", "412K", "412 mil",
"1,2 M" o "1.2M".

Uso
  python3 swipe.py capturados.tsv
  python3 swipe.py capturados.tsv --out ~/.claude/instagram/swipe.md
  python3 swipe.py capturados.tsv --json
  python3 swipe.py captured.tsv --lang en      # fórmulas y mensajes en inglés

Idioma: --lang es (por defecto) usa ig-reel/hooks.es.json; --lang en usa
ig-reel/hooks.json. También vale la variable de entorno IG_LANG.
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata

LANGS = ("es", "en")
DEFAULT_LANG = os.environ.get("IG_LANG", "es") if os.environ.get("IG_LANG") in LANGS else "es"

HERE = os.path.dirname(os.path.abspath(__file__))
HOOKS = {
    "es": os.path.join(HERE, "..", "ig-reel", "hooks.es.json"),
    "en": os.path.join(HERE, "..", "ig-reel", "hooks.json"),
}
WORD_RE = re.compile(r"[\w$€£%'’-]+")

try:                                              # opcional: puntuar también los ganchos
    sys.path.insert(0, os.path.join(HERE, "..", "ig-reel"))
    from hookscore import run as score_hook       # noqa: E402
except Exception:                                 # ig-viral copiado por separado
    score_hook = None

# Cabeceras aceptadas -> nombre interno.
COLUMNS = {
    "account": "account", "cuenta": "account", "handle": "account", "usuario": "account",
    "followers": "followers", "seguidores": "followers",
    "median": "median", "mediana": "median",
    "views": "views", "vistas": "views", "visualizaciones": "views",
    "reproducciones": "views", "visitas": "views",
    "hook": "hook", "gancho": "hook",
    "on-screen": "on_screen", "pantalla": "on_screen", "en pantalla": "on_screen",
    "length": "length", "duracion": "length",
    "cta": "cta",
}

MSG = {
    "en": {
        "head": "SWIPE FILE  ·  {n} reels  ·  {a} accounts  ·  baseline: {b}",
        "base_median": "account median", "base_followers": "follower count",
        "working": "WHAT IS WORKING IN THIS BATCH",
        "top_formulas": "  top third by outlier:  ",
        "hook_scores": "  median hook score:     top {t:.0f}  vs bottom {b:.0f}",
        "hook_len": "  median hook length:    top {t} words  vs bottom {b} words",
        "unclassified": "  unclassified:          {u} of {n}. Read those by hand, they are where a "
                        "formula you do not have yet is hiding.",
        "caveat": "\n  A hand-collected batch is evidence, not proof. Twelve reels shows you "
                  "nothing;\n  forty across six accounts shows you something. Collect more before "
                  "you believe it.\n",
        "unclassified_name": "unclassified",
        "hook": "hook",
        "md_title": "# Swipe file",
        "md_intro": "{n} reels across {a} accounts. Ranked by multiple over {b}.",
        "md_views": "- views: {v}  baseline: {b}",
        "md_score": "- hook score: {s}  words: {w}",
        "md_hook": "- hook: \"{h}\"",
        "no_rows": "no usable rows. Need a tab-separated file with at least views and hook.",
        "no_hooks": "note: hooks file not found, formulas not named. Pass --hooks.",
        "no_score": "note: hookscore.py not importable, hook scores skipped.",
        "wrote": "wrote {p}",
    },
    "es": {
        "head": "SWIPE FILE  ·  {n} reels  ·  {a} cuentas  ·  referencia: {b}",
        "base_median": "mediana de la cuenta", "base_followers": "número de seguidores",
        "working": "QUÉ ESTÁ FUNCIONANDO EN ESTE LOTE",
        "top_formulas": "  tercio superior:        ",
        "hook_scores": "  nota mediana gancho:    arriba {t:.0f}  frente a abajo {b:.0f}",
        "hook_len": "  longitud mediana:       arriba {t} palabras  frente a abajo {b} palabras",
        "unclassified": "  sin clasificar:         {u} de {n}. Léelos a mano: ahí se esconde una "
                        "fórmula que todavía no tienes.",
        "caveat": "\n  Un lote recogido a mano es un indicio, no una prueba. Doce reels no te "
                  "enseñan nada;\n  cuarenta en seis cuentas te enseñan algo. Recoge más antes de "
                  "creértelo.\n",
        "unclassified_name": "sin clasificar",
        "hook": "gancho",
        "md_title": "# Swipe file",
        "md_intro": "{n} reels de {a} cuentas. Ordenados por múltiplo sobre {b}.",
        "md_views": "- visualizaciones: {v}  referencia: {b}",
        "md_score": "- nota del gancho: {s}  palabras: {w}",
        "md_hook": "- gancho: \"{h}\"",
        "no_rows": "no hay filas utilizables. Hace falta un archivo separado por tabuladores con, "
                   "como mínimo, vistas y gancho.",
        "no_hooks": "nota: no se encontró el archivo de fórmulas, no se nombran. Usa --hooks.",
        "no_score": "nota: no se pudo importar hookscore.py, se omiten las notas de gancho.",
        "wrote": "escrito {p}",
    },
}


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")


def parse_count(raw):
    """'412.000', '412,000', '412K', '412 mil', '1,2 M', '1.2M' -> int."""
    if not raw:
        return None
    s = fold(raw).replace(" ", "").replace(" ", "")
    m = re.fullmatch(r"(\d+(?:[.,]\d+)?)(k|mil|m|mill|millones|mm)?", s)
    if m and m.group(2):
        num = float(m.group(1).replace(",", "."))
        mult = 1000 if m.group(2) in ("k", "mil") else 1000000
        return int(round(num * mult))
    digits = re.sub(r"[^\d]", "", s)
    return int(digits) if digits else None


def load_formulas(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None, False
    by_id = {h["id"]: h for h in d["hooks"]}
    order = d.get("classify_order") or sorted(by_id)
    formulas = [(by_id[i]["id"], by_id[i]["name"],
                 re.compile(by_id[i]["match"], re.IGNORECASE)) for i in order if i in by_id]
    return formulas, bool(d.get("normalize"))


def classify(hook, formulas, normalize, unclassified):
    if not formulas:
        return None, unclassified
    text = fold(hook) if normalize else hook
    for fid, name, pattern in formulas:
        if pattern.search(text):
            return fid, name
    return None, unclassified


def read_rows(path):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    lines = [l for l in raw.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    if not lines:
        return []
    head = [COLUMNS.get(fold(c.strip()), fold(c.strip())) for c in lines[0].split("\t")]
    if "views" in head and "hook" in head:
        cols, body = head, lines[1:]
    else:
        cols, body = ["account", "followers", "views", "hook"], lines
    rows = []
    for line in body:
        cells = line.split("\t")
        if len(cells) < len(cols):
            cells += [""] * (len(cols) - len(cells))
        r = dict(zip(cols, [c.strip() for c in cells]))
        r["views"] = parse_count(r.get("views", "")) or 0
        for k in ("followers", "median"):
            r[k] = parse_count(r.get(k, "") or "")
        if r["views"] and r.get("hook"):
            rows.append(r)
    return rows


def analyse(rows, formulas, normalize, lang):
    m = MSG[lang]
    used_median = any(r.get("median") for r in rows)
    for r in rows:
        base = r.get("median") or r.get("followers") or 0
        r["baseline"] = base
        r["outlier"] = round(r["views"] / base, 2) if base else None
        r["formula_id"], r["formula"] = classify(r["hook"], formulas, normalize,
                                                 m["unclassified_name"])
        r["words"] = len(WORD_RE.findall(r["hook"]))
        if score_hook:
            _, overall, verdict, _ = score_hook(r["hook"], lang)
            r["hook_score"], r["hook_verdict"] = round(overall, 1), verdict
        else:
            r["hook_score"], r["hook_verdict"] = None, None
    ranked = sorted(rows, key=lambda r: -(r["outlier"] or 0))
    third = max(1, len(ranked) // 3)
    top, bottom = ranked[:third], ranked[-third:]

    def med(items, key):
        vals = [i[key] for i in items if i.get(key) is not None]
        return round(statistics.median(vals), 1) if vals else None

    counts = {}
    for r in top:
        counts[r["formula"]] = counts.get(r["formula"], 0) + 1
    return {
        "lang": lang,
        "baseline": m["base_median"] if used_median else m["base_followers"],
        "n": len(ranked),
        "accounts": len({r.get("account", "") for r in ranked}),
        "reels": ranked,
        "top_formulas": sorted(counts.items(), key=lambda kv: -kv[1]),
        "top_hook_score": med(top, "hook_score"),
        "bottom_hook_score": med(bottom, "hook_score"),
        "top_words": med(top, "words"),
        "bottom_words": med(bottom, "words"),
        "unclassified": sum(1 for r in ranked if r["formula_id"] is None),
    }


def thousands(n, lang):
    s = f"{n:,}"
    return s.replace(",", ".") if lang == "es" else s


def render(a, out=sys.stdout):
    lang = a["lang"]
    m = MSG[lang]
    head = m["head"].format(n=a["n"], a=a["accounts"], b=a["baseline"])
    print("\n" + head, file=out)
    print("=" * max(len(head), 78), file=out)
    for r in a["reels"]:
        mult = f"{r['outlier']:.1f}x" if r["outlier"] else "   ?"
        score = f"{r['hook_score']:.0f}" if r["hook_score"] is not None else " -"
        fid = f"#{r['formula_id']:<2}" if r["formula_id"] else "-  "
        print(f"  {mult:>7}  {m['hook']} {score:>3}  {fid} {r['formula'][:22]:<22} "
              f"{r.get('account', '')[:16]:<16} {thousands(r['views'], lang):>9}", file=out)
        print(f"           \"{r['hook'][:96]}\"", file=out)
    print("-" * max(len(head), 78), file=out)
    print(m["working"], file=out)
    if a["top_formulas"]:
        print(m["top_formulas"] + ", ".join(f"{n} x{c}" for n, c in a["top_formulas"][:4]),
              file=out)
    if a["top_hook_score"] is not None:
        print(m["hook_scores"].format(t=a["top_hook_score"], b=a["bottom_hook_score"]), file=out)
    print(m["hook_len"].format(t=a["top_words"], b=a["bottom_words"]), file=out)
    print(m["unclassified"].format(u=a["unclassified"], n=a["n"]), file=out)
    print(m["caveat"], file=out)


def to_markdown(a):
    lang = a["lang"]
    m = MSG[lang]
    lines = [m["md_title"], "", m["md_intro"].format(n=a["n"], a=a["accounts"], b=a["baseline"]),
             ""]
    for r in a["reels"]:
        mult = f"{r['outlier']:.1f}x" if r["outlier"] else "?"
        lines += [f"## {mult}  {r['formula']}  ({r.get('account', '')})",
                  m["md_views"].format(v=thousands(r["views"], lang),
                                       b=thousands(r["baseline"], lang)),
                  m["md_score"].format(s=r["hook_score"], w=r["words"]),
                  m["md_hook"].format(h=r["hook"]), ""]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Ordena reels recogidos por múltiplo sobre su cuenta.")
    ap.add_argument("input", nargs="?", default="-", help="archivo TSV, o - para stdin")
    ap.add_argument("--lang", choices=LANGS, default=DEFAULT_LANG,
                    help=f"idioma de las fórmulas y los mensajes (por defecto {DEFAULT_LANG})")
    ap.add_argument("--hooks", help="ruta a un archivo de fórmulas (por defecto según --lang)")
    ap.add_argument("--out", help="escribe también el swipe file en markdown aquí")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    lang = args.lang
    m = MSG[lang]

    rows = read_rows(args.input)
    if not rows:
        print(m["no_rows"], file=sys.stderr)
        sys.exit(2)
    formulas, normalize = load_formulas(args.hooks or HOOKS[lang])
    a = analyse(rows, formulas, normalize, lang)
    if not formulas:
        print(m["no_hooks"], file=sys.stderr)
    if score_hook is None:
        print(m["no_score"], file=sys.stderr)

    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    if args.out:
        path = os.path.expanduser(args.out)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(to_markdown(a))
        print(m["wrote"].format(p=path), file=sys.stderr)


if __name__ == "__main__":
    main()
