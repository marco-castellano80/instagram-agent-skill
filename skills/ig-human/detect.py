#!/usr/bin/env python3
"""
detect.py - un panel de cinco comprobaciones que puntúa cuánto parece
escrito por una máquina un borrador.

Qué es:  cinco heurísticas locales basadas en las señales que miden los
detectores públicos de IA: variación de longitud de frase, concreción,
vocabulario de relleno, huella tipográfica y voz. Todo se calcula en tu
máquina a partir del texto. No se sube nada.

Qué NO es:  GPTZero, Originality, Copyleaks, Winston ni Turnitin. No llama a
sus API y no puede prometer su veredicto. Los umbrales vienen de la versión
inglesa y NO se han calibrado con textos en español: tómalo como una revisión
de estilo, no como una medida.

Cada comprobación devuelve una nota HUMANA de 0 a 100. Más alto es mejor.

Uso
  python3 detect.py borrador.txt
  pbpaste | python3 detect.py -
  python3 detect.py borrador.txt --json
  python3 detect.py antes.txt despues.txt      # compara dos borradores
  python3 detect.py draft.txt --lang en

Idioma: --lang es (por defecto) o en, o la variable de entorno IG_LANG.
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
LEX = os.path.join(HERE, "slop.json")

# Un punto entre cifras ("18.000") no cierra la frase.
SENT_RE = re.compile(r"(?:[^.!?\n]|(?<=\d)\.(?=\d))+[.!?]*")
WORD_RE = re.compile(r"[^\W\d_][\w'’]*")
NUMBERS = re.compile(r"\b\d[\d,.]*%?\b|[$€£]\s?\d")
UPPER = "A-ZÁÉÍÓÚÑÜÀÈÌÒÙÂÊÎÔÛÇ"
LOWER = "a-záéíóúñüàèìòùâêîôûç"

LANG = {
    "en": {
        "contractions": re.compile(r"\b\w+'(?:s|t|re|ve|ll|d|m)\b", re.IGNORECASE),
        "pronouns": re.compile(r"\b(i|me|my|mine|we|us|our|you|your)\b", re.IGNORECASE),
        "proper": re.compile(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-z]{2,}\b", re.MULTILINE),
        # contracciones, persona, estructuras
        "voice_weights": (0.35, 0.35, 0.30),
        "labels": {"BURSTINESS": "BURSTINESS", "SPECIFICITY": "SPECIFICITY",
                   "SLOP DENSITY": "SLOP DENSITY", "FINGERPRINT": "FINGERPRINT",
                   "VOICE": "VOICE", "TOTAL": "HUMAN SCORE"},
        "verdicts": {"PASS": "PASS", "REVIEW": "REVIEW", "FLAGGED": "FLAGGED"},
        "msg": {
            "short": "too short to judge",
            "empty": "empty",
            "burst": "variation {cv:.2f} across {n} sentences (want 0.55+)",
            "spec": "{h} concrete markers, {d:.1f} per 100 words (want 4+)",
            "slop": "{h} stock terms, {d:.1f} per 100 words",
            "finger": "{i} invisible, {e} em dash, {c} curly quote, {l} ellipsis, {n} hard space",
            "voice": "{c:.1f} contractions, {p:.1f} personal pronouns per 100 words, "
                     "{t} structural tell(s)",
            "title": "AI DETECTION PANEL",
            "uniform_bullets": "uniform-bullets",
            "weakest": "Weakest signal: {c}. Fix that first.",
        },
    },
    "es": {
        # En español no hay contracciones equivalentes ("del" y "al" son
        # obligatorias), así que esa señal no existe y su peso pasa a persona
        # y estructuras.
        "contractions": None,
        "pronouns": re.compile(
            r"\b(yo|me|mi|mí|mis|mío|mía|míos|mías|conmigo|nosotros|nosotras|nos|nuestro"
            r"|nuestra|nuestros|nuestras|tú|tu|tus|te|ti|contigo|tuyo|tuya|tuyos|tuyas|vos"
            r"|usted|ustedes|os|vosotros|vosotras|vuestro|vuestra|vuestros|vuestras)\b",
            re.IGNORECASE),
        "proper": re.compile(r"(?<![.!?]\s)(?<![¿¡])(?<!^)\b[" + UPPER + r"][" + LOWER + r"]{2,}\b",
                             re.MULTILINE),
        "voice_weights": (0.0, 0.50, 0.50),
        "labels": {"BURSTINESS": "RITMO", "SPECIFICITY": "CONCRECIÓN",
                   "SLOP DENSITY": "RELLENO", "FINGERPRINT": "HUELLA",
                   "VOICE": "VOZ", "TOTAL": "NOTA HUMANA"},
        "verdicts": {"PASS": "APTO", "REVIEW": "REVISAR", "FLAGGED": "MARCADO"},
        "msg": {
            "short": "demasiado corto para juzgar",
            "empty": "vacío",
            "burst": "variación {cv:.2f} en {n} frases (ideal 0,55 o más)",
            "spec": "{h} datos concretos, {d:.1f} por cada 100 palabras (ideal 4 o más)",
            "slop": "{h} términos de relleno, {d:.1f} por cada 100 palabras",
            "finger": "{i} invisibles, {e} rayas, {c} comillas curvas, {l} puntos suspensivos, "
                      "{n} espacios duros",
            "voice": "{p:.1f} pronombres personales por cada 100 palabras, "
                     "{t} señal(es) de estructura",
            "title": "PANEL DE DETECCIÓN",
            "uniform_bullets": "viñetas-uniformes",
            "weakest": "Señal más débil: {c}. Arregla esa primero.",
        },
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


def clamp(n):
    return max(0.0, min(100.0, n))


def scale(value, human, machine):
    """Lleva value a 0-100, donde `human` -> 100 y `machine` -> 0."""
    if human == machine:
        return 50.0
    return clamp((value - machine) / (human - machine) * 100)


def sentences(text):
    return [s.strip() for s in SENT_RE.findall(text) if len(s.split()) > 2]


def words(text):
    return WORD_RE.findall(text)


def check_burstiness(text, L):
    """La gente varía mucho la longitud de las frases. Los modelos escriben parejo."""
    lens = [len(s.split()) for s in sentences(text)]
    if len(lens) < 4:
        return 50.0, L["msg"]["short"]
    mean = statistics.mean(lens)
    cv = statistics.pstdev(lens) / mean if mean else 0
    score = scale(cv, human=0.70, machine=0.22)
    return score, L["msg"]["burst"].format(cv=cv, n=len(lens))


def check_specificity(text, L):
    """Números, nombres y sustantivos concretos. El relleno es abstracto."""
    w = words(text)
    if len(w) < 25:
        return 50.0, L["msg"]["short"]
    per100 = 100 / len(w)
    hits = len(NUMBERS.findall(text)) + len(set(L["proper"].findall(text)))
    density = hits * per100
    score = scale(density, human=6.0, machine=0.5)
    return score, L["msg"]["spec"].format(h=hits, d=density)


def check_slop(text, lex, L):
    """Densidad de vocabulario de relleno según el léxico."""
    w = words(text)
    if not w:
        return 50.0, L["msg"]["empty"]
    hits, found = 0, []
    # Las más largas primero, y cada coincidencia se consume: "sígueme para más
    # contenido" cuenta una vez, no tres.
    work = text
    for entry in sorted(lex["words"] + lex["phrases"], key=lambda e: len(e["find"]), reverse=True):
        pattern = re.compile(r"\b" + re.escape(entry["find"]).replace(r"\ ", r"\s+") + r"\b",
                             re.IGNORECASE)
        work, n = pattern.subn("\x00", work)
        if n:
            hits += n
            found.append(entry["find"])
    density = hits * 100 / len(w)
    score = scale(density, human=0.0, machine=4.0)
    detail = L["msg"]["slop"].format(h=hits, d=density)
    if found:
        detail += " (" + ", ".join(sorted(found)[:4]) + (", ..." if len(found) > 4 else "") + ")"
    return score, detail


def check_fingerprint(text, L):
    """Caracteres que un teclado de móvil no produce. Las «» y los ¿ ¡ no cuentan."""
    invisible = sum(1 for c in text if unicodedata.category(c) == "Cf")
    em = text.count("—")
    curly = sum(text.count(c) for c in "‘’“”")
    ellip = text.count("…")
    nbsp = sum(text.count(c) for c in "   ")
    total = invisible * 4 + em * 2 + curly + ellip + nbsp
    per1k = total * 1000 / max(len(text), 1)
    score = scale(per1k, human=0.0, machine=12.0)
    return score, L["msg"]["finger"].format(i=invisible, e=em, c=curly, l=ellip, n=nbsp)


def check_voice(text, lex, L):
    """Contracciones (solo inglés), persona, y las formas por defecto de los modelos."""
    w = words(text)
    if len(w) < 25:
        return 50.0, L["msg"]["short"]
    per100 = 100 / len(w)
    contractions = len(L["contractions"].findall(text)) * per100 if L["contractions"] else 0.0
    person = len(L["pronouns"].findall(text)) * per100
    tells, names = 0, []
    for s in lex["structures"]:
        try:
            n = len(re.compile(s["regex"], re.MULTILINE).findall(text))
        except re.error:
            continue
        if n:
            tells += n
            names.append(s["id"])
    bullets = [len(b.split()) for b in re.findall(r"(?m)^\s*[-*•]\s+(.+)$", text)]
    uniform = (len(bullets) >= 3 and statistics.pstdev(bullets) < 1.6)
    wc, wp, wt = L["voice_weights"]
    score = (scale(contractions, human=3.0, machine=0.0) * wc
             + scale(person, human=8.0, machine=1.0) * wp
             + clamp(100 - tells * 22) * wt)
    if uniform:
        score -= 12
        names.append(L["msg"]["uniform_bullets"])
    detail = L["msg"]["voice"].format(c=contractions, p=person, t=tells)
    if names:
        detail += " [" + ", ".join(names[:4]) + "]"
    return clamp(score), detail


CHECKS = ["BURSTINESS", "SPECIFICITY", "SLOP DENSITY", "FINGERPRINT", "VOICE"]


def run(text, lex, lang=DEFAULT_LANG):
    L = LANG[lang]
    results = {
        "BURSTINESS": check_burstiness(text, L),
        "SPECIFICITY": check_specificity(text, L),
        "SLOP DENSITY": check_slop(text, lex, L),
        "FINGERPRINT": check_fingerprint(text, L),
        "VOICE": check_voice(text, lex, L),
    }
    scores = [results[c][0] for c in CHECKS]
    # La comprobación más débil arrastra el veredicto: basta una señal.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4
    verdict = "PASS" if overall >= 70 and min(scores) >= 55 else (
        "REVIEW" if overall >= 50 else "FLAGGED")
    return results, overall, verdict


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render(results, overall, verdict, lang, label=None, out=sys.stdout):
    L = LANG[lang]
    lab = L["labels"]
    title = L["msg"]["title"] + (f"  -  {label}" if label else "")
    print("\n" + title, file=out)
    print("=" * max(len(title), 62), file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {lab[name]:<13} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<13} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {lab['TOTAL']:<13} {bar(overall)} {overall:5.1f}   {L['verdicts'][verdict]}",
          file=out)
    if verdict != "PASS":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print("\n  " + L["msg"]["weakest"].format(c=lab[weakest]), file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Puntúa cuánto parece escrito por una máquina un borrador.")
    ap.add_argument("input", nargs="?", default="-", help="archivo, o - para stdin")
    ap.add_argument("compare", nargs="?", help="segundo archivo, para ver antes/después")
    ap.add_argument("--lang", choices=LANGS, default=DEFAULT_LANG,
                    help=f"idioma del léxico y los mensajes (por defecto {DEFAULT_LANG})")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lexicon", default=LEX, help="ruta a slop.json")
    ap.add_argument("--lexicon-lang", help="ruta al léxico del idioma (por defecto slop.<lang>.json)")
    args = ap.parse_args()
    lang = args.lang

    lex = load_lexicon(args.lexicon, lang, args.lexicon_lang)
    read = lambda p: sys.stdin.read() if p == "-" else open(p, encoding="utf-8").read()

    targets = [(args.input, read(args.input))]
    if args.compare:
        targets.append((args.compare, read(args.compare)))

    payload = []
    for name, text in targets:
        results, overall, verdict = run(text, lex, lang)
        payload.append({
            "source": name,
            "lang": lang,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "human_score": round(overall, 1),
            "verdict": verdict,
        })

    if args.json:
        print(json.dumps(payload if args.compare else payload[0], indent=2, ensure_ascii=False))
        return

    for (name, text), p in zip(targets, payload):
        results, overall, verdict = run(text, lex, lang)
        render(results, overall, verdict, lang,
               label=os.path.basename(name) if args.compare else None)
    if args.compare:
        a, b = payload
        delta = b["human_score"] - a["human_score"]
        v = LANG[lang]["verdicts"]
        print(f"  {a['human_score']:.1f} {v[a['verdict']]}  ->  "
              f"{b['human_score']:.1f} {v[b['verdict']]}   ({delta:+.1f})\n")

    sys.exit(0 if payload[-1]["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
