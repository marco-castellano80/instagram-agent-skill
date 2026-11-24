#!/usr/bin/env python3
"""
hookscore.py - puntúa la primera línea de un Reel en las cinco cosas que
tienen en común los ganchos fuertes, y ordena un lote de ganchos entre sí.

Qué es:  cinco heurísticas locales, calculadas en tu máquina solo a partir del
texto. Miden propiedades que suelen compartir los ganchos que retienen: una
duración que se dice en menos de tres segundos, un dato concreto, algo en
juego, la carga al principio y no al final, y alguien a quien va dirigido.

Qué NO es:  un predictor de visualizaciones. La versión original (en inglés)
se probó con 74 ganchos reales de vídeo corto. Separa bien un gancho real de
uno escrito mal a propósito (AUC 0,83), pero apenas distingue los aciertos de
un creador de sus fallos (AUC 0,56, donde 0,50 es tirar una moneda). Los
léxicos en español son una adaptación y NO se han calibrado con un corpus
español: úsalo para descartar ganchos flojos, no para elegir ganadores.

Cada comprobación devuelve de 0 a 100. Más alto es mejor.

Uso
  python3 hookscore.py ganchos.txt              # un gancho por línea, ordenados
  python3 hookscore.py --hook "Perdí 18.000 € por una cláusula que faltaba."
  pbpaste | python3 hookscore.py -
  python3 hookscore.py ganchos.txt --json
  python3 hookscore.py ganchos.txt --lang en    # léxico y mensajes en inglés

Idioma: --lang es (por defecto) o en. También se puede fijar con la variable
de entorno IG_LANG.
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

WORD_RE = re.compile(r"[\w$€£%'’-]+")
HASHTAG_RE = re.compile(r"(?:^|\s)#\w+")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")
UPPER = "A-ZÁÉÍÓÚÑÜÀÈÌÒÙÂÊÎÔÛÇ"
LOWER = "a-záéíóúñüàèìòùâêîôûç"


def strip_accents(s):
    """'Perdí' -> 'Perdi'. Los léxicos en español se comparan sin tildes,
    porque en redes la mitad de la gente no las escribe."""
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


# --------------------------------------------------------------------------
# Datos por idioma. Para añadir uno nuevo (p. ej. "it"), copia el bloque "es",
# tradúcelo y añade el código a LANGS. Las palabras de los conjuntos se
# guardan en minúscula y, si "fold" es True, sin tildes.
# --------------------------------------------------------------------------

EN = {
    "fold": False,
    "num_sep": r"(?<=\d),(?=\d)",
    "number_re": re.compile(
        r"[$€£]\s?\d[\d,]*(?:\.\d+)?"
        r"|\b\d[\d,]*(?:\.\d+)?\s?"
        r"(?:%|k\b|x\b|hrs?\b|hours?\b|mins?\b|minutes?\b"
        r"|days?\b|weeks?\b|months?\b|years?\b)?",
        re.IGNORECASE),
    "proper_re": re.compile(r"(?<!^)\b[A-Z][a-z]{2,}\b"),
    # Spoken hooks say their numbers out loud. "one" and "first" are
    # deliberately absent: they are filler far more often than a quantity.
    "spoken_numbers": {
        "zero", "two", "three", "four", "five", "six", "seven", "eight", "nine",
        "ten", "eleven", "twelve", "fifteen", "twenty", "thirty", "forty", "fifty",
        "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million",
        "billion", "dozen", "half", "twice", "triple",
    },
    "spoken_number_re": None,
    "money_words": {
        "dollars", "dollar", "bucks", "grand", "percent", "cents", "euros", "euro",
        "millionaire", "billionaire", "revenue", "profit", "salary", "rent",
    },
    "stakes": {
        "stop", "never", "wrong", "mistake", "mistakes", "lost", "lose", "losing",
        "cost", "costs", "broke", "broken", "failed", "failure", "fail", "nobody",
        "no", "not", "don't", "dont", "doesn't", "didn't", "can't", "won't",
        "quit", "quitting", "fired", "deleted", "delete", "killed", "kills", "kill",
        "replaced", "replaces", "cut", "beat", "free", "paid", "charged", "hired",
        "saved", "first",
        "banned", "illegal", "worst", "hate", "hated", "wasted", "waste", "scam",
        "lie", "lied", "lying", "truth", "secret", "hidden", "stole", "stolen",
        "before", "until", "instead", "but", "except", "unless", "problem",
        "risk", "danger", "warning", "regret", "wish", "should", "shouldn't",
        "still", "already", "only", "without", "versus", "vs", "actually",
    },
    "weak_openers": [
        "so", "ok", "okay", "hey", "hi", "hello", "guys", "yo", "alright",
        "welcome", "today", "basically", "honestly", "look", "listen", "um",
        "just", "let", "lets", "let's", "i wanted", "i want", "one of",
        "have you", "did you", "do you", "are you", "in this", "in today",
        "the thing", "a lot", "there is", "there are", "this is", "it is",
        "as a", "when it", "if you've", "you know",
    ],
    "imperatives": {
        "stop", "steal", "copy", "delete", "try", "watch", "read", "save",
        "use", "build", "make", "write", "send", "take", "start", "quit",
        "never", "always", "don't", "dont", "do", "put", "run", "check",
    },
    "you_re": re.compile(r"\b(you|your|you're|youre|yourself)\b"),
    "you_words": set(),
    "me_re": re.compile(r"\b(i|my|me|we|our)\b"),
    "me_words": set(),
    "me_suffix_re": None,
    "dealbreakers": [
        (re.compile(r"(?i)^\s*(?:stop scrolling|don'?t scroll)"),
         "Opens with \"stop scrolling\". Asking for attention proves you have not earned it."),
        (re.compile(r"(?i)\b(?:in (?:this|today'?s) (?:video|reel)|i'?m going to show you|i'?ll show you how)\b"),
         "Video preamble. Delete it and open on the payoff."),
        (re.compile(r"(?i)^\s*(?:hey |hi |what'?s up |welcome )"),
         "Greeting. Nobody came to the feed to be greeted."),
        (HASHTAG_RE,
         "Hashtag in the hook. Hashtags belong at the bottom of the caption, if anywhere."),
        (EMOJI_RE,
         "Emoji in the hook. On-screen text at hook size has room for words or for an emoji, not both."),
    ],
    "labels": {"LENGTH": "LENGTH", "SPECIFICITY": "SPECIFICITY", "STAKES": "STAKES",
               "FRONTLOAD": "FRONTLOAD", "ADDRESS": "ADDRESS", "TOTAL": "HOOK SCORE"},
    "verdicts": {"STRONG": "STRONG", "OK": "OK", "WEAK": "WEAK"},
    "msg": {
        "length": "{n} words, {chars} chars, ~{secs:.1f}s spoken (want 5-12 words)",
        "spec_hits": "{hits} concrete marker(s)",
        "spec_none": " - no number, no name, nothing checkable",
        "price": "a price",
        "stakes": "{n} tension marker(s)",
        "stakes_none": " - nothing is at stake in this line",
        "empty": "empty",
        "no_payload": "no payload word anywhere in the line",
        "payload_ok": "payload at word {k}",
        "payload_mid": "payload at word {k}, could move forward",
        "payload_late": "payload at word {k}, too late",
        "weak_opener": "; weak opener \"{w}\"",
        "addr_you": "speaks to the viewer",
        "addr_imp": "imperative opener (\"{w}\")",
        "addr_me": "first person, no viewer named",
        "addr_none": "third person, nobody in the room",
        "title_one": "HOOK SCORE",
        "title_table": "HOOK RANKING",
        "dealbreaker": "DEALBREAKER",
        "dealbreaker_row": "dealbreaker",
        "weakest_one": "Weakest property: {c}. Fix that one and re-run.",
        "weakest_row": "weakest",
        "footer": "Shoot the top one. If the top one is under 50, none of these are the hook.",
        "nothing": "nothing to score",
    },
}

ES = {
    "fold": True,
    # "18.000", "18,000" y "2,5" cuentan como una sola palabra dicha.
    "num_sep": r"(?<=\d)[.,](?=\d)|(?<=\d)\s+(?=[€%])",
    "number_re": re.compile(
        r"[$€£]\s?\d[\d.,]*"
        r"|\b\d[\d.,]*\s?"
        r"(?:€|%|k\b|x\b|h\b|horas?\b|min\b|minutos?\b|seg\b|segundos?\b"
        r"|d[ií]as?\b|semanas?\b|mes(?:es)?\b|años?\b|euros?\b|d[oó]lares\b"
        r"|pesos\b|mil\b|millones\b)?",
        re.IGNORECASE),
    # Una mayúscula detrás de ¿ o ¡ es inicio de frase, no un nombre propio.
    "proper_re": re.compile(r"(?<!^)(?<![¿¡])(?<![.!?] )(?<![.!?]\n)\b[" + UPPER + r"]["
                           + LOWER + r"]{2,}\b"),
    # Números dichos en voz alta. "uno", "una" y "primer" no están a propósito:
    # casi siempre son relleno, no una cantidad.
    "spoken_numbers": {
        "cero", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve",
        "diez", "once", "doce", "trece", "catorce", "quince", "dieciseis",
        "diecisiete", "dieciocho", "diecinueve", "veinte", "treinta", "cuarenta",
        "cincuenta", "sesenta", "setenta", "ochenta", "noventa", "cien", "ciento",
        "cientos", "doscientos", "trescientos", "cuatrocientos", "quinientos",
        "seiscientos", "setecientos", "ochocientos", "novecientos", "mil",
        "millon", "millones", "docena", "mitad", "doble", "triple",
    },
    "spoken_number_re": re.compile(r"^(?:veinti\w+|treinta y \w+)$"),
    "money_words": {
        "euros", "euro", "dolares", "dolar", "pesos", "pavos", "lucas", "centimos",
        "centavos", "millonario", "millonaria", "facturacion", "facture", "facturo",
        "ingresos", "beneficio", "beneficios", "sueldo", "salario", "alquiler",
    },
    # Palabras que ponen algo en juego. Sin tildes.
    "stakes": {
        "nunca", "jamas", "mal", "error", "errores", "equivocado", "equivocada",
        "equivoque", "equivocas", "perdi", "pierdo", "pierdes", "perder", "perdiendo",
        "perdido", "perdida", "perdidas", "perdimos", "cuesta", "costo", "coste",
        "costar", "costaba", "quiebra", "arruinado", "arruinada", "arruine",
        "fracase", "fracaso", "fracasar", "fracasan", "fallo", "falle", "fallar",
        "nadie", "no", "ni", "deja", "dejad", "deje", "dejar", "dejalo", "despedido", "despedida",
        "despidieron", "despedi", "borre", "borra", "borrar", "borralo", "elimine",
        "eliminar", "elimina", "mata", "mato", "matar", "matando", "muere", "mueren",
        "murio", "muerto", "muerta", "reemplace",
        "reemplaza", "reemplazo", "sustitui", "sustituye", "sustituyo", "gratis",
        "pague", "pagar", "pagas", "pagado", "pagando", "cobre", "cobrar", "cobras",
        "contrate", "contratar", "ahorre", "ahorrar", "ahorras", "primero",
        "primera", "primeros", "primeras", "prohibido", "prohibida", "ilegal",
        "peor", "peores", "odio", "odiaba", "odie", "desperdicie", "desperdiciar",
        "estafa", "timo", "mentira", "menti", "mienten", "mintiendo", "verdad",
        "secreto", "secretos", "oculto", "oculta", "robe", "robado", "robar", "roba",
        "antes", "hasta", "pero", "excepto", "salvo", "problema", "problemas",
        "riesgo", "peligro", "cuidado", "ojo", "aviso", "arrepiento", "arrepenti",
        "ojala", "deberia", "deberias", "todavia", "aun", "ya", "solo", "solamente",
        "sin", "versus", "vs", "realmente",
    },
    # Aperturas que gastan el primer segundo sin decir nada. Se comparan como
    # palabras completas, sin tildes, contra las dos primeras palabras.
    "weak_openers": [
        "hola", "buenas", "bueno", "pues", "vale", "ok", "okay", "hey", "ey",
        "chicos", "chicas", "gente", "amigos", "amigas", "bienvenidos",
        "bienvenidas", "bienvenido", "bienvenida", "hoy", "basicamente",
        "sinceramente", "honestamente", "la verdad", "mira", "mirad", "escucha",
        "escuchad", "eh", "em", "ehm", "entonces", "asi que", "a ver", "vamos a",
        "voy a", "quiero", "queria", "uno de", "una de", "alguna vez", "has",
        "habeis", "sabias", "te has", "os habeis", "en este", "esto es", "es que",
        "hay", "ya sabes", "que tal", "si alguna",
    ],
    "imperatives": {
        "deja", "dejad", "roba", "robad", "copia", "borra", "elimina", "prueba",
        "lee", "guarda", "usa", "haz", "crea", "escribe", "manda", "envia", "toma",
        "empieza", "nunca", "siempre", "no", "pon", "revisa", "apunta", "olvida",
        "evita", "cambia", "sube", "cobra", "publica", "graba", "corta", "quita",
        "aprende", "fijate", "di", "pide", "piensa", "imagina", "dejad", "ve",
    },
    # Imperativo con pronombre pegado: "róbame", "guárdalo", "dímelo".
    "enclitic_re": re.compile(r"^(\w{2,}?)(?:me|te|lo|la|los|las|le|les|nos|melo|mela|telo|tela)$"),
    # Español omite el pronombre, así que se buscan también formas verbales de
    # segunda persona. Se comparan en minúscula CON tildes ("estás" sí, "estas"
    # es "these").
    "you_re": re.compile(r"\b(tú|tu|tus|te|ti|contigo|usted|ustedes|os|vosotros|vosotras"
                         r"|vuestro|vuestra|vuestros|vuestras)\b"),
    "you_words": {
        "eres", "estás", "tienes", "haces", "sabes", "puedes", "quieres", "necesitas",
        "vendes", "cobras", "sigues", "crees", "piensas", "vas", "das", "dices",
        "usas", "publicas", "subes", "pierdes", "trabajas", "buscas", "llevas",
        "has", "hayas", "deberías", "deberias", "podrías", "podrias", "harías",
        "quieras", "tengas", "seas", "estés", "hiciste", "perdiste", "ganaste",
        "cobraste", "pagaste", "sabías", "sabias", "habéis", "sois", "tenéis",
        "hacéis", "sabéis", "queréis", "podéis",
        # voseo
        "vos", "sos", "tenés", "sabés", "querés", "podés", "hacés", "vendés", "cobrás",
        "necesitás", "estás", "pensás", "creés",
    },
    "me_re": re.compile(r"\b(yo|mi|mis|me|mí|conmigo|nosotros|nosotras|nuestro|nuestra"
                        r"|nuestros|nuestras|nos)\b"),
    "me_words": {
        "tengo", "hago", "cobro", "vendo", "pierdo", "gano", "creo", "pienso", "sé",
        "soy", "estoy", "voy", "llevo", "he", "había", "hice", "tuve", "fui", "dije",
        "puse", "vine", "quise", "supe", "pude", "hemos", "perdimos", "ganamos",
        "cobramos", "pagamos", "facturamos",
    },
    # Pretérito en primera persona: "perdí", "gané", "cobré".
    "me_suffix_re": re.compile(r"^\w{2,}[éí]$"),
    "me_suffix_skip": {"aquí", "allí", "ahí", "así", "sí", "qué", "café", "bebé",
                       "rubí", "esquí", "maní", "ají", "menú", "porqué"},
    "dealbreakers": [
        (re.compile(r"(?i)^\s*(?:deja de hacer scroll|para de hacer scroll|no hagas scroll"
                    r"|deja de deslizar|no sigas (?:bajando|deslizando)"
                    r"|espera,? no (?:hagas scroll|deslices|pases))"),
         "Abre con «deja de hacer scroll». Pedir atención demuestra que no te la has ganado."),
        (re.compile(r"(?i)\b(?:en este (?:v[ií]deo|reel)|en el (?:v[ií]deo|reel) de hoy"
                    r"|hoy (?:te|os|les) voy a (?:enseñar|ensenar|mostrar|contar|explicar)"
                    r"|(?:te|os|les) voy a (?:enseñar|ensenar|mostrar|explicar) c[oó]mo)\b"),
         "Preámbulo de vídeo. Bórralo y abre con el resultado."),
        (re.compile(r"(?i)^\s*[¡¿]?\s*(?:hola|buenas|qu[eé] tal|hey|ey|bienvenid[oa]s?)\b"),
         "Saludo. Nadie entra al feed para que le saluden."),
        (HASHTAG_RE,
         "Hashtag en el gancho. Los hashtags van al final del texto, si es que van."),
        (EMOJI_RE,
         "Emoji en el gancho. El texto en pantalla a tamaño de gancho tiene sitio para "
         "palabras o para un emoji, no para las dos cosas."),
    ],
    "labels": {"LENGTH": "DURACIÓN", "SPECIFICITY": "CONCRECIÓN", "STAKES": "TENSIÓN",
               "FRONTLOAD": "ARRANQUE", "ADDRESS": "A QUIÉN", "TOTAL": "NOTA GANCHO"},
    "verdicts": {"STRONG": "FUERTE", "OK": "OK", "WEAK": "DÉBIL"},
    "msg": {
        "length": "{n} palabras, {chars} caracteres, ~{secs:.1f}s dicho (ideal 5-12 palabras)",
        "spec_hits": "{hits} dato(s) concreto(s)",
        "spec_none": " - ni número, ni nombre, nada comprobable",
        "price": "un precio",
        "stakes": "{n} marcador(es) de tensión",
        "stakes_none": " - en esta frase no hay nada en juego",
        "empty": "vacío",
        "no_payload": "ninguna palabra con carga en toda la frase",
        "payload_ok": "carga en la palabra {k}",
        "payload_mid": "carga en la palabra {k}, podría ir antes",
        "payload_late": "carga en la palabra {k}, demasiado tarde",
        "weak_opener": "; apertura débil «{w}»",
        "addr_you": "le habla al espectador",
        "addr_imp": "abre con imperativo («{w}»)",
        "addr_me": "primera persona, sin espectador",
        "addr_none": "tercera persona, no hay nadie en la sala",
        "title_one": "NOTA DEL GANCHO",
        "title_table": "RANKING DE GANCHOS",
        "dealbreaker": "DESCALIFICA",
        "dealbreaker_row": "descalifica",
        "weakest_one": "Propiedad más débil: {c}. Arregla esa y vuelve a pasarlo.",
        "weakest_row": "más débil",
        "footer": "Graba el primero. Si el primero está por debajo de 50, ninguno de estos "
                  "es el gancho.",
        "nothing": "no hay nada que puntuar",
    },
}

DATA = {"en": EN, "es": ES}
CHECKS = ["LENGTH", "SPECIFICITY", "STAKES", "FRONTLOAD", "ADDRESS"]


def clamp(n):
    return max(0.0, min(100.0, n))


def words(text, lang=DEFAULT_LANG):
    # "18.000 €" es una palabra cuando se dice, así que aquí también.
    return WORD_RE.findall(re.sub(DATA[lang]["num_sep"], "", text))


def norm(token, L):
    t = token.lower().strip("'’")
    return strip_accents(t) if L["fold"] else t


def is_spoken_number(tok, L):
    if tok in L["spoken_numbers"] or tok in L["money_words"]:
        return True
    return bool(L["spoken_number_re"] and L["spoken_number_re"].match(tok))


def check_length(text, L, lang):
    """Un gancho tiene que llegar antes de que se mueva el pulgar."""
    n = len(words(text, lang))
    secs = n / 2.75                      # ~165 palabras por minuto, dicho
    chars = len(text.strip())
    if 5 <= n <= 12:
        score = 100.0
    elif n < 5:
        score = clamp(100 - (5 - n) * 20)
    else:
        score = clamp(100 - (n - 12) * 11)
    if chars > 60:                       # dos líneas de texto grande en pantalla
        score -= 12
    return clamp(score), L["msg"]["length"].format(n=n, chars=chars, secs=secs)


def check_specificity(text, L, lang):
    """Una cosa concreta gana a tres abstractas."""
    nums = [n.strip() for n in L["number_re"].findall(text) if n.strip()]
    propers = set(L["proper_re"].findall(text))
    low = [norm(w, L) for w in words(text, lang)]
    spoken = [w for w in low if is_spoken_number(w, L)]
    hits = len(nums) + len(propers) + len(spoken)
    score = 15.0 if hits == 0 else clamp(45 + hits * 30)
    found = ", ".join(nums[:2] + sorted(propers)[:2] + spoken[:2])
    return score, (L["msg"]["spec_hits"].format(hits=hits)
                   + (f": {found}" if found else L["msg"]["spec_none"]))


def check_stakes(text, L, lang):
    """Tensión, coste, negación. Algo que el espectador podría perder."""
    w = [norm(x, L) for x in words(text, lang)]
    markers = sorted(set(x for x in w if x in L["stakes"]))
    if re.search(r"[$€£]\s?\d|\d\s?(?:€|euros?\b)", text, re.IGNORECASE):
        markers.append(L["msg"]["price"])
    n = len(markers)
    score = {0: 20.0, 1: 70.0}.get(n, 100.0)
    detail = L["msg"]["stakes"].format(n=n) + (f": {', '.join(markers[:4])}" if markers
                                               else L["msg"]["stakes_none"])
    return clamp(score), detail


def check_frontload(text, L, lang):
    """La palabra interesante no puede estar en la posición nueve."""
    w = words(text, lang)
    if not w:
        return 0.0, L["msg"]["empty"]
    low = [norm(x, L) for x in w]
    opener = " ".join(low[:2])
    penalty, hit_opener = 0, None
    for weak in L["weak_openers"]:
        # Palabra completa: "yo" no debe atrapar "your", ni "hi" a "his".
        if opener == weak or opener.startswith(weak + " ") or low[0] == weak:
            penalty, hit_opener = 30, weak
            break
    payload = None
    for i, token in enumerate(low):
        if (token in L["stakes"] or is_spoken_number(token, L)
                or L["number_re"].match(w[i]) or (i and L["proper_re"].match(w[i]))):
            payload = i
            break
    if payload is None:
        base, where = 30.0, L["msg"]["no_payload"]
    elif payload <= 3:
        base, where = 100.0, L["msg"]["payload_ok"].format(k=payload + 1)
    elif payload <= 6:
        base, where = 70.0, L["msg"]["payload_mid"].format(k=payload + 1)
    else:
        base, where = 40.0, L["msg"]["payload_late"].format(k=payload + 1)
    detail = where + (L["msg"]["weak_opener"].format(w=hit_opener) if hit_opener else "")
    return clamp(base - penalty), detail


def check_address(text, L, lang):
    """Dirigido a un espectador, o flotando en el aire."""
    low = text.lower()
    toks = [x.lower().strip("'’") for x in words(text, lang)]
    if L["you_re"].search(low) or any(t in L["you_words"] for t in toks):
        return 100.0, L["msg"]["addr_you"]
    first = norm(toks[0], L) if toks else ""
    enc = L.get("enclitic_re")
    stem = enc.match(first).group(1) if enc and enc.match(first) else None
    if first in L["imperatives"] or (stem and stem in L["imperatives"]):
        return 90.0, L["msg"]["addr_imp"].format(w=toks[0])
    me_suffix = L.get("me_suffix_re")
    skip = L.get("me_suffix_skip", set())
    if (L["me_re"].search(low) or any(t in L["me_words"] for t in toks)
            or (me_suffix and any(me_suffix.match(t) and t not in skip for t in toks))):
        return 70.0, L["msg"]["addr_me"]
    return 35.0, L["msg"]["addr_none"]


def run(text, lang=DEFAULT_LANG):
    L = DATA[lang]
    results = {
        "LENGTH": check_length(text, L, lang),
        "SPECIFICITY": check_specificity(text, L, lang),
        "STAKES": check_stakes(text, L, lang),
        "FRONTLOAD": check_frontload(text, L, lang),
        "ADDRESS": check_address(text, L, lang),
    }
    flags = [msg for pattern, msg in L["dealbreakers"] if pattern.search(text)]
    scores = [results[c][0] for c in CHECKS]
    # La propiedad más débil limita el gancho: basta una mala para que el
    # pulgar siga bajando.
    overall = clamp(statistics.mean(scores) * 0.6 + min(scores) * 0.4 - len(flags) * 15)
    verdict = "STRONG" if overall >= 70 and min(scores) >= 55 and not flags else (
        "OK" if overall >= 50 else "WEAK")
    return results, overall, verdict, flags


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render_one(text, results, overall, verdict, flags, lang, out=sys.stdout):
    L = DATA[lang]
    lab, m = L["labels"], L["msg"]
    print("\n" + m["title_one"], file=out)
    print("=" * 62, file=out)
    print(f"  \"{text.strip()}\"\n", file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {lab[name]:<13} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<13} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {lab['TOTAL']:<13} {bar(overall)} {overall:5.1f}   {L['verdicts'][verdict]}",
          file=out)
    for f in flags:
        print(f"\n  {m['dealbreaker']}  {f}", file=out)
    if verdict != "STRONG":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print("\n  " + m["weakest_one"].format(c=lab[weakest]), file=out)
    print("", file=out)


def render_table(rows, lang, out=sys.stdout):
    L = DATA[lang]
    lab, m = L["labels"], L["msg"]
    print("\n" + m["title_table"] + "\n" + "=" * 78, file=out)
    for i, r in enumerate(rows, 1):
        mark = "->" if i == 1 else "  "
        hook = r["hook"] if len(r["hook"]) <= 62 else r["hook"][:59] + "..."
        print(f"{mark} {r['score']:5.1f} {L['verdicts'][r['verdict']]:<7} {hook}", file=out)
        print(f"        {m['weakest_row']}: {lab[r['weakest']]} "
              f"({r['checks'][r['weakest']]['score']:.0f})", file=out)
        for f in r["flags"]:
            print(f"        {m['dealbreaker_row']}: {f}", file=out)
    print("\n" + m["footer"] + "\n", file=out)


def main():
    ap = argparse.ArgumentParser(description="Puntúa un gancho de Reel en cinco propiedades.")
    ap.add_argument("input", nargs="?", default="-", help="archivo con un gancho por línea, o -")
    ap.add_argument("--hook", help="puntúa un solo gancho dado en la línea de comandos")
    ap.add_argument("--lang", choices=LANGS, default=DEFAULT_LANG,
                    help=f"idioma del léxico y los mensajes (por defecto {DEFAULT_LANG})")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    lang = args.lang

    if args.hook:
        lines = [args.hook]
    else:
        raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
    if not lines:
        print(DATA[lang]["msg"]["nothing"], file=sys.stderr)
        sys.exit(2)

    payload = []
    for line in lines:
        results, overall, verdict, flags = run(line, lang)
        payload.append({
            "hook": line,
            "lang": lang,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "weakest": min(CHECKS, key=lambda c: results[c][0]),
            "flags": flags,
            "score": round(overall, 1),
            "verdict": verdict,
        })

    if args.json:
        print(json.dumps(payload if len(payload) > 1 else payload[0], indent=2, ensure_ascii=False))
        return

    if len(payload) == 1:
        results, overall, verdict, flags = run(lines[0], lang)
        render_one(lines[0], results, overall, verdict, flags, lang)
    else:
        render_table(sorted(payload, key=lambda r: -r["score"]), lang)

    sys.exit(0 if max(p["score"] for p in payload) >= 70 else 1)


if __name__ == "__main__":
    main()
