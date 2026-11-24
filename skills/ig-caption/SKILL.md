---
name: ig-caption
description: >-
  Escribe el texto (caption) de Instagram: la línea que sobrevive al corte de
  «... más», el cuerpo, la única petición, los términos de búsqueda y hasta
  cinco hashtags, y lo revisa antes de que salga. Úsala cuando el usuario diga
  «escríbeme el texto», «ponle un caption a esto», «qué pongo en la
  descripción», tenga un reel o un carrusel listo y le falte el texto, o
  pregunte por hashtags.
---

# ig-caption

Escribe siempre en español, en la variante que diga `~/.claude/instagram/voice.md`
(España, Latinoamérica o neutro). Si no lo dice, español neutro con «tú».

En esta carpeta hay una herramienta y funciona de verdad:

```bash
python3 caption.py texto.txt
python3 caption.py texto.txt --keywords "propuestas para clientes,precios de agencia"
```

Imprime el texto (caption) como lo imprime el feed: los primeros 125
caracteres en un recuadro y todo lo demás detrás del toque. Lee ese recuadro
antes que cualquier otra cosa que hayas escrito. Revisa en español por
defecto; con `--lang en`, en inglés.

## Primero, decide qué función tiene este texto

Es la decisión que estropea los textos cuando se salta.

**Función A: el vídeo ya los ha enganchado.** Un reel lleva su propio gancho en
los dos primeros segundos, hablado y en pantalla. El texto no es un segundo
gancho, y competir con el vídeo es la forma de perder los dos. Su trabajo es la
petición, el contexto que le da sentido y las palabras que la gente busca.

**Función B: el texto es el contenido.** Una foto, una imagen suelta, la
portada de un carrusel que abre una intriga. Aquí la primera línea es el gancho
y funciona igual que el gancho de un reel: concreta, corta y cortada en un
punto de intriga, no a media subordinada.

Pregunta cuál estás escribiendo. Si el usuario tiene un reel con un gancho
fuerte, escribe la A y explica por qué.

## La forma

```
Línea 1     125 caracteres de espacio visible. Función A: la petición, sin
            rodeos. Función B: el gancho.
            Nunca un saludo, nunca un hashtag, nunca un emoji como primer
            carácter.
Cuerpo      párrafos cortos, con una línea en blanco entre cada uno. De dos a
            seis. Aquí van los términos de búsqueda.
Petición    una. Comentar una palabra clave, guardar o mandar un DM. Una.
Hashtags    hasta cinco, en su propia línea al final, o ninguno.
```

El límite es de 2.200 caracteres y casi nada necesita 2.200. Un texto que se
gana el toque y luego entrega 600 caracteres gana a uno que entrega 1.800.

## La verdad sobre los hashtags

Los hashtags ya no son una palanca de alcance, y la plataforma lo ha dicho con
un cambio de producto. **Instagram limitó los hashtags a cinco por publicación
el 18 de diciembre de 2025**, cuando antes eran treinta, y avisó a los
creadores de que rinden mejor menos hashtags (hasta 5) y más específicos que
muchos genéricos. Adam Mosseri ya había dicho en febrero de 2025 que los
hashtags no sirven para aumentar el alcance y que son una etiqueta, no una
palanca de distribución. Compruébalo antes de publicar, las cifras de la
plataforma cambian.

Así que: hasta cinco, específicos, como etiquetas de tema. Si el usuario tiene
un bloque de veinte guardado en las notas del móvil, ese bloque ya es lastre y
la revisión lo va a marcar como FALLO.

`#viral`, `#parati`, `#fyp`, `#explorepage`, `#foryou` no describen nada.
Quítalos.

## Los términos de búsqueda importan más que los hashtags

La búsqueda de Instagram lee el texto. Así que la frase por la que el usuario
quiere que lo encuentren va en el texto tal como la escribiría una persona,
dentro de una frase que se lea con normalidad. «Propuestas para clientes» como
palabras en la línea tres, no «#propuestasparaclientes» en un bloque al final.

Pide dos o tres de esos términos y pásaselos a la revisión:

```bash
python3 caption.py borrador.txt --keywords "propuestas para clientes,precios de agencia"
```

## Reglas

- **Nada de enlaces en el texto.** El texto no es clicable. Una URL en el
  cuerpo es texto muerto que dice «no uso esta plataforma». A la bio o al DM.
- **Una sola petición.** Dos peticiones es lo mismo que ninguna. `caption.py`
  las cuenta.
- **La petición de palabra clave necesita una palabra que se pueda escribir.**
  Una palabra, sin espacios, sin emoji, y dila también en voz alta en el vídeo.
  `Comenta CONTRATO` funciona. `Comenta "la guía del contrato"` no.
- **Escribe el primer comentario aparte** si hay un enlace. Dilo en el
  resumen.
- **Emoji como puntuación, no como decoración.** La revisión marca cualquier
  cosa por encima de 4 por cada 100 caracteres.
- **El texto alternativo merece 20 segundos.** En carruseles y fotos, escríbelo.
  Lo leen los lectores de pantalla y también Instagram.

## El ciclo

1. Decide si es la función A o la B, y di cuál.
2. Redáctalo.
3. Pásalo por `/ig-human`. Los textos son cortos, así que el relleno se nota
   aquí más que en ningún otro sitio del paquete.
4. Pasa `caption.py` con los términos de búsqueda del usuario. Corrige cada
   FALLO. Decide cada AVISO en voz alta, no en silencio.
5. Imprime el bloque listo para copiar y luego el resumen:

```
TEXTO LISTO
función:    A, el reel lleva el gancho
visible:    108 de 125 caracteres usados antes del corte
petición:   una, comenta CONTRATO
hashtags:   3
búsqueda:   "propuestas para clientes" en la línea 3, "precios de agencia" en la línea 5
revisión:   LISTO
```

Nada se publica. El usuario lo pega.
