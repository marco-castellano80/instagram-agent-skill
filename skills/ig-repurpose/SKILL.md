---
name: ig-repurpose
description: >-
  Convierte un contenido largo (un vídeo de YouTube, un pódcast, un directo,
  una newsletter, un artículo de blog o una llamada con un cliente) en una
  semana de reels y carruseles. Úsala cuando el usuario diga «reaprovecha
  esto», «conviértelo en reels», «tengo un vídeo / pódcast / transcripción»,
  «trocea esto», o pegue algo largo y lo quiera en Instagram.
---

# ig-repurpose

Escribe siempre en español, en la variante que diga `~/.claude/instagram/voice.md`
(España, Latinoamérica o neutro). Si no lo dice, español neutro con «tú».

Un buen contenido largo lleva dentro de cuatro a seis publicaciones. La mayoría
de la gente saca una y tira el resto.

## Entrada

Una transcripción, un artículo, una newsletter, un guion, el resumen de una
llamada, un directo. Si el usuario da una URL y esta sesión tiene una
herramienta de transcripción, úsala; si no, pídele que lo pegue. Léelo entero
antes de extraer nada.

Si la fuente es un vídeo del propio usuario, pídele también el archivo. Un reel
montado con sus propias imágenes gana a uno montado con sus propias palabras
leídas otra vez.

## Extrae, no resumas

El resumen de un vídeo no es un reel. Nadie quiere el resumen. Recorre el
contenido y saca lo que se sostiene solo:

| qué sacar | qué es |
| --- | --- |
| **Afirmaciones** | cada frase que abriría una discusión |
| **Cifras** | cada número, coste, duración o porcentaje |
| **Relatos** | cada momento con una persona, una escena y un coste |
| **Mecanismos** | cada «así es como funciona de verdad...» |
| **Errores** | cada vez que se admite algo que salió mal |
| **Frases** | cada frase que ya se puede citar tal cual |

Enumera lo que has encontrado, con el recuento, antes de escribir nada. Si el
contenido da menos de cuatro elementos, es flojo, y cuatro publicaciones
exprimidas de ahí también lo serán. Dilo.

## Luego elige el formato de cada extracto

No todo es un reel.

- **Afirmación, error o relato**: a reel. Necesitan una voz y una cara.
- **Mecanismo o lista numerada**: a carrusel. Hay que volver a leerlos.
- **Una frase citable**: a una pantalla de historia, no a una publicación.

## Luego monta la semana

Cada extracto se convierte en una publicación, y cada publicación se sostiene
sola del todo. El espectador no ha visto la fuente y no la verá nunca. No
escribas nunca «como dije en mi último vídeo». La publicación es la cosa.

Asigna a cada una una fórmula de gancho de `ig-reel/hooks.es.json` y varíalas.
Cinco publicaciones de la misma fuente con la misma forma de gancho se leen
como una fábrica de contenido, porque lo son.

Si la fuente es un vídeo del propio usuario, **usa las imágenes reales**. El
clip en el que dijo la frase, con la reacción real, gana siempre a volver a
grabarlo. Corta en la frase, no en la respiración.

Ordénalas en la semana para que la afirmación más fuerte vaya primero, el
relato caiga a mitad de semana y el mecanismo vaya al final, cuando la gente a
la que le gustaron las anteriores ya lo está esperando.

## Salida

```
FUENTE: "Por qué eliminamos las llamadas de descubrimiento" (pódcast de 42 min, 8.900 palabras)

ENCONTRADO  5 afirmaciones, 9 cifras, 3 relatos, 4 mecanismos, 2 errores, 7 frases citables

SEMANA
MAR  REEL      #2  La orden negativa      Deja de hacer llamadas de descubrimiento
                                          usa el clip del 14:20, se ríe al final
MIÉ  CARRUSEL  texto tipo B               El formulario de 4 preguntas que sustituyó a la llamada
VIE  REEL      #21 Empezar a media frase  "...y nueve días después pidió que le devolviéramos el dinero"
DOM  REEL      #5  El tiempo comprimido   Seis horas a la semana recuperadas, un enlace menos

Di "escribe el martes" y te lo redacto.
```

Después redacta lo que el usuario pida, de una en una, cada una pasando por
`/ig-reel` y `/ig-human`. No sueltes cuatro guiones terminados de golpe. Sonarán
todos igual y el usuario no grabará ninguno.
