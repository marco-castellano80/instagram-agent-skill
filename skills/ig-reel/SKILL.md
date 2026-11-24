---
name: ig-reel
description: >-
  Escribe un reel de Instagram a partir de una idea en bruto: opciones de
  gancho sacadas de 26 fórmulas, el guion hablado, el texto en pantalla y una
  escaleta cronometrada, con la voz del propio usuario y con nota antes de
  grabarlo. Úsala siempre que el usuario quiera un reel, un guion de vídeo
  corto, un gancho, una locución, «hazme un reel sobre X», «qué digo en este
  vídeo», o esté a punto de grabar y todavía no tenga la primera frase.
---

# ig-reel

Escribe siempre en español, en la variante que diga `~/.claude/instagram/voice.md`
(España, Latinoamérica o neutro). Si no lo dice, español neutro con «tú».

Convierte una idea en bruto en un reel que alguien ve hasta el final.

En esta carpeta hay dos herramientas y las dos funcionan de verdad. Úsalas. No
juzgues el gancho a ojo ni adivines la duración.

```bash
python3 hookscore.py ganchos.txt            # ordena tus opciones de gancho
python3 hookscore.py --hook "una frase"     # puntúa uno solo
python3 beats.py guion.txt --target 30      # escaleta cronometrada antes de grabar
```

Las dos trabajan en español por defecto. Con `--lang en` usan el léxico y los
mensajes en inglés.

## Antes de escribir

1. Lee `~/.claude/instagram/voice.md` si existe. Es el perfil de voz del
   usuario: cómo habla a cámara, qué no dice nunca, a quién le habla. Si no
   existe, pídele **tres de sus propios reels**, transcríbelos o léelos, deduce
   la voz y escribe el archivo. Un guion con la voz equivocada no sirve, porque
   lo tiene que decir en voz alta.
2. Lee `hooks.es.json` en esta carpeta. 26 fórmulas, cada una con su
   plantilla, un ejemplo relleno, la versión en pantalla, para qué sirve y cómo
   se estropea. Cuatro están ahí porque no paraban de aparecer en ganchos
   reales, no por completar un patrón.
3. Si la idea es flaca, no la rellenes. Haz una sola pregunta agrupada: qué
   pasó, a quién, y qué costó o qué devolvió. Un reel necesita una cosa
   concreta y verdadera. Consíguela antes de escribir.
4. Si existe `~/.claude/instagram/swipe.md`, léelo. Lo escribe `/ig-viral` y
   son las pruebas del propio usuario sobre qué fórmulas funcionan ahora mismo
   en su nicho. Manda sobre los valores por defecto de este archivo.

## La forma

Un reel se decide en los dos primeros segundos y se sostiene en los cinco
siguientes.

```
0:00 - 0:02    GANCHO         la afirmación. Frase hablada y frase en pantalla,
                              escritas por separado. Movimiento en el primer
                              fotograma, no una cara quieta.
0:02 - 0:07    EN JUEGO       por qué le importa a quien lo ve. Una frase.
0:07 - ...     EL CUERPO      una idea por bloque, y el plano cambia en cada bloque.
ÚLTIMOS 3 s    LA RECOMPENSA  cumple lo que prometió el gancho y luego la única petición.
ÚLTIMA FRASE   EL BUCLE       repite una palabra del gancho para que la vuelta encaje.
```

Duración: de 15 a 45 segundos es el rango que funciona. Los reels pueden durar
hasta 3 minutos y casi nadie debería usarlos. Por debajo de 7 segundos se
inflan las vistas por repetición y nada más.

## El ciclo

**1. Elige tres ganchos, no uno.** Pasa la idea por `hooks.es.json`, elige tres
fórmulas que de verdad le encajen y escribe la frase hablada y la frase en
pantalla de cada una. Fórmulas distintas, no tres versiones de la misma.

**2. Puntúalos.** Pon las tres frases habladas en un archivo, una por línea, y
pasa `hookscore.py`. Enséñale el ranking al usuario. Si el primero está por
debajo de 50, todavía no tienes el gancho y ninguna edición lo arregla. En
español la nota es una adaptación sin calibrar con ganchos reales: úsala para
descartar los flojos, no para elegir entre dos fuertes.

**3. Escribe el guion** sobre el gancho ganador. Lenguaje hablado, el que usa de
verdad el usuario. Frases cortas. Nada de giros de texto escrito, ninguna frase
que tenga que ensayar.

**4. Cronométralo.** Pasa `beats.py guion.txt --target {duración}`. Corrige cada
aviso: un gancho de más de 3 segundos, cualquier bloque de más de 4 segundos,
una racha de bloques sin nada concreto, la falta de bucle. Vuelve a pasarlo
hasta que salga limpio.

**5. Humanízalo.** Pasa el guion por `/ig-human` antes de enseñarlo. Una frase
que suena a escrita se nota en cuanto alguien la dice en voz alta.

**6. Imprime el bloque.** El guion en un bloque de código, el texto en pantalla
como lista aparte con sus tiempos, y luego:

```
REEL LISTO
gancho:       #3 Nadie te lo dice, nota 87 FUERTE
duración:     28,4 s en 9 bloques a 165 ppm
en pantalla:  6 cartelas
humanizador:  4 rastros eliminados, nota humana 81 APTO
texto:        ahora pasa /ig-caption

Responde "sí" para registrarlo, o dime qué cambio.
```

**7. Nunca publiques.** Esta skill produce un guion. El usuario lo graba y lo
publica. Con un «sí», añade a `~/.claude/instagram/log.md` la fecha, la fórmula
de gancho usada y la primera frase, para que `/ig-audit` tenga historial más
adelante.

## El texto en pantalla es otro guion

Escríbelo aparte, siempre. Se lee antes de oírse.

- **Seis palabras o menos por cartela.** Lo lee con el brazo estirado alguien
  que todavía no está escuchando.
- **La cartela del gancho está desde el fotograma 1**, no después de un
  silencio.
- **Dentro de la zona segura.** En un fotograma de 1080x1920, nada por encima
  de y=230 ni por debajo de y=1440, y deja libres los 230 píxeles de la
  derecha. Fuera de esa caja la interfaz tapa todo lo que haya: el texto
  (caption), la columna de botones, la franja del audio.
- **Nunca pongas el gancho donde va el texto.** Es la parte de abajo del
  fotograma y queda tapada.
- **Subtítulos incrustados en el cuerpo.** Casi todo el mundo lo ve primero sin
  sonido.

## Las reglas que marcan la diferencia

- **Una idea por reel.** Si el guion tiene dos, tienes dos reels. Dilo.
- **Números antes que adjetivos.** «4.200 €» gana a «mucho». Si el usuario no
  ha dado un número, pídeselo en vez de escribir alrededor del hueco.
- **Corta la introducción.** Sin saludo, sin «en este vídeo», sin nombre, sin
  cortinilla con el logo. El vídeo empieza en la frase a la que normalmente
  llegarías en el segundo seis.
- **Cambia el plano en cada bloque.** Un plano fijo de 8 segundos es donde la
  gente se va, y `beats.py` lo va a marcar.
- **Una sola petición al final.** Comentar una palabra clave, guardar o seguir.
  Una.
- **Nunca inventes.** Ni métricas, ni clientes, ni facturación, ni resultados
  inventados a nombre del usuario, ni siquiera provisionales. Si hace falta un
  número y no lo sabes, deja `{{tu número}}` en el guion y avísalo.
- **No escribas un guion alrededor de un audio en tendencia que el usuario no
  puede usar.** Si la idea necesita la voz del usuario, dilo.

## Ejemplo

```
/ig-reel hemos pasado de 5 horas a 20 minutos por propuesta con una plantilla
```

```
GANCHOS  (con nota)
  79  FUERTE  #5  El tiempo comprimido  "Antes cada propuesta me llevaba cinco horas. Ahora, veinte minutos."
                                        en pantalla: 5 HORAS -> 20 MIN
  75  FUERTE  #1  Lo que me costó       "Cuatro horas a la semana durante dos años: eso me costó maquetar a mano."
                                        en pantalla: 2 AÑOS PERDIDOS
  61  OK      #9  Róbalo                "Róbame esta plantilla de propuesta. A mí me costó dos años."
                                        en pantalla: RÓBAME ESTO

Graba el #5: la proporción es creíble, se lee de un vistazo en pantalla
y el número es tuyo.
```
