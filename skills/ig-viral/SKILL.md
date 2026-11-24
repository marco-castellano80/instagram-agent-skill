---
name: ig-viral
description: >-
  Sale a buscar los reels que están funcionando de verdad ahora mismo en el
  nicho del usuario, los ordena por cuánto superó cada uno a su propia cuenta,
  pone nombre a la fórmula de gancho que usó cada uno y lo convierte en un
  swipe file (archivo de referencias) desde el que grabar. Úsala cuando el
  usuario diga «busca vídeos virales», «qué está funcionando ahora», «qué
  publica la gente de mi nicho», «haz ingeniería inversa de esta cuenta»,
  «hazme un swipe file», «por qué este reel tiene tantas vistas», o pregunte
  qué hacer a continuación y no tenga pruebas con las que responder.
---

# ig-viral

Escribe siempre en español, en la variante que diga `~/.claude/instagram/voice.md`
(España, Latinoamérica o neutro). Si no lo dice, español neutro con «tú».

La skill de investigación. Todo lo demás del paquete escribe; esta sale a
mirar. Pásala una vez al mes, no a diario. Las fórmulas duran una temporada.

En esta carpeta hay una herramienta y funciona de verdad:

```bash
python3 swipe.py capturados.tsv --out ~/.claude/instagram/swipe.md
```

## La única idea que hace que merezca la pena

**Las visualizaciones brutas no son una prueba.** Una cuenta con dos millones
de seguidores que hace 400.000 visualizaciones ha tenido un martes flojo. Una
cuenta con cuatro mil seguidores que hace 400.000 ha encontrado algo, y ese
algo se puede copiar.

Por eso aquí todo se ordena por el **múltiplo sobre la mediana**: las
visualizaciones divididas entre la mediana reciente de esa misma cuenta. Por
encima de 3x hay señal. Por debajo de 1,5x es un día normal de esa cuenta y no
te enseña nada, por grande que parezca el número.

Recoge cuentas **que no se alejen más de unas 10x del tamaño del usuario**.
Una fórmula que funciona con 2 millones de seguidores muchas veces
funciona porque tiene 2 millones de seguidores.

## Paso 1: elige las cuentas

Pídele al usuario de 6 a 12 cuentas, o propónselas y espera su visto bueno:

- **4 directas**: mismo nicho, misma oferta, un poco por delante.
- **4 vecinas**: otro nicho, la misma audiencia. Aquí es donde se toman
  prestados los formatos antes de que nadie del nicho los tenga.
- **De 2 a 4 enormes**: cuentas mucho más grandes, solo por el formato, nunca
  por la frecuencia ni por el tono.

Pídele también que abra su propia **colección de Guardados**. Es el corpus más
rápido y más relevante que existe, y ya viene filtrado por su gusto.

## Paso 2: sal a mirar

Usa la herramienta de navegación que tenga de verdad esta sesión: un navegador
dentro de la app, una extensión conectada al Chrome del propio usuario o una
herramienta de uso del ordenador. No hay API para esto ni hace falta, porque el
volumen es lo bastante pequeño como para leerlo.

**Reglas que no se negocian:**

- **Nunca inicies sesión en Instagram en nombre del usuario ni le pidas la
  contraseña.** Si una página pide iniciar sesión, quien ya tiene la sesión
  abierta es el usuario. Maneja su navegador con él delante, o pídele que pegue
  lo que ve.
- **Esto es leer, no extraer datos en masa (scraping).** Diez cuentas, una
  docena de reels de cada una, a velocidad humana. La recogida automatizada a
  gran escala incumple las Condiciones de uso de Instagram y acaba con la
  cuenta bloqueada para acciones. No construyas un rastreador, no uses un
  servicio de scraping y no lo dejes en bucle en segundo plano.
- **Copia la fórmula, nunca el vídeo.** La forma del gancho, la estructura, la
  duración, el patrón de cortes. No su guion, ni su voz, ni su edición.
  Atribuye cada fila del swipe file a la cuenta de la que salió.

**Qué apuntar de cada reel**, con las palabras del propio creador:

| campo | notas |
| --- | --- |
| cuenta | nombre de usuario (@) |
| seguidores | del perfil |
| mediana | mira a ojo los últimos 12 reels y quédate con las visualizaciones del que queda en medio |
| vistas | las de este reel |
| gancho | la primera frase, hablada o en pantalla, literal, con sus faltas incluidas |
| en pantalla | la primera cartela, si es distinta |
| duración | en segundos |
| cta | lo que piden al final |

La mediana es la que importa. Sin ella vuelves a ordenar por número de
seguidores, que es justo lo que esta skill existe para evitar.

**Cuando Instagram no te enseñe lo suficiente:** la misma gramática de gancho
funciona en YouTube Shorts, donde las visualizaciones y las transcripciones son
públicas y no hace falta iniciar sesión. Es un segundo corpus legítimo, y ahí
el gancho hablado es más fácil de conseguir:

```bash
# visualizaciones de los shorts de un canal
python3 -m yt_dlp --flat-playlist --playlist-end 40 -J \
  "https://www.youtube.com/@CANAL/shorts" > canal.json

# la primera frase hablada de un short, sacada de sus subtítulos automáticos
python3 -m yt_dlp --skip-download --write-auto-subs --sub-langs "es.*" \
  --sub-format json3 -o gancho "https://www.youtube.com/watch?v=ID_DEL_VIDEO"
```

Quédate con todas las palabras de los subtítulos cuya marca de tiempo esté por
debajo de 3,0 segundos. Ese es el gancho tal como se dijo, no como se escribió.

## Paso 3: ordénalo

Rellena un archivo separado por tabuladores con una fila de cabecera y pasa el
script:

```
cuenta	seguidores	mediana	vistas	gancho
@alguien	48000	11000	412000	nadie te dice que tus primeros 30 reels tienen que fracasar
```

```bash
python3 swipe.py capturados.tsv --out ~/.claude/instagram/swipe.md
```

La cabecera también vale en inglés, y las cifras se pueden escribir como
`412.000`, `412K`, `412 mil`, `1,2 M` o `1 millón`. Si una celda no se
entiende, el script avisa y la deja vacía en vez de inventarse una cifra (una
fila sin vistas no entra en el ranking): corrígela y vuelve a pasarlo.

Calcula el múltiplo sobre la mediana, pone nombre a la fórmula de cada gancho
con las mismas 26 fórmulas de las que escribe `/ig-reel` (`hooks.es.json`; con
`--lang en`, las de `hooks.json`), puntúa cada gancho con `hookscore.py` e
imprime lo que separa el tercio superior del tercio inferior.

## Paso 4: di lo que significa, con cuidado

Cuenta tres cosas y ni una más:

1. **Qué fórmulas están sobrerrepresentadas** en el tercio superior, con sus
   recuentos. Dos fórmulas que aparecen cuatro veces cada una en seis cuentas
   son un hallazgo. Una que aparece dos veces, no.
2. **Qué tiene en común la estructura del tercio superior** que el inferior no
   tiene: la longitud del gancho, si la recompensa es visual, si el primer
   fotograma se mueve, dónde va la petición.
3. **Las filas sin clasificar.** Cada gancho al que el clasificador no ha
   podido poner nombre es ruido o una fórmula que todavía no está en
   `hooks.es.json`. Léelos a mano. Es la columna más valiosa de la salida y la
   razón por la que el script imprime el recuento.

Luego di el tamaño de la muestra y la confianza con palabras claras. Cuarenta
reels de seis cuentas sostienen una afirmación. Doce no, y decirlo es la
diferencia entre investigar y leer el horóscopo.

## Paso 5: conviértelo en algo que grabar

Para las tres fórmulas de arriba, escribe **la versión del usuario**: su propia
historia y su propio número, con la forma que está funcionando. Pásale cada una
a `/ig-reel` con el id de la fórmula ya elegido.

Nunca devuelvas «haz un reel como este». Devuelve una frase de gancho que pueda
decir mañana.

## Salida

La primera parte, hasta la nota sobre el tamaño del lote, es lo que imprime
`swipe.py` (recortado donde pone «...»). Lo de debajo lo escribes tú.

```
SWIPE FILE  ·  38 reels  ·  7 cuentas  ·  referencia: mediana de la cuenta
==============================================================================
    38.5x  gancho  87  #3  Nadie te lo dice         @cuenta_a          412.000
           "nadie te dice que tus primeros 30 reels tienen que fracasar"
    30.0x  gancho  53  #3  Nadie te lo dice         @cuenta_b           96.000
           "nadie te cuenta que el primer cliente casi nunca paga lo que vale"
    ...
------------------------------------------------------------------------------
QUÉ ESTÁ FUNCIONANDO EN ESTE LOTE
  tercio superior:        Nadie te lo dice x5, La orden negativa x4, sin clasificar x2, Róbalo x1
  nota mediana gancho:    arriba 52  frente a abajo 33
  longitud mediana:       arriba 10.5 palabras  frente a abajo 15.5 palabras
  sin clasificar:         15 de 38. Léelos a mano: ahí se esconde una fórmula que todavía no tienes.

  Un lote recogido a mano es un indicio, no una prueba. Doce reels no te enseñan nada;
  cuarenta en seis cuentas te enseñan algo. Recoge más antes de creértelo.

SIN CLASIFICAR (15)
  Los dos del tercio superior tienen la misma forma y no está en hooks.es.json:
  un gancho que empieza leyendo en voz alta el comentario de otra persona.
  Merece la pena añadirla.

TU VERSIÓN
  #3  "Nadie te dice que tus primeras 20 propuestas tienen que perderse."
  ...
```

Escribe el swipe file en `~/.claude/instagram/swipe.md`. `/ig-reel` y
`/ig-plan` lo leen los dos, y de eso se trata: después de pasarlo una vez, el
resto del paquete trabaja con las pruebas del propio usuario y no con los
valores por defecto.

Esta skill no publica, no sigue, no da me gusta ni manda mensajes. Lee.
