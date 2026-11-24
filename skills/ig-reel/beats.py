#!/usr/bin/env python3
"""
beats.py - convierte un guion de Reel en una escaleta cronometrada antes de
grabarlo.

Calcula cuánto se tarda en decir cada línea, las apila en códigos de tiempo y
marca las cuatro cosas que matan un Reel en la edición: un gancho que pasa de
los tres segundos, un bloque tan largo que el espectador se va, una racha de
líneas sin nada concreto, y una duración total que no cuadra con lo que dijiste
que ibas a hacer.

Los tiempos son una estimación a partir del número de palabras y un ritmo en
palabras por minuto. Sirven para planificar la edición, no para sustituir la
grabación. Fija tu propio ritmo con --wpm cuando te hayas cronometrado leyendo
un guion en voz alta: casi todo el mundo cae entre 150 y 200, y el valor por
defecto es 165 (no está calibrado específicamente para español).

Uso
  python3 beats.py guion.txt
  python3 beats.py guion.txt --target 30
  python3 beats.py guion.txt --wpm 185 --target 45
  pbpaste | python3 beats.py -
  python3 beats.py guion.txt --json
  python3 beats.py guion.txt --lang en

Idioma: --lang es (por defecto) o en, o la variable de entorno IG_LANG.
"""

import argparse
import json
import os
import re
import sys
import unicodedata

LANGS = ("es", "en")
DEFAULT_LANG = os.environ.get("IG_LANG", "es") if os.environ.get("IG_LANG") in LANGS else "es"

WORD_RE = re.compile(r"[\w$€£%'’-]+")
SENT_RE = re.compile(r"[^.!?]+[.!?]*")
UPPER = "A-ZÁÉÍÓÚÑÜÀÈÌÒÙÂÊÎÔÛÇ"
LOWER = "a-záéíóúñüàèìòùâêîôûç"

HOOK_WINDOW = 3.0        # segundos. Pasado esto, el pulgar ya ha decidido.
MAX_BEAT = 4.0           # segundos con una sola idea sin cambio en pantalla.
ABSTRACT_RUN = 3         # bloques seguidos sin nada comprobable.


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


EN = {
    "fold": False,
    "num_sep": r"(?<=\d),(?=\d)",
    "concrete_re": re.compile(r"[$€£]\s?\d|\b\d[\d,.]*\b|(?<!^)\b[A-Z][a-z]{2,}\b", re.MULTILINE),
    "stopwords": {
        "the", "a", "an", "and", "or", "but", "if", "of", "to", "in", "on", "for",
        "with", "that", "this", "it", "is", "are", "was", "were", "be", "been",
        "you", "your", "i", "my", "me", "we", "our", "they", "them", "he", "she",
        "so", "just", "not", "no", "do", "did", "does", "have", "has", "had",
        "will", "can", "at", "as", "by", "from", "out", "up", "off", "one", "all",
    },
    "labels": {"HOOK": "HOOK", "MID": "MID", "CTA": "CTA", "HOOK/CTA": "HOOK/CTA"},
    "msg": {
        "head": "BEAT SHEET  ·  {words} words  ·  ~{secs:.1f}s at {wpm:g} wpm",
        "target": "  ·  target {t:g}s",
        "flag_hook": "hook runs {d:.1f}s, past the {w:.0f}s mark",
        "note_hook": "Beat 1 takes {d:.1f}s to say. Cut it to {n} words or fewer, or the hook "
                     "lands after the decision has been made.",
        "note_hook_abstract": "Beat 1 has no number and no name in it. Hooks without something "
                              "checkable are the ones that get scrolled.",
        "flag_long": "{d:.1f}s on one beat",
        "note_long": "Beat(s) {beats} run past {m:.0f}s. Either split the line or change what is "
                     "on screen inside it. A static frame is where people leave.",
        "note_abstract": "Beats {a}-{b} have nothing concrete in them. Put a number, a name or a "
                         "price in one of them.",
        "note_loop": "Loops: the last beat repeats \"{w}\" from the hook. Second watches are free "
                     "reach.",
        "note_noloop": "No loop. The last beat shares no word with the hook, so the video ends "
                       "flat. Echoing one word from beat 1 is the cheapest replay you get.",
        "note_on_target": "Length is on target ({total:.1f}s against {t:g}s).",
        "note_over": "{d:.1f}s over target. Cut about {n} words.",
        "note_under": "{d:.1f}s under target. Either add {n} words or shoot it short. Short is "
                      "usually right.",
        "empty": "empty script",
    },
}

ES = {
    "fold": True,
    "num_sep": r"(?<=\d)[.,](?=\d)|(?<=\d)\s+(?=[€%])",
    "concrete_re": re.compile(
        r"[$€£]\s?\d|\b\d[\d,.]*\b|(?<!^)(?<![¿¡])\b[" + UPPER + r"][" + LOWER + r"]{2,}\b",
        re.MULTILINE),
    # Para detectar el bucle se comparan palabras con contenido, sin tildes.
    "stopwords": {
        "el", "la", "los", "las", "un", "una", "unos", "unas", "y", "e", "o", "u",
        "pero", "si", "de", "del", "a", "al", "en", "por", "para", "con", "sin", "que",
        "es", "son", "era", "fue", "ser", "estar", "esta", "estan", "este", "esto",
        "estos", "estas", "ese", "esa", "eso", "lo", "le", "les", "se", "me", "te",
        "nos", "os", "mi", "mis", "tu", "tus", "su", "sus", "yo", "el", "ella", "ellos",
        "ellas", "nosotros", "vosotros", "ustedes", "usted", "no", "ni", "ya", "mas",
        "muy", "como", "cuando", "donde", "hay", "he", "ha", "has", "han", "hemos",
        "tengo", "tiene", "uno", "todo", "todos", "asi", "solo", "tambien", "porque",
        "entonces", "pues", "cada",
    },
    "labels": {"HOOK": "GANCHO", "MID": "MITAD", "CTA": "CTA", "HOOK/CTA": "GANCHO/CTA"},
    "msg": {
        "head": "ESCALETA  ·  {words} palabras  ·  ~{secs:.1f}s a {wpm:g} ppm",
        "target": "  ·  objetivo {t:g}s",
        "flag_hook": "el gancho dura {d:.1f}s, pasa de los {w:.0f}s",
        "note_hook": "El bloque 1 tarda {d:.1f}s en decirse. Déjalo en {n} palabras o menos, o el "
                     "gancho llega cuando la decisión ya está tomada.",
        "note_hook_abstract": "El bloque 1 no tiene ni un número ni un nombre. Los ganchos sin "
                              "nada comprobable son los que se pasan de largo.",
        "flag_long": "{d:.1f}s en un solo bloque",
        "note_long": "El/los bloque(s) {beats} pasan de {m:.0f}s. Parte la frase o cambia lo que "
                     "hay en pantalla dentro de ella. Un plano estático es donde la gente se va.",
        "note_abstract": "Los bloques {a}-{b} no tienen nada concreto. Mete un número, un nombre o "
                         "un precio en alguno.",
        "note_loop": "Bucle: el último bloque repite «{w}» del gancho. Las segundas vistas son "
                     "alcance gratis.",
        "note_noloop": "Sin bucle. El último bloque no comparte ninguna palabra con el gancho, así "
                       "que el vídeo acaba plano. Repetir una palabra del bloque 1 es la "
                       "repetición más barata que vas a conseguir.",
        "note_on_target": "La duración cuadra con el objetivo ({total:.1f}s frente a {t:g}s).",
        "note_over": "{d:.1f}s por encima del objetivo. Recorta unas {n} palabras.",
        "note_under": "{d:.1f}s por debajo del objetivo. Añade {n} palabras o grábalo corto. Corto "
                      "suele ser lo correcto.",
        "empty": "guion vacío",
    },
}

DATA = {"en": EN, "es": ES}


def words(text, lang=DEFAULT_LANG):
    # "18.000" es una palabra cuando se dice, así que aquí también.
    return WORD_RE.findall(re.sub(DATA[lang]["num_sep"], "", text))


def pretty(token, lang):
    """Vuelve a poner el separador de miles para mostrarlo."""
    sep = "." if lang == "es" else ","

    def fmt(m):
        digits = m.group(0)
        if re.fullmatch(r"(?:19|20)\d\d", digits):      # un año, no una cifra
            return digits
        return format(int(digits), ",").replace(",", sep)

    return re.sub(r"\d{4,}", fmt, token)


def tc(seconds):
    m, s = divmod(seconds, 60)
    return f"{int(m)}:{s:04.1f}"


def split_beats(raw, wps, lang):
    """Una línea es un bloque, salvo que sea demasiado larga para serlo."""
    beats = []
    for line in [l.strip() for l in raw.splitlines()]:
        if not line:
            continue
        if len(words(line, lang)) / wps <= MAX_BEAT * 1.5:
            beats.append(line)
            continue
        # Párrafo largo: se corta en los finales de frase para que los tiempos
        # signifiquen algo.
        parts = [p.strip() for p in SENT_RE.findall(line) if p.strip()]
        buf = ""
        for part in parts:
            candidate = (buf + " " + part).strip()
            if buf and len(words(candidate, lang)) / wps > MAX_BEAT:
                beats.append(buf)
                buf = part
            else:
                buf = candidate
        if buf:
            beats.append(buf)
    return beats


def content_words(text, L, lang):
    out = set()
    for w in words(text, lang):
        k = w.lower()
        k = strip_accents(k) if L["fold"] else k
        if k not in L["stopwords"]:
            out.add(k)
    return out


def analyse(raw, wpm=165, target=None, lang=DEFAULT_LANG):
    L = DATA[lang]
    m = L["msg"]
    wps = wpm / 60.0
    beats = split_beats(raw, wps, lang)
    if not beats:
        return None

    rows, clock = [], 0.0
    for i, text in enumerate(beats):
        n = len(words(text, lang))
        dur = n / wps
        rows.append({
            "n": i + 1,
            "start": round(clock, 2),
            "dur": round(dur, 2),
            "words": n,
            "text": text,
            "concrete": len(L["concrete_re"].findall(text)),
            "label": "",
            "flags": [],
        })
        clock += dur
    total = clock

    # Las posiciones estructurales sobre las que se construye un Reel.
    for r in rows:
        if r["n"] == 1 or r["start"] + r["dur"] <= HOOK_WINDOW:
            r["label"] = "HOOK"
    rows[-1]["label"] = "CTA" if rows[-1]["label"] != "HOOK" else "HOOK/CTA"
    half = total / 2
    for r in rows:
        if not r["label"] and r["start"] <= half < r["start"] + r["dur"]:
            r["label"] = "MID"

    notes = []
    if rows[0]["dur"] > HOOK_WINDOW:
        rows[0]["flags"].append(m["flag_hook"].format(d=rows[0]["dur"], w=HOOK_WINDOW))
        notes.append(m["note_hook"].format(d=rows[0]["dur"], n=int(HOOK_WINDOW * wps)))
    if rows[0]["concrete"] == 0:
        notes.append(m["note_hook_abstract"])

    for r in rows:
        if r["dur"] > MAX_BEAT:
            r["flags"].append(m["flag_long"].format(d=r["dur"]))
    long_beats = [r["n"] for r in rows if r["dur"] > MAX_BEAT]
    if long_beats:
        notes.append(m["note_long"].format(beats=", ".join(map(str, long_beats)), m=MAX_BEAT))

    run, start = 0, None
    for r in rows:
        if r["concrete"] == 0:
            run += 1
            start = start if start is not None else r["n"]
            if run == ABSTRACT_RUN:
                notes.append(m["note_abstract"].format(a=start, b=r["n"]))
        else:
            run, start = 0, None

    # ¿La última línea te devuelve a la primera?
    loop = sorted(pretty(w, lang) for w in
                  content_words(rows[0]["text"], L, lang) & content_words(rows[-1]["text"], L, lang))
    if loop:
        notes.append(m["note_loop"].format(w=", ".join(loop[:3])))
    else:
        notes.append(m["note_noloop"])

    if target:
        delta = total - target
        if abs(delta) <= target * 0.1:
            notes.append(m["note_on_target"].format(total=total, t=target))
        elif delta > 0:
            notes.append(m["note_over"].format(d=delta, n=int(delta * wps)))
        else:
            notes.append(m["note_under"].format(d=-delta, n=int(-delta * wps)))

    return {
        "lang": lang,
        "wpm": wpm, "target": target,
        "total_seconds": round(total, 2),
        "total_words": sum(r["words"] for r in rows),
        "beats": rows,
        "notes": notes,
    }


def render(a, out=sys.stdout):
    L = DATA[a["lang"]]
    m, lab = L["msg"], L["labels"]
    width = max(len(v) for v in lab.values()) + 2
    head = m["head"].format(words=a["total_words"], secs=a["total_seconds"], wpm=a["wpm"]) + (
        m["target"].format(t=a["target"]) if a["target"] else "")
    print("\n" + head, file=out)
    print("=" * max(len(head), 72), file=out)
    for r in a["beats"]:
        label = f"{lab[r['label']]:<{width}}" if r["label"] else " " * width
        print(f"  {tc(r['start'])}  {r['dur']:4.1f}s  {label}{r['text']}", file=out)
        for f in r["flags"]:
            print(f"  {'':>6}  {'':>5}  {'':<{width}}^ {f}", file=out)
    print("-" * max(len(head), 72), file=out)
    for n in a["notes"]:
        print(f"  - {n}", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Cronometra un guion de Reel en una escaleta.")
    ap.add_argument("input", nargs="?", default="-", help="archivo de guion, o - para stdin")
    ap.add_argument("--wpm", type=float, default=165,
                    help="ritmo al hablar, palabras por minuto (por defecto 165)")
    ap.add_argument("--target", type=float, help="duración objetivo en segundos")
    ap.add_argument("--lang", choices=LANGS, default=DEFAULT_LANG,
                    help=f"idioma de los mensajes y las palabras vacías (por defecto {DEFAULT_LANG})")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    a = analyse(raw, wpm=args.wpm, target=args.target, lang=args.lang)
    if not a:
        print(DATA[args.lang]["msg"]["empty"], file=sys.stderr)
        sys.exit(2)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0)


if __name__ == "__main__":
    main()
