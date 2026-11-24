# La skill de Instagram para Claude, en español

Trece skills de Claude que llevan una cuenta de Instagram, adaptadas al
español. Gratis, MIT, sin registro, sin clave de API, sin nada que conectar.

Es una adaptación del pack original en inglés de Jake Schincariol
([instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill)).
Las skills escriben en español, los cinco scripts leen español por defecto y el
inglés sigue disponible con `--lang en`.

Una escribe tus reels a partir de 26 fórmulas de gancho y puntúa el gancho
antes de que gastes una toma. Otra busca los reels que están funcionando en tu
nicho y los ordena por cuánto superaron a su propia cuenta. Otra escribe el
texto y te enseña exactamente lo que muestra el feed antes del «... más». Otra
puntúa tu perfil sobre 100 y reescribe lo que pierde puntos. Otra planifica la
semana.

Y una es el humanizador: quita las rayas, el vocabulario de relleno y los
caracteres invisibles de un borrador, y luego puntúa lo que queda con un panel
de cinco comprobaciones antes de que lo veas.

**No se publica nada hasta que tú digas que sí.** Estas skills escriben. Tú
publicas.

## Instalación

En Claude Code, desde una copia de este repositorio:

```bash
cp -r skills/ig-* ~/.claude/skills/
```

O como plugin, desde tu fork en GitHub:

```
/plugin marketplace add TU_USUARIO/instagram-agent-skill
/plugin install instagram-agent
```

Para un solo proyecto en lugar de global: copia las mismas carpetas en
`.claude/skills/` del repositorio. ¿Sin Claude Code? Pega cualquier `SKILL.md`
al principio de un chat y funciona como un modo. Pierdes los cinco scripts de
Python, que son buena parte del valor de `/ig-reel` y `/ig-human`, pero el resto
funciona.

Después dedica diez minutos a `templates/voice.md`. Cópialo en
`~/.claude/instagram/voice.md` y rellénalo, o pásale a Claude tres de tus reels
y dile «escribe mi voice.md a partir de estos». Ahí se fija también la variante
(España, Latinoamérica o neutro) y si hablas de tú, vos o usted. Todas las
skills leen ese archivo.

## Las trece

| comando | qué hace |
| --- | --- |
| `/ig-reel` | Una idea convertida en reel. Tres ganchos a partir de [26 fórmulas](skills/ig-reel/hooks.es.json), puntuados, y luego el guion, el texto en pantalla y una escaleta cronometrada. |
| `/ig-viral` | Busca lo que funciona en tu nicho, lo ordena por múltiplo sobre la mediana de cada cuenta, pone nombre a la fórmula y escribe el swipe file. |
| `/ig-caption` | El texto de la publicación, revisado. Te enseña los 125 caracteres que muestra el feed antes del toque. |
| `/ig-carousel` | Carruseles. La portada que se gana el deslizamiento, el texto de cada diapositiva y los archivos de 1080x1350. |
| `/ig-story` | La secuencia diaria de historias, qué sticker hace qué trabajo y el embudo de DM que empieza cuando la otra persona se mueve primero. |
| `/ig-profile` | Puntúa tu perfil con una [rúbrica de 12 puntos](skills/ig-profile/rubric.es.json) sobre 100 y lo reescribe empezando por lo que más pierde. |
| `/ig-plan` | La semana. Qué publicar, en qué formato, cuándo, y las 10 cuentas con las que interactuar. |
| `/ig-human` | El humanizador. Dos scripts que se ejecutan de verdad. |
| `/ig-comment` | Comentarios en publicaciones de otros. Nueve tipos, elegidos según lo que es la publicación. Nunca «🔥🔥🔥». |
| `/ig-reply` | Los comentarios bajo tu propia publicación. Los clasifica y responde en orden de valor. |
| `/ig-dm` | La entrega por palabra clave, el primer mensaje, la propuesta de colaboración y los dos seguimientos. Dos. |
| `/ig-repurpose` | Un vídeo, pódcast o newsletter convertido en una semana de reels y carruseles que se sostienen solos. |
| `/ig-audit` | Análisis de lo que ya has publicado. Ordena por múltiplo sobre la mediana y envíos por alcance, no por visualizaciones. |

## Los cinco scripts

Sin dependencias, sin red, sin subir nada. Se ejecutan en tu máquina, sobre tu
texto. Todos aceptan `--lang es` (por defecto) o `--lang en`, o la variable de
entorno `IG_LANG`.

### Ganchos

```bash
python3 hookscore.py ganchos.txt            # ordena tus opciones
python3 beats.py guion.txt --target 30      # cronométralo antes de grabarlo
```

```
RANKING DE GANCHOS
==============================================================================
->  87.0 FUERTE  Nadie te dice que tus primeros 30 reels tienen que fracasar.
        más débil: CONCRECIÓN (75)
    81.4 FUERTE  Perdí 18.000 € por una cláusula que faltaba en el contrato.
        más débil: A QUIÉN (70)
    53.0 OK      Deja de hacer scroll si quieres crecer en Instagram en 2026 🔥
        más débil: TENSIÓN (70)
        descalifica: Abre con «deja de hacer scroll». Pedir atención demuestra que no te la has ganado.
        descalifica: Emoji en el gancho. El texto en pantalla a tamaño de gancho tiene sitio para palabras o para un emoji, no para las dos cosas.
     5.4 DÉBIL   Hola a todos, hoy quiero hablaros de estrategia de contenido
        más débil: ARRANQUE (0)
        descalifica: Saludo. Nadie entra al feed para que le saluden.
```

`beats.py` calcula cuánto se tarda en decir cada línea, las apila en códigos de
tiempo y marca las cuatro cosas que matan un reel en la edición: un gancho que
pasa de tres segundos, un bloque lo bastante largo como para que el espectador
se vaya, una racha de líneas sin nada concreto y la falta de un bucle que
vuelva a la primera línea.

```
ESCALETA  ·  54 palabras  ·  ~19.6s a 165 ppm  ·  objetivo 30s
========================================================================
  0:00.0   2.5s  GANCHO      Perdí 18.000 € por una cláusula que faltaba.
  0:02.5   6.9s              Esta es la cláusula exacta que ahora pongo en cada contrato...
                             ^ 6.9s en un solo bloque
  0:09.4   3.6s  MITAD       Sección 4. Pago a la entrega, no a la aprobación.
  0:13.1   3.6s              La aprobación es una sensación. La entrega es una fecha.
  0:16.7   2.9s  CTA         Ese cambio de una palabra me vale 18.000 €.
------------------------------------------------------------------------
  - El/los bloque(s) 2 pasan de 4s. Parte la frase o cambia lo que hay en pantalla dentro de ella.
  - Bucle: el último bloque repite «18.000€» del gancho. Las segundas vistas son alcance gratis.
  - 10.4s por debajo del objetivo. Añade 28 palabras o grábalo corto. Corto suele ser lo correcto.
```

El ritmo por defecto es 165 palabras por minuto y no está calibrado para
español. Cronométrate una vez leyendo un guion y pásalo con `--wpm`.

### El texto de la publicación

```bash
python3 caption.py texto.txt --keywords "diseño web,contratos freelance"
```

Instagram muestra unos 125 caracteres del texto en el feed y esconde el resto
detrás de un toque. Casi todos los textos que fallan, fallan ahí. Así que lo
primero que imprime es esa ventana, en un recuadro, tal como la lee un
desconocido haciendo scroll:

```
  LO QUE ENSEÑA EL FEED
  +------------------------------------------------------+
  | Perdí 18.000 € por una cláusula que faltaba en un    |
  | contrato, y lo peor es que me lo había leído dos     |
  | veces antes de firmarlo.                             |
  +--------------------------------------------- ... más +

  OK    LONGITUD          432 / 2200 caracteres
  OK    PRIMERA LÍNEA     123 caracteres, se ve entera
  OK    GANCHO CONCRETO   1 número(s) o nombre(s) en la ventana visible
  OK    HASHTAGS          3 hashtag(s): #freelance #contratos #diseñoweb
  OK    UNA PETICIÓN      una llamada a la acción: comentar una palabra clave
  AVISO BÚSQUEDA          1/2 presentes, 0 en la ventana visible. Faltan: contratos freelance
```

Aplica el tope actual de **cinco hashtags por publicación**, no treinta, según
el repo original (Instagram lo redujo el 18 de diciembre de 2025). Reconoce las
peticiones habituales en español («Comenta CONTRATO», «guárdalo», «escríbeme
por privado», «link en la bio»), los hashtags con tildes y ñ, y compara los
términos de búsqueda sin distinguir tildes.

### El humanizador

```bash
python3 humanize.py borrador.txt --report      # límpialo y enseña cada cambio
python3 detect.py borrador.txt                  # puntúalo, cinco comprobaciones
python3 detect.py antes.txt despues.txt         # demuestra la diferencia
```

**Lo que se quita solo:**

- **Caracteres invisibles.** Espacios y uniones de ancho cero, word joiners,
  guiones blandos, marcas de orden de bytes, caracteres de etiqueta Unicode,
  espacios duros y estrechos. Tu teclado no los produce.
- **Tipografía.** Raya a coma, semirraya a guion, comillas curvas a rectas,
  puntos suspensivos a tres puntos. Las comillas angulares «» y los signos ¿ ¡
  no se tocan: son español correcto.
- **El léxico.** [`slop.es.json`](skills/ig-human/slop.es.json) reúne casi 300
  palabras y frases de relleno en español con su sustitución normal
  («sumérgete en», «potenciar», «crucial», «en el mundo actual», «juega un
  papel fundamental», «al siguiente nivel», «sin lugar a dudas»), con las
  formas de género y número para no romper la concordancia. El último bloque es
  de Instagram: «deja de hacer scroll», «en el vídeo de hoy», «sígueme para
  más», «etiqueta a alguien que necesite esto», «al algoritmo le encanta». Está
  pensado para que lo edites.

**Lo que se señala en lugar de arreglarse:** «No es solo X, es Y», «no solo X,
sino también Y», tríadas, el preámbulo de vídeo, viñetas con emoji, tres
palabras gritadas seguidas, muros de hashtags, cebos de seguir o etiquetar,
frases de longitud uniforme y tres señales propias del español: la pregunta
retórica de apertura («¿Alguna vez te has preguntado...?»), las mayúsculas a la
inglesa en títulos («Cómo Hacer Crecer Tu Marca») y las exclamaciones en
cadena.

En español no existen contracciones como en inglés, así que la comprobación de
VOZ mide pronombres personales y estructuras. **Los umbrales del panel vienen de
la versión inglesa y no se han calibrado con textos en español.**

### El swipe file

```bash
python3 swipe.py capturados.tsv --out ~/.claude/instagram/swipe.md
```

Las visualizaciones brutas no son una prueba. Una cuenta de 2.000.000 de
seguidores que hace 400.000 tuvo un martes tranquilo. Una cuenta de 4.000 que
hace 400.000 encontró algo. `swipe.py` ordena por el múltiplo sobre la mediana
de cada cuenta, pone nombre a la fórmula del gancho y enseña qué separa el
tercio de arriba del de abajo. Acepta cabeceras en español (`cuenta`,
`seguidores`, `mediana`, `vistas`, `gancho`) y cifras como `412.000`, `412K`,
`412 mil` o `1,2 M`.

```
SWIPE FILE  ·  4 reels  ·  4 cuentas  ·  referencia: mediana de la cuenta
==============================================================================
    60.0x  gancho  76  #9  Róbalo                 @c                 180.000
           "róbame este seguimiento de cuatro líneas que me costó dos años"
    37.5x  gancho  87  #3  Nadie te lo dice       @a                 412.000
           "nadie te dice que tus primeros 30 reels tienen que fracasar"
     1.3x  gancho  13  -   sin clasificar         @b               1.200.000
           "en este vídeo te enseño mi rutina de mañana"
```

## Lo que está medido y lo que no

El autor original midió el puntuador de ganchos con **74 ganchos reales en
inglés** (los tres primeros segundos de los Shorts con mejor y peor rendimiento
de cinco canales de YouTube). Resultados: detecta bien los ganchos malos (AUC
0,83) y **no distingue ganadores** (AUC 0,56, donde 0,50 es tirar una moneda).
Las fórmulas, reescritas sobre habla real, ponían nombre al 49% de los ganchos.

**Nada de eso se ha repetido en español.** Esta adaptación:

- tradujo los léxicos y escribió las regex de las 26 fórmulas para el español
  hablado;
- se probó solo con ejemplos escritos a mano: 60 de 60 ganchos de prueba
  clasificados en su fórmula. Son ejemplos hechos para las regex, así que ese
  número no dice nada sobre ganchos reales. El original pasó del 8% al 49%
  justo cuando dejó de probar con sus propias plantillas;
- no se ha calibrado con un corpus español.

Úsalo para descartar los ganchos flojos antes de grabar y fíate de tu gráfico
de retención. Si lo pruebas con un corpus real en español, el método está en
[`/ig-viral`](skills/ig-viral/SKILL.md) y el resultado será más útil que
cualquier ejemplo de este README.

## Cambios respecto al original

- Todos los scripts aceptan `--lang es|en` (por defecto `es`) o `IG_LANG`. Para
  añadir otro idioma basta con un bloque de datos por script y un
  `hooks.<idioma>.json` y `slop.<idioma>.json`.
- Palabras con tildes y ñ, cifras en formato español (`18.000 €`), signos ¿ ¡ y
  segunda persona sin pronombre («¿Sabías...?», «tienes», «perdiste»).
- Arreglado un fallo del original en `hookscore.py`: las aperturas débiles se
  comparaban como prefijo, así que «Your» contaba como «yo», «His» como «hi» y
  «Someone» como «so». Ahora se comparan palabras completas.
- `caption.py` avisa si la primera línea es un saludo (el original lo decía en
  la documentación pero no lo comprobaba).
- `swipe.py` entiende `412K`, `412 mil` o `1,2 M`. El original quitaba todo lo
  que no fuera dígito, así que `1.2M` se leía como 12.
- La señal de muro de hashtags es de 6 o más (coherente con el tope de 5) y ya
  no menciona LinkedIn.

## La letra pequeña, que es la parte honesta

**Estas skills no publican en Instagram.** Existe una API oficial de
publicación de contenido para cuentas profesionales, pero necesita una app de
desarrollador de Meta, una página vinculada, un token de larga duración y una
revisión de la app, y eso no te lo puede dar una skill. Todo lo demás que se usa
para automatizar publicaciones, comentarios, follows o DMs es automatización
del navegador o una herramienta de terceros, y las dos cosas incumplen las
[Condiciones de uso de Instagram](https://help.instagram.com/581066165581870) y
acaban en bloqueos de acción. Así que cada skill termina igual: un bloque listo
para copiar, y lo publicas tú.

La excepción son las respuestas automáticas por palabra clave en los DM, que
Instagram permite con sus propias herramientas y socios aprobados, y que solo
se disparan después de que alguien comente primero. `/ig-dm` explica dónde está
esa línea.

**`/ig-viral` lee, no hace scraping.** Diez cuentas, una docena de reels por
cuenta, a velocidad humana, contigo manejando tu propio navegador. Nunca pide
tu contraseña y nunca entra con tu cuenta.

**Las cinco comprobaciones de detección son heurísticas locales, no APIs de
detectores.** No son GPTZero, Originality, Copyleaks, Winston ni Turnitin, no
llaman a esos servicios y no pueden prometer su veredicto. Nadie puede venderte
honestamente un texto «indetectable».

**La pasada de caracteres invisibles es real y es limitada.** Quita los
caracteres de ancho cero y de formato que acaban en el texto generado y
sobreviven al copiar y pegar. No pretende desactivar ningún sistema de marca de
agua criptográfica.

**Aquí no se inventa nada.** Ninguna métrica, cliente o resultado inventado va
con tu nombre. Si un borrador necesita un número que no has dado, vuelve con
`{{tu número}}` y un aviso.

**Las cifras de la plataforma caducan.** El tope de hashtags pasó de 30 a 5 en
diciembre de 2025. Si algo de aquí contradice lo que hace Instagram cuando lo
leas, tiene razón Instagram.

## Archivos

```
skills/ig-reel/hooks.es.json       26 fórmulas de gancho en español: plantilla, ejemplo,
                                   texto en pantalla, para qué sirve, cómo se estropea y regex
skills/ig-reel/hooks.json          las mismas 26 en inglés (--lang en)
skills/ig-reel/hookscore.py        el panel de cinco propiedades del gancho
skills/ig-reel/beats.py            del guion a la escaleta cronometrada
skills/ig-caption/caption.py       la vista previa del corte y la revisión del texto
skills/ig-human/slop.json          caracteres invisibles, tipografía y léxico en inglés
skills/ig-human/slop.es.json       el léxico y las señales de estructura en español
skills/ig-human/humanize.py        las tres pasadas de limpieza
skills/ig-human/detect.py          el panel de cinco comprobaciones
skills/ig-viral/swipe.py           ordenación por múltiplo y clasificación por fórmula
skills/ig-profile/rubric.es.json   la nota del perfil sobre 100 (rubric.json en inglés)
templates/voice.md                 tu perfil de voz. Rellénalo primero.
```

## Créditos

Pack original de Jake Schincariol, [opusjake.ai](https://opusjake.ai), con
licencia MIT. Esta adaptación al español mantiene la misma licencia.

## Licencia

MIT. Cógelo, cámbialo, publícalo.
