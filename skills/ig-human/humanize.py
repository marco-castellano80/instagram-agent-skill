#!/usr/bin/env python3
"""
humanize.py - quita de un borrador la huella de máquina.

Tres pasadas, en este orden:

  1. INVISIBLES  borra o normaliza los caracteres que un teclado humano no
                 produce: espacios y uniones de ancho cero, word joiners,
                 guiones blandos, BOM, caracteres de etiqueta Unicode,
                 espacios duros y estrechos. Sobreviven al copiar y pegar.
  2. TIPOGRAFÍA  raya -> coma, semirraya -> guion, comillas curvas ->
                 rectas, puntos suspensivos -> tres puntos, viñeta -> guion.
                 Las comillas angulares «» y los signos ¿ ¡ se respetan.
  3. LÉXICO      sustituye el léxico de relleno (slop.es.json con --lang es,
                 slop.json con --lang en) por palabras normales, conservando
                 mayúsculas y sin tocar las URL.

Las señales de estructura (tríadas, "no es solo X, es Y", muros de hashtags)
se SEÑALAN, nunca se reescriben solas: cambiar la forma de una frase necesita
criterio, y eso le toca al modelo, no a una regex.

Uso
  python3 humanize.py borrador.txt
  python3 humanize.py borrador.txt --report
  pbpaste | python3 humanize.py - --report
  python3 humanize.py borrador.txt --json
  python3 humanize.py borrador.txt -o limpio.txt
  python3 humanize.py draft.txt --lang en

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

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "slop.json")

# URL, emails, hashtags y menciones no se reescriben: "#innovador" no debe
# convertirse en "#nuevo".
URL_RE = re.compile(r"https?://\S+|www\.\S+|\S+@\S+\.\S+|(?<!\w)[#@][\w.]*\w")
# Un punto entre cifras ("18.000") no cierra la frase.
SENT_RE = re.compile(r"(?:[^.!?\n]|(?<=\d)\.(?=\d))+[.!?]*")
LETTER = r"[^\W\d_]"
OPENERS = "¿¡\"'«(“"

# Una raya seguida de un conector ("es importante — además, es una prueba")
# daría una frase empalmada al convertirse en coma. Solo en ese caso se
# convierte en punto. Incluye los conectores de relleno que el léxico cambia
# después ("asimismo" -> "también").
SPLICE = {
    "en": r"also|so|still|basically|in the end|moreover|furthermore|additionally"
          r"|nevertheless|consequently|thus|hence|ultimately|in essence|in conclusion",
    "es": r"además|así que|aun así|básicamente|al final|también|asimismo|no obstante"
          r"|en consecuencia|por consiguiente|en definitiva|en esencia|en última instancia"
          r"|en conclusión",
}

MSG = {
    "en": {
        "report": "HUMANIZE REPORT",
        "summary": "{t} machine artefacts removed, {s} structural tells flagged for rewrite",
        "invisible": "1. INVISIBLE CHARACTERS",
        "typo": "2. TYPOGRAPHY",
        "lexicon": "3. SLOP LEXICON",
        "structures": "4. STRUCTURAL TELLS  (not auto-fixed - rewrite these yourself)",
        "clean": "CLEAN",
        "nothing": "  Nothing to strip.",
        "deleted": "(deleted)",
        "space": "(space)",
        "other_cf": "other invisible format chars",
        "actions": {"delete": "delete", "space": "space"},
        "uniform": "Uniform sentence length (variation {cv:.2f})",
        "uniform_fix": "Break one sentence in half. Let another run long. Machines write even.",
        "wrote": "wrote {p}",
    },
    "es": {
        "report": "INFORME DE HUMANIZACIÓN",
        "summary": "{t} artefactos de máquina eliminados, {s} señales de estructura marcadas "
                   "para reescribir",
        "invisible": "1. CARACTERES INVISIBLES",
        "typo": "2. TIPOGRAFÍA",
        "lexicon": "3. LÉXICO DE RELLENO",
        "structures": "4. SEÑALES DE ESTRUCTURA  (no se arreglan solas: reescríbelas tú)",
        "clean": "LIMPIO",
        "nothing": "  No hay nada que quitar.",
        "deleted": "(borrado)",
        "space": "(espacio)",
        "other_cf": "otros caracteres de formato invisibles",
        "actions": {"delete": "borrar", "space": "espacio"},
        "uniform": "Frases de longitud uniforme (variación {cv:.2f})",
        "uniform_fix": "Parte una frase por la mitad. Deja que otra se alargue. Las máquinas "
                       "escriben parejo.",
        "wrote": "escrito {p}",
    },
}


def load_lexicon(path=LEX, lang=DEFAULT_LANG, overlay=None):
    """slop.json da invisibles y tipografía; slop.<lang>.json, si existe y el
    idioma no es inglés, sustituye palabras, frases y estructuras."""
    with open(path, encoding="utf-8") as fh:
        lex = json.load(fh)
    if overlay is None and lang != "en":
        overlay = os.path.join(os.path.dirname(os.path.abspath(path)), f"slop.{lang}.json")
    if overlay and os.path.exists(overlay):
        with open(overlay, encoding="utf-8") as fh:
            extra = json.load(fh)
        for key in ("invisible", "typographic", "words", "phrases", "structures"):
            if key in extra:
                lex[key] = extra[key]
    return lex


def _cp(spec):
    """'U+200B' -> 0x200b;  'U+E0000-U+E007F' -> (inicio, fin)."""
    if "-" in spec:
        a, b = spec.split("-")
        return (int(a[2:], 16), int(b[2:], 16))
    return int(spec[2:], 16)


def protect_urls(text):
    """Cambia las URL por marcadores para que ninguna pasada reescriba un enlace."""
    found = []

    def stash(m):
        found.append(m.group(0))
        return f"\x00URL{len(found) - 1}\x00"

    return URL_RE.sub(stash, text), found


def restore_urls(text, found):
    for i, url in enumerate(found):
        text = text.replace(f"\x00URL{i}\x00", url)
    return text


def pass_invisible(text, lex, m):
    """Borra o convierte en espacio los caracteres invisibles. Devuelve (texto, hallazgos)."""
    hits = []
    for entry in lex["invisible"]:
        cp = _cp(entry["cp"])
        if isinstance(cp, tuple):
            pattern = "[" + re.escape(chr(cp[0])) + "-" + re.escape(chr(cp[1])) + "]"
        else:
            pattern = re.escape(chr(cp))
        n = len(re.findall(pattern, text))
        if n:
            hits.append({"name": entry["cp"] + " " + entry["name"], "count": n,
                         "action": entry["action"]})
            text = re.sub(pattern, "" if entry["action"] == "delete" else " ", text)
    # Cualquier otro carácter Cf (de formato) es invisible por definición.
    stray = [c for c in text if unicodedata.category(c) == "Cf"]
    if stray:
        hits.append({"name": m["other_cf"], "count": len(stray), "action": "delete"})
        text = "".join(c for c in text if unicodedata.category(c) != "Cf")
    return text, hits


def pass_typographic(text, lex, m, lang=DEFAULT_LANG):
    hits = []
    for entry in lex["typographic"]:
        ch = entry["from"]
        n = len(re.findall(r"[ \t]+·[ \t]+", text)) if ch == "·" else text.count(ch)
        if not n:
            continue
        hits.append({"name": f"{ch} {entry['name']}", "count": n,
                     "to": entry["to"].strip() or m["space"]})
        if ch == "—":
            text = re.sub(r"[ \t]*—[ \t]*(" + SPLICE[lang] + r")[ \t]*,[ \t]*",
                          lambda mm: ". " + mm.group(1)[0].upper() + mm.group(1)[1:] + ", ",
                          text, flags=re.IGNORECASE)
            # " palabra — palabra " y "palabra—palabra" quedan en coma + espacio.
            text = re.sub(r"\s*—\s*", ", ", text)
        elif ch == "·":
            # Solo como separador entre espacios: la "l·l" catalana se queda.
            text = re.sub(r"[ \t]+·[ \t]+", " " + entry["to"] + " ", text)
        elif ch == "–":
            text = re.sub(r"\s*–\s*(?=\d)", "-", text)      # 5–10 -> 5-10
            text = re.sub(r"\s+–\s+", ", ", text)            # usada como raya
            text = text.replace("–", "-")
        else:
            text = text.replace(ch, entry["to"])
    # Una coma insertada delante de otra puntuación queda mal.
    text = re.sub(r",\s*([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*\n", "\n", text)
    # Una raya al principio de línea (diálogo o lista) deja una coma huérfana.
    text = re.sub(r"(?m)^,\s*", "", text)
    return text, hits


def _match_case(src, repl):
    if not repl:
        return repl
    if src.isupper() and len(src) > 1:
        return repl.upper()
    if src[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def pass_lexical(text, lex, lang, m):
    """Sustituye palabras y frases de relleno. Las más largas primero para que ganen las frases."""
    hits = []
    entries = sorted(lex["phrases"] + lex["words"],
                     key=lambda e: len(e["find"]), reverse=True)
    for entry in entries:
        find = entry["find"]
        pattern = re.compile(r"\b" + re.escape(find).replace(r"\ ", r"\s+") + r"\b",
                             re.IGNORECASE)
        found = pattern.findall(text)
        if not found:
            continue
        hits.append({"find": find, "replace": entry["replace"] or m["deleted"],
                     "count": len(found), "family": entry["family"]})
        text = pattern.sub(lambda mm: _match_case(mm.group(0), entry["replace"]), text)
    # Limpieza después de borrar. Borrar una cláusula entera deja puntuación
    # huérfana ("sistema. ." o una línea que ahora empieza por coma), y eso se
    # lee peor que el relleno.
    text = text.replace("...", "\x00ELL\x00")          # protege los puntos suspensivos reales
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"(?m)^[ \t]*(?:[,.;:]+[ \t]*)+", "", text)
    text = re.sub(r"(?m)^[ \t](?=\S)", "", text)       # un espacio que dejó un borrado.
                                                      # Las sangrías más hondas son a propósito.
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*([,.;:!?])", r"\1", text)      # una raya se volvió coma y luego
                                                      # se fue la cláusula de detrás
    text = re.sub(r"([¿¡])\s*[,;:]\s*", r"\1", text)   # "¿, qué" -> "¿qué"
    # Borrar todo lo que había entre ¡ y ! (o ¿ y ?) deja los signos solos.
    text = re.sub(r"(?m)^[ \t]*[¡¿][ \t]*[!?]+[ \t]*(?:\n|$)", "", text)
    text = re.sub(r"[ \t]*[¡¿][ \t]*[!?]+", "", text)
    # "Funciona., hay" -> "Funciona. hay" (respeta "etc.," y "p. ej.,")
    text = re.sub(r"(?<!etc)(?<!ej)(?<!aprox)([.!?])[ \t]*[,;:]+[ \t]*", r"\1 ", text)
    text = re.sub(r"\.\s*\.+", ".", text)
    text = re.sub(r"([!?])\s*\.", r"\1", text)
    text = text.replace("\x00ELL\x00", "...")
    text = re.sub(r"(?m)^[ \t]+$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text, hits


def scan_structures(text, lex, m):
    flags = []
    for s in lex["structures"]:
        try:
            pattern = re.compile(s["regex"], re.MULTILINE)
        except re.error:
            continue
        found = pattern.findall(text)
        if found:
            flags.append({"name": s["name"], "count": len(found), "fix": s["fix"]})
    # La uniformidad de longitud de frase también es estructural.
    lens = [len(s.split()) for s in SENT_RE.findall(text) if len(s.split()) > 2]
    if len(lens) >= 4:
        mean = sum(lens) / len(lens)
        var = sum((n - mean) ** 2 for n in lens) / len(lens)
        cv = (var ** 0.5) / mean if mean else 0
        if cv < 0.35:
            flags.append({"name": m["uniform"].format(cv=cv), "count": len(lens),
                          "fix": m["uniform_fix"]})
    return flags


def restore_capitals(original, text):
    """Borrar una apertura deja la siguiente palabra en minúscula.

    Solo se arregla si quien escribe pone mayúscula al empezar frase: una voz
    en minúsculas a propósito es un estilo, no un artefacto. Tiene en cuenta
    ¿ ¡ y comillas delante de la primera letra.
    """
    lead = "[" + re.escape(OPENERS) + "]?"
    starts = re.findall(r"(?:^|[.!?]\s+|\n)\s*" + lead + "(" + LETTER + ")", original)
    if not starts or sum(1 for c in starts if c.isupper()) * 2 < len(starts):
        return text
    return re.sub(r"(?:^|(?<=[.!?] )|(?<=[.!?]\n)|(?<=\n))(\s*" + lead + ")(" + LETTER + ")",
                  lambda mm: mm.group(1) + mm.group(2).upper(), text)


def humanize(text, lex, lang=DEFAULT_LANG):
    m = MSG[lang]
    raw_for_case = text
    text, urls = protect_urls(text)
    text, inv = pass_invisible(text, lex, m)
    text, typo = pass_typographic(text, lex, m, lang)
    text, lexi = pass_lexical(text, lex, lang, m)
    text = restore_capitals(raw_for_case, text)
    text = restore_urls(text, urls)
    return text.strip() + "\n", {
        "invisible": inv,
        "typographic": typo,
        "lexical": lexi,
        "structures": scan_structures(text, lex, m),
    }


def render_report(report, lang=DEFAULT_LANG, out=sys.stderr):
    m = MSG[lang]

    def head(title):
        print(f"\n{title}\n" + "-" * len(title), file=out)

    total = sum(h["count"] for h in report["invisible"]) \
        + sum(h["count"] for h in report["typographic"]) \
        + sum(h["count"] for h in report["lexical"])

    head(m["report"])
    print(m["summary"].format(t=total, s=len(report["structures"])), file=out)

    if report["invisible"]:
        head(m["invisible"])
        for h in report["invisible"]:
            print(f"  {h['count']:>3}x  {h['name']}  -> {m['actions'].get(h['action'], h['action'])}",
                  file=out)
    if report["typographic"]:
        head(m["typo"])
        for h in report["typographic"]:
            print(f"  {h['count']:>3}x  {h['name']}  -> {h['to']}", file=out)
    if report["lexical"]:
        head(m["lexicon"])
        for h in report["lexical"]:
            print(f"  {h['count']:>3}x  {h['find']}  -> {h['replace']}   [{h['family']}]", file=out)
    if report["structures"]:
        head(m["structures"])
        for h in report["structures"]:
            print(f"  {h['count']:>3}x  {h['name']}\n        {h['fix']}", file=out)
    if not any(report.values()):
        head(m["clean"])
        print(m["nothing"], file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Quita de un borrador la huella de máquina.")
    ap.add_argument("input", nargs="?", default="-", help="archivo, o - para stdin")
    ap.add_argument("-o", "--out", help="escribe aquí el texto limpio en vez de en stdout")
    ap.add_argument("--report", action="store_true", help="muestra lo que cambió, por stderr")
    ap.add_argument("--json", action="store_true", help="emite {text, report} como JSON")
    ap.add_argument("--lang", choices=LANGS, default=DEFAULT_LANG,
                    help=f"idioma del léxico y los mensajes (por defecto {DEFAULT_LANG})")
    ap.add_argument("--lexicon", default=LEX, help="ruta a slop.json (invisibles y tipografía)")
    ap.add_argument("--lexicon-lang", help="ruta al léxico del idioma (por defecto slop.<lang>.json)")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    lex = load_lexicon(args.lexicon, args.lang, args.lexicon_lang)
    clean, report = humanize(raw, lex, args.lang)

    if args.json:
        print(json.dumps({"text": clean, "report": report}, indent=2, ensure_ascii=False))
        return
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(clean)
        print(MSG[args.lang]["wrote"].format(p=args.out), file=sys.stderr)
    else:
        sys.stdout.write(clean)
    if args.report:
        render_report(report, args.lang)


if __name__ == "__main__":
    main()
