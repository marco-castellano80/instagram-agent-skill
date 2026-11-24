---
name: ig-audit
description: >-
  Autopsia de lo que el usuario ya ha publicado: qué reels funcionaron de
  verdad y por qué, y qué conviene dejar de hacer. Úsala cuando el usuario
  pegue sus estadísticas de Instagram o publicaciones anteriores y pregunte
  «qué está funcionando», «por qué ha fracasado esto», «léeme las
  estadísticas», «audita mi contenido», o quiera saber de qué hacer más.
---

# ig-audit

Escribe siempre en español, en la variante que diga `~/.claude/instagram/voice.md`
(España, Latinoamérica o neutro). Si no lo dice, español neutro con «tú».

La única fuente honesta de lo que funciona en una cuenta es esa cuenta. Todas
las reglas de todas las guías de Instagram, incluidas las de este paquete, son
una hipótesis de partida. Las 30 últimas publicaciones del usuario son la
prueba.

## Entrada

Pide lo que el usuario tenga:

- Estadísticas por publicación: visualizaciones, alcance, interacciones,
  tiempo de visualización, guardados, envíos, seguidores ganados y la parte del
  alcance que viene de no seguidores. Las capturas valen.
- O el gráfico de retención de sus mejores y peores reels recientes. Esa sola
  captura vale más que todo lo demás junto.
- O solo las publicaciones con sus visualizaciones, que basta para una primera
  pasada.

Lee también `~/.claude/instagram/log.md` si existe, porque ahí consta qué
fórmula de gancho usó cada publicación.

## Qué medir de verdad

Las visualizaciones a secas son la cifra menos útil de la pantalla, porque
dependen sobre todo de cuánta gente sigue ya la cuenta. Calcula esto en su
lugar y enseña las cuentas:

| métrica | cómo | qué te dice |
| --- | --- | --- |
| **Múltiplo sobre la mediana** | visualizaciones / mediana de visualizaciones de la propia cuenta | si fue un éxito de verdad o un día normal |
| **Alcance a no seguidores** | % del alcance que viene de gente que no sigue la cuenta | si salió de su círculo |
| **Retención a los 3 s** | espectadores que siguen a los 3 s / espectadores que empezaron | si el gancho funcionó. Es la nota del gancho. |
| **Tiempo medio de visualización** | directo de las estadísticas | si funcionó la parte del medio |
| **Envíos por alcance** | envíos / alcance | la señal más fuerte que puedes ganarte. Un envío es alguien que pone su nombre detrás. |
| **Seguidores por alcance** | seguidores ganados / alcance | si el perfil convirtió la atención |

Ordena por múltiplo sobre la mediana y por envíos por alcance, no por
visualizaciones. Un reel con 4.000 visualizaciones y 90 envíos le ganó al de
60.000 visualizaciones y 11.

## Luego busca el patrón

Con los cinco mejores y los cinco peores lado a lado, busca qué los separa, y
atrévete a concluir algo que al usuario no le va a gustar:

- **Retención a los 3 segundos.** Si los mejores y los peores se diferencian
  aquí, es el gancho y nada más, y todo lo que viene después distrae.
- **Fórmula de gancho.** ¿Qué ids de `ig-reel/hooks.es.json` están entre los
  cinco mejores?
- **Formato.** Reel, carrusel o imagen única.
- **Duración.** Agrupa en menos de 15 s, de 15 a 30 s, de 30 a 60 s y más de
  60 s.
- **Tema.**
- **Si el usuario respondió a los comentarios en la primera hora.**
- **Día y hora.** Mira esto **lo último**, y solo si lo demás no enseña nada.
  Casi nunca es la causa, y es donde la gente quiere que esté.

Expresa el hallazgo como una afirmación con la prueba al lado, y di cuánta
confianza merece. Con 30 publicaciones se ve un patrón. Con 6 no, y decirlo es
mejor que inventarse uno.

## La distinción que ahorra meses

**Un reel con visualizaciones y sin seguidores nuevos tiene un problema de
perfil, no de reel.** Un reel sin visualizaciones tiene un problema de gancho.
Separa las dos cosas antes de recomendar nada. Si el alcance a no seguidores es
alto y los seguidores por alcance son bajos, deja de reescribir ganchos y pasa
a `/ig-profile`.

## Salida

```
AUDITORÍA  ·  31 publicaciones  ·  12 jun - 5 sep  ·  mediana 4.100 vistas

LOS 5 MEJORES POR MÚLTIPLO SOBRE LA MEDIANA
  18,2x  #3  Nadie te lo dice    74.600 vistas  62% no seguid.  ret. 3 s 71%  128 envíos
   6,4x  #1  Lo que me costó     26.300 vistas  48% no seguid.  ret. 3 s 64%   71 envíos
  ...

LOS 5 PEORES
   0,3x  #11 Lista con favorita   1.200 vistas   9% no seguid.  ret. 3 s 31%    2 envíos
  ...

LO QUE DICEN LOS DATOS
1. La retención a los 3 segundos lo explica todo. Los cinco mejores tienen
   una media del 66%, los cinco peores del 33%. Todo lo demás que te preocupa
   depende de los dos primeros segundos.
2. Las publicaciones en las que el que quedaba mal eras tú: media de 8,1x
   frente a 0,9x en todo lo demás. n=5. Es la señal más fuerte de aquí, y con
   mucha diferencia.
3. Las listas de herramientas traen visualizaciones y nada más. Mucho alcance,
   ningún envío, ningún seguidor. Son tres de tus cinco peores.
4. El día de la semana no enseña nada. Tus medias del martes y del viernes
   están dentro del ruido. Deja de optimizarlo.

DEJA DE HACER: listas de herramientas.
HAZ MÁS: las que llevan un coste que pagaste y una cifra.
```

Después pasa las conclusiones a `/ig-plan`, para que la semana que viene se
construya con las pruebas del propio usuario y no con valores por defecto, y a
`/ig-viral`, para que el swipe file se filtre por las fórmulas que funcionan en
esta cuenta en concreto.
