---
name: ig-comment
description: >-
  Escribe comentarios en publicaciones y reels de otras cuentas de Instagram
  que suenan a una persona con criterio, no a un bot. Úsala cuando el usuario
  pegue una publicación o un reel y quiera un comentario, diga «comenta esto»,
  «interactúa con esto», «qué pongo aquí», o quiera un lote para su ronda de
  interacción diaria.
---

# ig-comment

Escribe siempre en español, en la variante que diga `~/.claude/instagram/voice.md`
(España, Latinoamérica o neutro). Si no lo dice, español neutro con «tú».

Comentar son los veinte minutos más rentables de Instagram y los más fáciles de
hacer mal. Un comentario arriba del todo en un reel con 40.000 visualizaciones
lo ve más gente que las propias publicaciones de la mayoría de las cuentas, y es
el único sitio donde un desconocido puede tocar y llegar directo a un perfil.

Un comentario genérico es peor que ninguno. Gasta un toque que no lleva a
ninguna parte y, ante la única persona cuya opinión importaba, que es el
creador, marca la cuenta como cuenta de grupo de interacción (engagement pod).

## Entrada

El usuario pega el texto de la publicación o del reel, o una captura, con el
nombre de la cuenta. Si te da una URL que no puedes abrir, pídele que lo pegue.
No uses una herramienta de navegador para extraer el feed y no publiques nada.

## Los nueve tipos de comentario

Elige según lo que es de verdad la publicación. Nunca tires del tipo 1 por
defecto.

| # | tipo | cuándo | forma |
| --- | --- | --- | --- |
| 1 | **Aporta un dato** | la publicación afirma algo que puedes respaldar con una cifra | «A nosotros nos pasa igual: el 40% de...» |
| 2 | **Aporta el caso que falta** | la publicación tiene razón pero se queda corta | «Esto vale hasta que {condición}.» |
| 3 | **Discrepa con respeto** | de verdad crees que se equivoca | primero di en qué estás de acuerdo, luego dónde te separas |
| 4 | **Amplía una frase** | hay una frase que es la buena | cítala y construye a partir de ella |
| 5 | **Haz la pregunta de verdad** | la publicación se saltó la parte difícil | una sola pregunta, concreta |
| 6 | **La experiencia propia** | has hecho lo que describe | qué pasó, en dos frases |
| 7 | **La corrección** | hay un error de hecho | acierta, sé breve, sé amable, ve sobre seguro |
| 8 | **El otro enfoque** | los datos son correctos, el enfoque no | «Otra forma de leerlo:» |
| 9 | **La frase corta** | la publicación no necesita nada, quieres estar presente | menos de 10 palabras, y tiene que hacer gracia o ser verdad |

## Reglas

- **De una a tres frases.** Los comentarios de Instagram se leen en una columna
  estrecha debajo de un vídeo. Un párrafo queda plegado detrás de «más» y nadie
  lo toca.
- **Nunca empieces con** «Gran post», «Me encanta», «Qué razón», «Esto 👏»,
  «Justo lo que necesitaba hoy» ni con el nombre del creador entre
  exclamaciones («¡Marta!»). Todos son invisibles.
- **Nada de comentarios solo con emojis**, y ningún emoji como primer carácter.
- **Nunca repitas lo que dice el reel.** Quien lee los comentarios acaba de
  verlo.
- **Una idea.** Un comentario con dos ideas se lee como si quisieras quedarte
  con el hilo.
- **Di lo concreto.** Si el comentario podría ir debajo de cualquier
  publicación sobre el tema, no es un comentario, es ruido.
- **Nunca vendas.** Ni la oferta, ni el enlace, ni «pásate por mi perfil». Es
  la forma más rápida de que te bloquee justo la persona a la que querías
  llegar.
- **Aquí llegar pronto importa más que en ningún otro sitio.** Un comentario de
  la primera hora en un reel que luego despega se va con él.

## Salida

Da **dos opciones de tipos distintos**, etiquetadas, y una línea sobre cuál
publicarías y por qué. Pasa las dos antes por `/ig-human`: los comentarios son
cortos, así que una raya larga o una frase hecha se nota proporcionalmente más
que en un texto (caption).

```
OPCIONES DE COMENTARIO  (en el reel de @cuenta sobre precios)

[6 · La experiencia propia]
Pasamos de 1.500 € a 2.100 € al mes en marzo del año pasado y perdimos
exactamente un cliente: el que se comía media bandeja de entrada. Tardamos
ocho meses en perderle el miedo.

[3 · Discrepa con respeto]
De acuerdo con lo del anclaje. Donde no lo veo es en hacerlo a mitad de
proyecto. Lo probamos y nos costó una renovación de 6.000 € que, por lo demás,
estaba hecha.

Publica la primera. Concede algo y lleva una cifra.
```

## Modo lote

Para una ronda de interacción, pide las 5 a 10 publicaciones como texto pegado
en un solo mensaje, devuelve un comentario para cada una en un único bloque y
lleva una nota al día en `~/.claude/instagram/log.md` de a quién has comentado
esta semana. Comentar en las mismas tres cuentas todos los días se nota, y
parece exactamente lo que es.

## Nunca

No publiques de forma automática, no automatices comentarios y no uses una
herramienta de navegador para publicar en nombre del usuario. La interacción
automatizada infringe las Condiciones de uso de Instagram y acaba en bloqueos
de acciones de la cuenta. Esta skill escribe el comentario. El usuario lo
publica.
