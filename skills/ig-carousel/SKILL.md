---
name: ig-carousel
description: >-
  Monta un carrusel de Instagram: la portada que se gana el deslizamiento, el
  texto diapositiva a diapositiva y los archivos de 1080x1350 para subir.
  Úsala cuando el usuario diga «carrusel», «diapositivas», «post para
  deslizar», «convierte esto en un carrusel», o tenga una idea con forma de
  lista o de pasos que moriría como imagen suelta.
---

# ig-carousel

Escribe siempre en español, en la variante que diga `~/.claude/instagram/voice.md`
(España, Latinoamérica o neutro). Si no lo dice, español neutro con «tú».

Los carruseles son el formato de la cuadrícula con más tiempo de permanencia,
porque deslizar es una interacción y hacer scroll no. Además tienen una segunda
oportunidad: Instagram puede volver a enseñarle un carrusel, empezando por una
diapositiva posterior, a alguien que no interactuó la primera vez. Así que la
diapositiva dos también tiene que sostenerse sola.

El formato premia una idea partida en pasos. Castiga un texto cortado en
trozos.

## Cuándo usarlo en vez de un reel

Usa un carrusel cuando la idea tiene **secuencia y hay que releerla**: pasos, un
marco con partes, un antes y después, una lista que merece una captura. Usa un
reel cuando la idea tiene movimiento, una cara o una recompensa que hay que ver
ocurrir.

Si la idea es una sola afirmación, no es ninguno de los dos. Pásasela a
`/ig-reel` y dilo.

## Estructura

De 6 a 10 diapositivas. El tope es 20, y 20 casi siempre es un libro que nadie
termina. Con menos de 5 el deslizamiento ni empieza.

```
1         PORTADA   el gancho. 6 palabras o menos, a un tamaño que se lea en la
                    cuadrícula en miniatura. Una línea de promesa debajo.
2         EN JUEGO  por qué importa, en una frase. Esta diapositiva también es
                    una segunda portada, así que no puede ser preparación.
3 a N     UNA IDEA POR DIAPOSITIVA. Un titular de 3 a 7 palabras y como mucho
                    25 palabras debajo. Si necesita un párrafo, son dos diapositivas.
N+1       RESUMEN   todo junto en forma de lista. Esta es la diapositiva de la captura.
ÚLTIMA    CTA       una acción. Guardar, comentar una palabra clave o seguir. Una.
```

## Reglas del texto de las diapositivas

- **La portada es el 80% del resultado.** Seis palabras. En grande. Nada del
  resto salva una portada que nadie desliza.
- **Diseña para el recorte de la cuadrícula.** La cuadrícula del perfil recorta
  a un rectángulo vertical, más alto que ancho, y la proporción exacta ha
  cambiado más de una vez. Monta a 1080x1350, deja el texto de la portada bien
  metido en el centro, lejos de los 120 píxeles exteriores de cada lado, y el
  recorte deja de importar.
- **Numera las diapositivas** (3/8). La finalización sube cuando la gente ve
  dónde está el final.
- **Ninguna diapositiva es un párrafo.** Si no cabe en 25 palabras, pártela.
- **La diapositiva de resumen es la que la gente captura y envía.** Los envíos
  son la señal más fuerte que te puedes ganar. Haz que se sostenga sola y que se
  lea sin contexto.
- **El nombre de usuario (@) en cada diapositiva**, pequeño, en una esquina de
  abajo. Las capturas viajan sin ti.
- **Texto alternativo al menos en la portada.** Lo leen los lectores de
  pantalla y también Instagram.

## Cómo montar los archivos

Instagram pide 1080x1350 (4:5), JPEG o PNG, hasta 20 elementos. Móntalo en
HTML e imprime cada diapositiva:

```bash
# un <section> por diapositiva, 1080x1350, page-break-after: always
# luego Chrome headless --print-to-pdf, o el conversor de HTML a imagen que ya uses
```

Escribe el HTML con `width:1080px; height:1350px`, un solo color de acento y
ningún texto por debajo de 32px, porque se lee en un móvil a un tercio de su
tamaño real. Si el proyecto tiene una skill de marca o un sistema de diseño,
úsalo y no te inventes una paleta.

## Salida

Primero el texto diapositiva a diapositiva, como una lista numerada que el
usuario pueda leer en diez segundos y editar antes de renderizar nada. Luego el
**texto (caption)**, que en un carrusel es la función B de `/ig-caption`: aquí
el texto trabaja, porque la portada ya ha gastado sus seis palabras.

Pasa los dos por `/ig-human`. Monta los archivos solo cuando el usuario apruebe
el texto.

```
CARRUSEL  ·  8 diapositivas

1  PORTADA   LA CLÁUSULA DE 18.000 €
             Una frase que ahora pongo en todos mis contratos.
2  EN JUEGO  Me aprobaron el trabajo. Nueve días después querían el dinero de vuelta.
3            QUÉ DICE
             Pago a la entrega, no a la aprobación.
...
7  RESUMEN   Las cuatro frases, en orden.
8  CTA       Comenta CONTRATO y te mando la cláusula completa.

Texto: función B, gancho en la línea 1, una petición, 3 hashtags.
```

Nada se sube. El usuario lo publica.
