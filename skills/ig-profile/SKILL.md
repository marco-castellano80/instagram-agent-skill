---
name: ig-profile
description: >-
  Puntúa un perfil de Instagram sobre 100 con una rúbrica de 12 apartados y
  reescribe las partes que pierden puntos: campo de nombre, bio, enlace,
  historias destacadas, las tres fijadas y la cuadrícula. Úsala cuando el
  usuario diga «optimiza mi perfil», «arréglame la bio», «puntúa mi
  Instagram», «por qué no me sigue la gente», o pegue su perfil y pregunte cómo
  se lee.
---

# ig-profile

Escribe siempre en español, en la variante que diga `~/.claude/instagram/voice.md`
(España, Latinoamérica o neutro). Si no lo dice, español neutro con «tú».

Casi todo el mundo optimiza aquí lo que no es. El perfil no es un escaparate
por el que la gente pasea. Es una **pantalla de decisión** a la que se llega
desde un reel, y tiene unos tres segundos para responder a una pregunta: ¿hay
más de eso aquí, y es para mí?

## Entrada

Pide al usuario que pegue o haga captura de: el campo de nombre, el nombre de
usuario (@), la bio, adónde lleva el enlace, los nombres de las historias
destacadas, lo que tiene fijado y las nueve primeras portadas de la cuadrícula.
Para una primera pasada basta una captura de la parte de arriba del perfil más
las dos primeras filas de la cuadrícula.

No inicies sesión en Instagram en su nombre.

## Puntúalo

Lee `rubric.es.json` en esta carpeta. Doce apartados, 100 puntos, cada uno con
cómo es la nota máxima y cómo suele fallar. Puntúa todos, enseña la tabla y da
el total. Sé honesto. En la primera pasada la mayoría de los perfiles se quedan
entre los 30 y los 49 puntos, y una nota generosa no sirve de nada.

```
NOTA DEL PERFIL  38/100

  campo de nombre          2/12   solo el nombre, ninguna palabra que alguien busque
  primera línea de la bio  3/12   tres sustantivos y un emoji de café
  las tres fijadas         0/10   nada fijado
  historias destacadas     2/8    "Random", "Vida", "2023"
  cuadrícula legible       4/8    seis de nueve portadas son una cara a media frase
  ...
```

## Luego reescribe, en este orden

Arregla de más a menos puntos perdidos. No lo reescribas todo de golpe: el
usuario tiene que ir a cambiar cada cosa a mano.

**1. El campo de nombre (30 caracteres).** La línea en negrita debajo de la
foto, no el nombre de usuario. Es el campo con el que compara el buscador de
Instagram, y la mayoría de las cuentas ponen ahí un nombre y nada más. El
formato que funciona: `{Nombre} | {lo que haces, con palabras que se buscan}`.
Da tres opciones.

**2. La primera línea de la bio.** Para quién es y qué cambia. No un cargo, no
adjetivos, no una lista de identidades separadas por barras. El resto de los
150 caracteres lleva una prueba o una oferta dicha claro.

**3. Las tres fijadas.** Tres huecos, tres funciones distintas: la mejor
prueba, la explicación más clara de la oferta, la mejor presentación de la
persona. Es el arreglo que más rinde de todo el perfil y son cuatro toques. Una
cuadrícula sin nada fijado enseña lo último que se publicó, que es jugárselo a
cara o cruz.

**4. Historias destacadas.** De cuatro a seis, con el nombre de las preguntas
que hace un comprador: «Precios», «Resultados», «Cómo funciona», «Sobre mí».
Nada de «Random». Borra el resto.

**5. El enlace.** Un destino que cuadre con lo que la bio acaba de prometer. Se
permiten cinco; dos ya es un menú, y un menú convierte peor que una puerta.

**6. Portadas de la cuadrícula.** Las nueve primeras, a tamaño miniatura. Las
portadas de los reels se eligen, no se deja el primer fotograma que salga.
Cuatro palabras de texto en una portada hacen que la cuadrícula se lea de un
vistazo.

## Salida

La tabla de puntos y después las reescrituras como bloques listos para copiar,
en orden de arreglo, cada una pasada por `/ig-human`. Vuelve a puntuar al final
y enseña la diferencia con honestidad. Si la reescritura llega a 84 y no a 98,
di 84, y di qué necesita el resto, que suele ser una cuadrícula, la costumbre
de subir historias y una publicación fijada que todavía no existe. Nada de eso
es una reescritura.

Esta skill no guarda nada en Instagram. El usuario edita cada campo.
