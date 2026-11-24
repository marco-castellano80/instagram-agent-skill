#!/usr/bin/env python3
"""
caption.py - revisa el texto de una publicación de Instagram y enseña
exactamente lo que se ve en el feed antes del "... más".

Instagram muestra unos 125 caracteres del texto en el feed y esconde el resto
detrás de un toque. Casi todos los textos que fallan, fallan ahí: el gancho
está en la tercera frase, la primera línea es un saludo, o todo empieza con un
hashtag. Este script imprime la ventana visible en un recuadro para que la
leas como la lee un desconocido haciendo scroll, y luego comprueba las ocho
cosas que merece la pena comprobar.

El corte de 125 caracteres es aproximado. El número real cambia con el
dispositivo, el tamaño de letra y dónde caen tus saltos de línea, que es
justo por lo que quieres margen y no un texto diseñado para acabar en 125.
Cámbialo con --truncate si quieres probar uno más estricto.

Uso
  python3 caption.py texto.txt
  python3 caption.py texto.txt --keywords "contratos freelance,precios de agencia"
  pbpaste | python3 caption.py -
  python3 caption.py texto.txt --json
  python3 caption.py texto.txt --lang en

Idioma: --lang es (por defecto) o en, o la variable de entorno IG_LANG.
"""

import argparse
import json
import os
import re
import sys
import textwrap
import unicodedata

LANGS = ("es", "en")
DEFAULT_LANG = os.environ.get("IG_LANG", "es") if os.environ.get("IG_LANG") in LANGS else "es"

LIMIT = 2200             # Límite duro de Instagram para el texto.
TRUNCATE = 125           # Más o menos donde el feed corta a "... más".
HASHTAG_LIMIT = 5        # Tope de Instagram por publicación o reel desde el
                         # 18 dic 2025, antes 30 (anunciado por la cuenta
                         # @Creators: "using fewer (up to 5) more targeted
                         # hashtags, rather than many generic ones, can
                         # improve both your content's performance and
                         # people's experience"). Compruébalo: las cifras de
                         # la plataforma cambian.

HASHTAG_RE = re.compile(r"(?:^|\s)(#\w+)")
MENTION_RE = re.compile(r"(?:^|\s)(@[\w.]+)")
LINK_RE = re.compile(r"https?://\S+|\bwww\.\S+"
                     r"|\b[a-z0-9-]+\.(?:com|co|io|net|org|ai|app|es|mx|ar|cl|pe|eu|me)/\S*",
                     re.IGNORECASE)
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿←-⇿️]")
UPPER = "A-ZÁÉÍÓÚÑÜÀÈÌÒÙÂÊÎÔÛÇ"
LOWER = "a-záéíóúñüàèìòùâêîôûç"


def fold(s):
    """Minúsculas y sin tildes, para comparar términos de búsqueda."""
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")


FILLER_EN = {"#viral", "#fyp", "#explore", "#explorepage", "#foryou", "#foryoupage",
             "#trending", "#instagood", "#love", "#follow", "#like4like", "#reels",
             "#reelsinstagram", "#viralreels", "#instadaily"}
FILLER_ES = FILLER_EN | {"#parati", "#paratii", "#paratipage", "#explorar", "#tendencia",
                         "#tendencias", "#reel", "#instagram", "#amor", "#sigueme",
                         "#seguidores", "#likes", "#megusta", "#reelsespanol",
                         "#reelsespana", "#viralespana", "#virales"}

EN = {
    "concrete_re": re.compile(r"[$€£]\s?\d|\b\d[\d,.]*\b|(?<!^)\b[A-Z][a-z]{2,}\b", re.MULTILINE),
    "asks": [
        (re.compile(r"(?i)\bcomment (?:the word |\")?[A-Z0-9]{2,}\b"), "comment a keyword"),
        (re.compile(r"(?i)\b(?:dm|message) me\b"), "DM me"),
        (re.compile(r"(?i)\bsave (?:this|it)\b"), "save this"),
        (re.compile(r"(?i)\bshare (?:this|it)\b"), "share this"),
        (re.compile(r"(?i)\bfollow (?:me|for)\b"), "follow"),
        (re.compile(r"(?i)\blink in (?:my )?bio\b"), "link in bio"),
        (re.compile(r"(?i)\b(?:swipe|tap) (?:through|left|right|for|to)\b"), "swipe or tap"),
        (re.compile(r"(?i)\btell me\b|\bwhat would you\b|\bwhich one\b"), "answer a question"),
    ],
    "filler": FILLER_EN,
    "greeting_re": re.compile(r"(?i)^\s*(?:hey|hi|hello|welcome|good (?:morning|evening))\b"),
    "labels": {"LENGTH": "LENGTH", "FIRST LINE": "FIRST LINE", "HOOK IS CONCRETE": "HOOK IS CONCRETE",
               "HASHTAGS": "HASHTAGS", "TAG PLACEMENT": "TAG PLACEMENT", "LINKS": "LINKS",
               "ONE ASK": "ONE ASK", "EMOJI": "EMOJI", "SEARCH TERMS": "SEARCH TERMS"},
    "status": {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL"},
    "verdicts": {"READY": "READY", "REVIEW": "REVIEW", "FIX": "FIX"},
    "msg": {
        "box_title": "WHAT THE FEED SHOWS",
        "more": "... more",
        "fits": "(whole caption fits)",
        "length": "{c} / {l} characters",
        "length_over": ", {n} over the limit",
        "fl_blank": "the caption opens on a blank line",
        "fl_tag": "opens on a hashtag or a mention, which is the one position worth a sentence",
        "fl_greeting": "opens on a greeting. Nobody opened the app to be greeted: start on the hook",
        "fl_long": "{n} characters, so it gets cut at {cut} mid-thought. Fine if the cut is a "
                   "cliffhanger, bad if it is a subordinate clause",
        "fl_ok": "{n} characters, lands whole",
        "concrete": "{n} number(s) or name(s) in the visible window",
        "concrete_none": " - nothing checkable before the tap",
        "tags_over": "{n} tags, over Instagram's cap of {cap}. Tags past the fifth do not count "
                     "and the block reads as old",
        "tags_cap_filler": "{n} tags, at the cap, and {f} of them generic. Spend the five on topics",
        "tags_filler": "{n} tags, {f} of them generic ({ex}). Those describe nothing",
        "tags_ok": "{n} tag(s)",
        "place_none": "no tags to place",
        "place_window": "a hashtag is inside the visible window, spending feed space on a label",
        "place_ok": "tags are below the fold",
        "links": "{n} link(s) in the caption, and captions are not clickable. Move it to the bio "
                 "or the DM",
        "links_ok": "no dead links in the body",
        "ask_one": "one call to action: {a}",
        "ask_none": "no call to action. Decide what this post is for",
        "ask_many": "{n} asks ({a}). Two asks is the same as none",
        "emoji": "{n} emoji, {d:.1f} per 100 characters",
        "emoji_heavy": " - reads as decoration",
        "search": "{f}/{t} present",
        "search_window": ", {n} in the visible window",
        "search_missing": ". Missing: {m}",
        "head": "CAPTION LINT  ·  {c} / {l} chars  ·  {h} hashtags  ·  {a} ask(s)",
        "verdict": "VERDICT",
    },
}

ES = {
    # Una mayúscula detrás de ¿ o ¡ es inicio de frase, no un nombre.
    "concrete_re": re.compile(
        r"[$€£]\s?\d|\b\d[\d,.]*\b|(?<!^)(?<![¿¡])\b[" + UPPER + r"][" + LOWER + r"]{2,}\b",
        re.MULTILINE),
    "asks": [
        (re.compile(r"(?i)\bcomenta (?:la palabra |aqu[ií] )?[\"“'«]?[" + UPPER + r"0-9]{2,}\b"
                    r"|\bescribe [\"“'«]?\w+[\"”'»]? en (?:los )?comentarios\b"),
         "comentar una palabra clave"),
        (re.compile(r"(?i)\b(?:escr[ií]beme|m[aá]ndame|env[ií]ame)(?: un)? (?:dm|md|mensaje|privado)\b"
                    r"|\bpor (?:dm|md|privado)\b"),
         "mensaje privado"),
        (re.compile(r"(?i)\bgu[aá]rd(?:alo|atelo|adlo|ala|atela|aos)\b"
                    r"|\bguarda (?:este|esta|esto|el post|el reel|el carrusel|la publicaci[oó]n)\b"),
         "guardar"),
        (re.compile(r"(?i)\bcomp[aá]rt(?:elo|ela|idlo|ele)\b"
                    r"|\bcomparte (?:este|esta|esto|el post|el reel|con)\b"),
         "compartir"),
        (re.compile(r"(?i)\bs[ií]gueme\b|\bsigue a @|\bdale a seguir\b"), "seguir"),
        (re.compile(r"(?i)\b(?:link|enlace) en (?:la |mi )?bio\b"), "enlace en la bio"),
        (re.compile(r"(?i)\bdesliza\b|\bswipe\b|\bpulsa (?:aqu[ií]|el enlace)\b"
                    r"|\btoca (?:aqu[ií]|el enlace)\b"),
         "deslizar o tocar"),
        (re.compile(r"(?i)\bd[ií]me\b|\bcu[eé]ntame\b|\bqu[eé] har[ií]as\b"
                    r"|\bcu[aá]l (?:prefieres|elegir[ií]as|eliges)\b|\bqu[eé] opinas\b"),
         "responder una pregunta"),
    ],
    "filler": FILLER_ES,
    "greeting_re": re.compile(r"(?i)^\s*[¡¿]?\s*(?:hola|buenas|buenos d[ií]as|qu[eé] tal|hey|ey"
                              r"|bienvenid[oa]s?)\b"),
    "labels": {"LENGTH": "LONGITUD", "FIRST LINE": "PRIMERA LÍNEA",
               "HOOK IS CONCRETE": "GANCHO CONCRETO", "HASHTAGS": "HASHTAGS",
               "TAG PLACEMENT": "SITIO DE TAGS", "LINKS": "ENLACES", "ONE ASK": "UNA PETICIÓN",
               "EMOJI": "EMOJI", "SEARCH TERMS": "BÚSQUEDA"},
    "status": {"PASS": "OK", "WARN": "AVISO", "FAIL": "FALLO"},
    "verdicts": {"READY": "LISTO", "REVIEW": "REVISAR", "FIX": "CORREGIR"},
    "msg": {
        "box_title": "LO QUE ENSEÑA EL FEED",
        "more": "... más",
        "fits": "(cabe el texto entero)",
        "length": "{c} / {l} caracteres",
        "length_over": ", {n} por encima del límite",
        "fl_blank": "el texto empieza con una línea en blanco",
        "fl_tag": "empieza con un hashtag o una mención, en la única posición que merece una frase",
        "fl_greeting": "empieza con un saludo. Nadie abre la app para que le saluden: empieza por el gancho",
        "fl_long": "{n} caracteres, así que se corta en {cut} a media idea. Bien si el corte deja "
                   "intriga, mal si corta una subordinada",
        "fl_ok": "{n} caracteres, se ve entera",
        "concrete": "{n} número(s) o nombre(s) en la ventana visible",
        "concrete_none": " - nada comprobable antes del toque",
        "tags_over": "{n} hashtags, por encima del tope de {cap} de Instagram. A partir del quinto "
                     "no cuentan y el bloque suena a 2019",
        "tags_cap_filler": "{n} hashtags, en el tope, y {f} genéricos. Gasta los cinco en temas",
        "tags_filler": "{n} hashtags, {f} genéricos ({ex}). Esos no describen nada",
        "tags_ok": "{n} hashtag(s)",
        "place_none": "no hay hashtags que colocar",
        "place_window": "hay un hashtag dentro de la ventana visible, gastando espacio del feed "
                        "en una etiqueta",
        "place_ok": "los hashtags están debajo del corte",
        "links": "{n} enlace(s) en el texto, y el texto no es clicable. Llévalo a la bio o al "
                 "mensaje privado",
        "links_ok": "no hay enlaces muertos en el texto",
        "ask_one": "una llamada a la acción: {a}",
        "ask_none": "ninguna llamada a la acción. Decide para qué es esta publicación",
        "ask_many": "{n} peticiones ({a}). Dos peticiones es lo mismo que ninguna",
        "emoji": "{n} emoji, {d:.1f} por cada 100 caracteres",
        "emoji_heavy": " - parece decoración",
        "search": "{f}/{t} presentes",
        "search_window": ", {n} en la ventana visible",
        "search_missing": ". Faltan: {m}",
        "head": "REVISIÓN DEL TEXTO  ·  {c} / {l} caracteres  ·  {h} hashtags  ·  {a} petición(es)",
        "verdict": "VEREDICTO",
    },
}

DATA = {"en": EN, "es": ES}


def visible_window(text, cut):
    """Lo que enseña el feed. Instagram corta a mitad de palabra, así que esto también."""
    flat = text.strip()
    return flat if len(flat) <= cut else flat[:cut]


def render_box(window, truncated, m, out=sys.stdout, width=52):
    print("\n  " + m["box_title"], file=out)
    print("  +" + "-" * (width + 2) + "+", file=out)
    lines = []
    for raw in window.split("\n"):
        lines.extend(textwrap.wrap(raw, width) or [""])
    for line in lines[:8]:
        print(f"  | {line:<{width}} |", file=out)
    tail = m["more"] if truncated else m["fits"]
    print("  +" + "-" * (width + 2 - len(tail) - 2) + f" {tail} " + "+", file=out)


def analyse(text, cut=TRUNCATE, keywords=None, lang=DEFAULT_LANG):
    L = DATA[lang]
    m = L["msg"]
    concrete_re = L["concrete_re"]
    text = text.rstrip()
    stripped = text.strip()
    chars = len(stripped)
    lines = [l for l in stripped.split("\n")]
    first_line = lines[0].strip() if lines else ""
    tags = HASHTAG_RE.findall(stripped)
    mentions = MENTION_RE.findall(stripped)
    links = LINK_RE.findall(stripped)
    emoji = EMOJI_RE.findall(stripped)
    window = visible_window(stripped, cut)
    truncated = chars > cut
    asks = [name for pattern, name in L["asks"] if pattern.search(stripped)]
    filler = [t for t in tags if fold(t) in L["filler"]]
    keywords = [k.strip() for k in (keywords or []) if k.strip()]

    checks = []

    def add(cid, status, detail):
        checks.append({"check": cid, "label": L["labels"][cid], "status": status,
                       "detail": detail})

    add("LENGTH", "FAIL" if chars > LIMIT else "PASS",
        m["length"].format(c=chars, l=LIMIT)
        + (m["length_over"].format(n=chars - LIMIT) if chars > LIMIT else ""))

    if not first_line:
        add("FIRST LINE", "FAIL", m["fl_blank"])
    elif first_line.startswith("#") or first_line.startswith("@"):
        add("FIRST LINE", "FAIL", m["fl_tag"])
    elif L["greeting_re"].search(first_line):
        add("FIRST LINE", "WARN", m["fl_greeting"])
    elif len(first_line) > cut:
        add("FIRST LINE", "WARN", m["fl_long"].format(n=len(first_line), cut=cut))
    else:
        add("FIRST LINE", "PASS", m["fl_ok"].format(n=len(first_line)))

    found_concrete = concrete_re.findall(window)
    add("HOOK IS CONCRETE", "PASS" if found_concrete else "WARN",
        m["concrete"].format(n=len(found_concrete))
        + ("" if found_concrete else m["concrete_none"]))

    if len(tags) > HASHTAG_LIMIT:
        add("HASHTAGS", "FAIL", m["tags_over"].format(n=len(tags), cap=HASHTAG_LIMIT))
    elif len(tags) == HASHTAG_LIMIT and filler:
        add("HASHTAGS", "WARN", m["tags_cap_filler"].format(n=len(tags), f=len(filler)))
    elif filler:
        add("HASHTAGS", "WARN", m["tags_filler"].format(n=len(tags), f=len(filler),
                                                        ex=", ".join(filler[:3])))
    else:
        add("HASHTAGS", "PASS", m["tags_ok"].format(n=len(tags))
            + (f": {' '.join(tags)}" if tags else ""))

    if not tags:
        add("TAG PLACEMENT", "PASS", m["place_none"])
    elif any(re.search(r"(?:^|\s)" + re.escape(t) + r"\b", window) for t in tags):
        add("TAG PLACEMENT", "WARN", m["place_window"])
    else:
        add("TAG PLACEMENT", "PASS", m["place_ok"])

    add("LINKS", "WARN" if links else "PASS",
        m["links"].format(n=len(links)) if links else m["links_ok"])

    if len(asks) == 1:
        add("ONE ASK", "PASS", m["ask_one"].format(a=asks[0]))
    elif not asks:
        add("ONE ASK", "WARN", m["ask_none"])
    else:
        add("ONE ASK", "WARN", m["ask_many"].format(n=len(asks), a=", ".join(asks)))

    density = len(emoji) * 100 / max(chars, 1)
    add("EMOJI", "WARN" if density > 4 else "PASS",
        m["emoji"].format(n=len(emoji), d=density) + (m["emoji_heavy"] if density > 4 else ""))

    if keywords:
        # Sin distinguir mayúsculas ni tildes: "diseño web" encuentra "diseno web".
        low, win = fold(stripped), fold(window)
        found = [k for k in keywords if fold(k) in low]
        missing = [k for k in keywords if fold(k) not in low]
        in_window = [k for k in found if fold(k) in win]
        status = "PASS" if not missing else ("WARN" if found else "FAIL")
        add("SEARCH TERMS", status,
            m["search"].format(f=len(found), t=len(keywords))
            + (m["search_window"].format(n=len(in_window)) if found else "")
            + (m["search_missing"].format(m=", ".join(missing)) if missing else ""))

    fails = sum(1 for c in checks if c["status"] == "FAIL")
    warns = sum(1 for c in checks if c["status"] == "WARN")
    verdict = "FIX" if fails else ("REVIEW" if warns else "READY")

    return {
        "lang": lang,
        "characters": chars, "limit": LIMIT, "truncate_at": cut,
        "visible": window, "truncated": truncated,
        "first_line_chars": len(first_line),
        "hashtags": tags, "mentions": mentions, "links": links,
        "emoji": len(emoji), "asks": asks,
        "checks": checks, "verdict": verdict,
    }


def render(a, out=sys.stdout):
    L = DATA[a["lang"]]
    m = L["msg"]
    head = m["head"].format(c=a["characters"], l=a["limit"], h=len(a["hashtags"]),
                            a=len(a["asks"]))
    print("\n" + head, file=out)
    print("=" * max(len(head), 62), file=out)
    render_box(a["visible"], a["truncated"], m, out=out)
    print("", file=out)
    for c in a["checks"]:
        print(f"  {L['status'][c['status']]:<5} {c['label']:<17} {c['detail']}", file=out)
    print("-" * max(len(head), 62), file=out)
    print(f"  {m['verdict']}  {L['verdicts'][a['verdict']]}\n", file=out)


def main():
    ap = argparse.ArgumentParser(description="Revisa el texto de una publicación de Instagram.")
    ap.add_argument("input", nargs="?", default="-", help="archivo con el texto, o - para stdin")
    ap.add_argument("--truncate", type=int, default=TRUNCATE,
                    help=f"caracteres visibles antes de '... más' (por defecto {TRUNCATE})")
    ap.add_argument("--keywords", default="",
                    help="términos separados por comas por los que quieres que te encuentren")
    ap.add_argument("--lang", choices=LANGS, default=DEFAULT_LANG,
                    help=f"idioma de las reglas y los mensajes (por defecto {DEFAULT_LANG})")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    a = analyse(raw, cut=args.truncate, keywords=args.keywords.split(","), lang=args.lang)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0 if a["verdict"] == "READY" else 1)


if __name__ == "__main__":
    main()
