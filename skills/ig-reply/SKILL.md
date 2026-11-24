---
name: ig-reply
description: >-
  Gestiona los comentarios en los reels y publicaciones del propio usuario:
  redacta respuestas para los que merecen respuesta, ordenados según cuáles lo
  merecen. Úsala cuando el usuario pegue sus comentarios, diga «responde a
  estos», «gestiona mis comentarios», «alguien ha puesto X en mi reel», o esté
  lidiando con un crítico, un hater o un cliente potencial en los comentarios.
---

# ig-reply

Escribe siempre en español, en la variante que diga `~/.claude/instagram/voice.md`
(España, Latinoamérica o neutro). Si no lo dice, español neutro con «tú».

El hilo de comentarios de tu propia publicación es donde se decide el alcance.
Cada respuesta es una interacción más en la publicación. Las que llegan en la
primera hora hacen casi todo el trabajo. Y en Instagram una respuesta también
puede ser un reel, que es el recurso más infrautilizado de toda la plataforma.

Pero no todos los comentarios valen lo mismo, así que esta skill clasifica
antes de escribir.

## Entrada

El usuario pega los comentarios, idealmente con los nombres de usuario (@).
Las capturas valen. No extraigas el hilo con una herramienta de navegador.

## Primero, clasifica

Mete cada comentario en uno de seis grupos y di claramente cuántos hay en cada
uno:

| grupo | qué es | qué recibe |
| --- | --- | --- |
| **PALABRA CLAVE** | la palabra que les pediste que comentaran | lo prometido, enviado a mano o con tu herramienta aprobada |
| **CLIENTE POTENCIAL** | alguien que describe el problema que tú resuelves | una respuesta de verdad en público, y luego una puerta |
| **SUSTANCIA** | aporta datos, discrepa o amplía | la respuesta más larga del hilo |
| **PREGUNTA** | una pregunta que tiene mucha gente | esta se convierte en un reel, no solo en una respuesta |
| **APOYO** | «🔥», «gran post», una etiqueta | un me gusta y, como mucho, de 3 a 8 palabras |
| **RUIDO** | autopromoción, spam, mala fe, provocación | nada, o una línea y fuera |

Escribe en ese orden y para cuando se acabe el valor.

## El movimiento que casi todos se saltan

Si una pregunta de los comentarios es de las que tienen otras treinta personas,
**respóndela con un reel**. Instagram adjunta el comentario al vídeo nuevo como
sticker, la persona que preguntó recibe una notificación, y una pregunta con
demanda real detrás se convierte en una publicación con el gancho ya escrito.
Marca cada PREGUNTA que cumpla y pásasela a `/ig-reel` como la fórmula #16, La
pregunta literal.

## Cómo responder

- **Responde a lo que te preguntan.** Si alguien pregunta cómo, dile cómo, en
  la propia respuesta. No lo mandes a los DM para oír una respuesta que podía
  tener ahí mismo.
- **Usa su nombre una vez**, al principio, sin exclamación.
- **Iguala su longitud.** Un comentario de cuatro palabras no recibe una
  respuesta de cuatro líneas.
- **A un crítico:** concede primero la parte que es verdad, con sus palabras, y
  luego mantén tu postura. Nunca borres, nunca te pongas a la defensiva, nunca
  respondas dos veces en el mismo hilo.
- **A un hater:** nada. Una respuesta es alcance, y el alcance es justo lo que
  vino a buscar. Oculta el comentario si es ofensivo. Los controles de
  comentarios de Instagram están para eso, y usarlos no es perder.
- **A un cliente potencial:** responde completo y en público. La puerta es una
  frase al final, y es una oferta de ayuda, no una venta. La respuesta pública
  es lo que hace que la siguiente persona te escriba por DM.

## Comentarios con palabra clave

Si la publicación usó una petición de palabra clave, esos comentarios son el
motivo de la publicación. Cada uno es una persona que ha levantado la mano.
Responde a cada uno y luego envía lo prometido. Si el usuario tiene la
automatización configurada con las herramientas propias de Instagram o con un
socio aprobado, dilo y deja que funcione; si no, las respuestas son manuales y
a este volumen no pasa nada. Nunca mandes DM masivos a gente que no ha
comentado.

## Salida

Un solo bloque, por grupos, con cada respuesta lista para copiar y ya
humanizada:

```
RESPUESTAS  ·  84 comentarios  ·  41 PALABRA CLAVE, 2 CLIENTE POTENCIAL, 3 SUSTANCIA, 2 PREGUNTA, 34 APOYO, 2 RUIDO

PALABRA CLAVE  (41)  envía la cláusula. Una línea a cada uno, mismo tono cercano, nada de copiar y pegar.

CLIENTE POTENCIAL
@usuario - "nos pasó exactamente esto en junio"
> Lo que nos lo arregló fue que el pago dejara de depender de la aprobación,
> del todo. Si te sirve, te paso cómo lo redactamos.

PREGUNTA -> REEL
@usuario - "¿y qué haces si se niegan a firmarla?"
  34 me gusta en este comentario. Eso es un reel, no una respuesta. Fórmula #16, La pregunta literal.

RUIDO  (2)  omitidos. Responder les da alcance.
```

Después, el filtro: no se publica nada hasta que el usuario diga que sí. Las
respuestas las pega él.
