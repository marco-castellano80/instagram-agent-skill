---
name: ig-human
description: >-
  Quita la huella de máquina de cualquier borrador (rayas, palabras de relleno
  típicas de la IA, caracteres invisibles de marca de agua) y lo puntúa con un
  panel de cinco comprobaciones antes de que salga. Úsala siempre que un texto
  tenga que sonar humano, cuando el usuario diga «humaniza esto», «¿esto suena
  a IA?», «quita las rayas», «quítale el relleno», «esto suena a ChatGPT», o
  antes de enseñar al usuario cualquier texto (caption), guion, comentario,
  respuesta o DM.
---

# ig-human

Escribe siempre en español, en la variante que diga `~/.claude/instagram/voice.md`
(España, Latinoamérica o neutro). Si no lo dice, español neutro con «tú».

En esta carpeta hay dos herramientas y las dos funcionan de verdad. Úsalas. No
lo hagas a ojo.

```bash
python3 humanize.py borrador.txt --report       # lo limpia y enseña qué cambió
python3 detect.py borrador.txt                  # lo puntúa, cinco comprobaciones
python3 detect.py borrador.txt limpio.txt       # demuestra la diferencia
```

Las dos trabajan en español por defecto. Con `--lang en` usan el léxico y los
mensajes en inglés.

Con `--lang es`, las dos leen dos archivos de léxico (con `--lang en`, solo `slop.json`):

- `slop.json`: las 18 clases de caracteres invisibles, que valen para todos
  los idiomas. Con `--lang en` da también la tipografía, el léxico y las
  señales de estructura en inglés.
- `slop.es.json`: con `--lang es`, todo lo demás. Las 11 sustituciones
  tipográficas (las mismas que en inglés, con nombres en español; esta tabla
  sustituye a la de `slop.json`, así que un cambio de tipografía para español
  se hace aquí), 284 palabras y frases de relleno en español (75 palabras y
  209 frases), cada una con su sustitución en lenguaje normal, y 19 señales de
  estructura. Muchas entradas aparecen en cuatro formas, porque la sustitución
  tiene que concordar en género y número. El último tramo de aperturas y de
  cierres es específico de Instagram: el vocabulario que solo sale en textos y
  locuciones de reels.

Si falta `slop.es.json`, las dos salen con código 2 y un mensaje de error en
lugar de seguir con el léxico inglés. Con `--lexicon-lang` puedes indicar otra
ruta.

Es una lista hecha a mano, no calibrada con un corpus, y está pensada para
editarla. Si el usuario tiene una palabra que usa siempre y el léxico se la
quita, sácala de `slop.es.json`.

## Por qué esto importa más en Instagram de lo que parece

Los textos son cortos y los guiones se dicen en voz alta. Una frase que suena a
escrita pesa más en un texto de 600 caracteres que la misma frase en un ensayo,
y una locución que nadie diría así se nota en la primera toma. Aquí la señal no
es un detector que marca la publicación. Es una persona que pasa de largo ante
algo que suena a marca, o un creador que se traba con su propio guion.

## Lo que se arregla solo

**1. Caracteres invisibles.** Espacios y uniones de ancho cero, unidores de palabra,
guiones blandos, marcas de orden de bytes (BOM), caracteres de etiqueta
Unicode, separadores invisibles, espacios duros y estrechos. Un teclado no los
produce. Sobreviven al copiar y pegar, no se ven en ningún editor y son lo más
mecánico de un texto generado. `humanize.py` los borra todos (los espacios
duros y estrechos los cambia por un espacio normal), incluido cualquier otro
carácter de formato Unicode que no tenga en la lista.

**2. Tipografía.** Raya a coma, semirraya a guion, comillas curvas a rectas, el
carácter de puntos suspensivos a tres puntos, viñeta a guion. Las comillas
angulares «» y los signos de apertura ¿ ¡ no se tocan. La pasada de la raya es
la que importa: convierte la raya en coma y después limpia la puntuación doble
y los puntos huérfanos que deja. Delante de un conector («además», «así que»)
la raya pasa a punto, para no empalmar dos frases, y una semirraya entre
espacios se trata igual. Una raya al principio de línea (diálogo o viñeta) se
quita sin pegar la línea a la anterior.

**3. El léxico de relleno.** «sumérgete en», «apalancar», «robusto», «sin
fisuras», «crucial», «un testimonio de», «en el acelerado mundo actual», y el
bloque de Instagram: «deja de hacer scroll», «en el vídeo de hoy», «sígueme
para más», «etiqueta a alguien que necesite esto», «al algoritmo le encanta»,
«corre, no camines». Cada una se cambia por una palabra normal o se borra,
respetando las mayúsculas y sin tocar las URL, los hashtags ni las menciones.
La pasada se repite (tres veces como mucho) mientras cambie algo, porque una
sustitución puede formar otra entrada del léxico. Las comas y las minúsculas
que siguen a una abreviatura («p. ej.,», «a. m.», «EE. UU.») se respetan.

## Lo que NO se arregla solo

Las señales de estructura se **marcan, no se reescriben**, porque cambiar la
forma de una frase necesita criterio. Estas son las 19 de `slop.es.json`:

- «No es solo X, es Y» y «No solo X, sino también Y»
- «Esto no va de X. Va de Y.»
- Preguntas retóricas de una línea: «¿El resultado?», «¿La clave?»
- Apertura con pregunta retórica: «¿Alguna vez te has preguntado...?»,
  «¿Sabías que...?»
- «Esto es lo que aprendí»
- Tríadas de tres elementos
- Emoji de cohete, fuego, bombilla, chispas o diana
- Listas con emojis como viñetas
- Muros de hashtags (6 o más)
- El modelo hablando de sí mismo: «como IA», «como modelo de lenguaje»
- Aperturas de conclusión de redacción: «En resumen», «Para concluir»
- Preguntas de enganche por reflejo: «¿Qué opinas?», «¿Estás de acuerdo?»,
  «¿Y tú?»
- La apertura «deja de hacer scroll»
- El preámbulo de vídeo: «en este vídeo te voy a enseñar»
- Tres o más palabras gritadas seguidas
- Mayúsculas a la inglesa: «Cómo Hacer Crecer Tu Marca»
- Tres exclamaciones seguidas
- Cebo de seguir o etiquetar por reflejo: «sígueme para más», «etiqueta a
  alguien», «doble tap si»

Tres son propias del español: la apertura con pregunta retórica, las mayúsculas
a la inglesa y las tres exclamaciones. `humanize.py` marca además las frases de
longitud uniforme cuando hay cuatro o más.

Esa lista te toca a ti. Reescribe a mano cada línea marcada, sin cambiar el
sentido, y vuelve a pasar `detect.py`. Esta es la parte que lleva la nota de
REVISAR a APTO, y es la parte que un script no puede hacer.

## Las cinco comprobaciones

`detect.py` puntúa cinco señales de 0 a 100. Más alto es más humano:

| comprobación | qué mide | cómo se ve la máquina |
| --- | --- | --- |
| RITMO | variación de longitud entre frases | todas las frases miden lo mismo |
| CONCRECIÓN | números, nombres y datos concretos por cada 100 palabras | sustantivos abstractos, ninguna cifra |
| RELLENO | coincidencias con el léxico por cada 100 palabras | vocabulario de plantilla |
| HUELLA | invisibles, rayas y comillas curvas por cada 1.000 caracteres | tipografía perfecta |
| VOZ | pronombres personales y señales de estructura | nadie habla en primera ni en segunda persona, revelaciones escenificadas |

En español VOZ mide solo pronombres personales y señales de estructura, a
partes iguales. La versión inglesa cuenta también las contracciones, pero en
español no existen («del» y «al» son obligatorias), así que esa señal
desaparece y su peso pasa a las otras dos. En HUELLA no cuentan las «» ni los
¿ ¡.

El veredicto pondera la media al 60% y la **comprobación más débil** al 40%,
porque basta una señal. APTO pide una nota total de 70 o más y ninguna
comprobación por debajo de 55. Si no llega, es REVISAR. Con menos de 50 en
total, MARCADO.

## Dilo con honestidad

Son cinco heurísticas locales basadas en las señales en las que se fijan los
detectores públicos. Se ejecutan enteras en la máquina del usuario y no se sube
nada. **No** son GPTZero, Originality, Copyleaks, Winston ni Turnitin, no
llaman a sus API y no pueden prometer su veredicto. Arreglar lo que miden suele
mover esas cifras, porque en el fondo miden lo mismo. Eso es lo que se afirma.
No afirmes nada más grande en nombre del usuario, y no le digas nunca que su
texto es indetectable.

Y una advertencia más: los umbrales vienen de la versión inglesa y no se han
calibrado con textos en español. Tómalo como una revisión de estilo, no como
una medida.

## Orden de trabajo

1. `humanize.py borrador.txt -o limpio.txt --report`
2. Lee las señales de estructura. Reescribe tú esas líneas.
3. `detect.py borrador.txt limpio.txt` para enseñar el antes y el después.
4. Si el veredicto no es APTO, arregla la comprobación más débil que nombra la
   salida y repite. Dos rondas es lo normal. Cinco significa que el borrador se
   escribió con fórmula, y la solución es otro borrador, no más pasadas.
5. Enseña al usuario el texto limpio y la nota. Nunca la nota sola.
