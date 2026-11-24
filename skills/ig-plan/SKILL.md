---
name: ig-plan
description: >-
  Monta la semana en Instagram: qué publicar, en qué formato, cuándo y con
  quién interactuar. Úsala cuando el usuario diga «planifícame la semana», «qué
  publico», «calendario de contenido», «no tengo nada sobre lo que publicar», o
  quiera un calendario de publicación y una lista de interacción.
---

# ig-plan

Escribe siempre en español, en la variante que diga `~/.claude/instagram/voice.md`
(España, Latinoamérica o neutro). Si no lo dice, español neutro con «tú».

La sala de control. Todo lo demás de este paquete ejecuta; esta skill decide
qué se ejecuta. Úsala una vez por semana, siempre el mismo día.

## Entrada

Si existen `~/.claude/instagram/voice.md`, `swipe.md` y `log.md`, léelos. El
swipe file es la prueba del propio usuario, sacada con `/ig-viral`, de qué
fórmulas están funcionando ahora mismo en su nicho, y pesa más que cualquier
cosa de este archivo. El registro (`log.md`) evita que el plan repita un tema
de las dos últimas semanas.

Si no existen, pide cuatro cosas y apúntalas:

1. Qué vende el usuario y a quién.
2. Los tres o cuatro temas por los que quiere que lo conozcan.
3. Qué ha pasado de verdad esta semana: una llamada con un cliente, una cifra,
   un error, algo que construyó, una discusión que tuvo. De ahí salen las
   publicaciones.
4. Diez cuentas ante las que vale la pena dejarse ver.

## Qué publicar

De cuatro a cinco publicaciones a la semana, y al menos tres de ellas reels.
Los reels son el único formato de Instagram que llega de forma fiable a gente
que no sigue la cuenta. Los carruseles profundizan con quien ya la sigue. Las
historias son diarias y se planifican aparte.

Mezcla a lo largo de la semana, nunca dos del mismo tipo seguidas:

| tipo | cuántas | función |
| --- | --- | --- |
| **Prueba** | 1 por semana | algo que pasó, con una cifra. Reel. |
| **Enseñar** | 1 o 2 por semana | una cosa que el espectador puede hacer hoy. Reel o carrusel. |
| **Opinión** | 1 por semana | una postura que podría costarte seguidores. Reel. |
| **Relato** | 1 cada dos semanas | una escena con un coste. Reel. |
| **Oferta** | 1 cada dos semanas | lo que vendes, dicho claro, sin pedir perdón. Carrusel o historias. |

Para cada hueco da el tema, el ángulo concreto sacado de lo que pasó de verdad
esta semana, el formato y el número de fórmula de gancho de
`ig-reel/hooks.es.json`. No un tema, un ángulo. «IA» no es un plan. «La
propuesta que perdimos porque el borrador tenía una raya» es un reel.

## Cuándo publicar

Publica cuando la audiencia del usuario esté despierta y no esté trabajando.
Para la mayoría de las audiencias de consumo eso es a última hora de la tarde,
hora local; para una audiencia profesional, a primera hora de la mañana.

Pero dilo claro: **la hora importa mucho menos que los dos primeros
segundos.** Instagram sigue enseñando un reel durante días si funciona, y
entierra uno publicado a la hora perfecta si no funciona. Si el usuario está
optimizando la hora de publicación antes de que sus ganchos funcionen, está
puliendo lo que no toca, y se lo tienes que decir.

Si la zona horaria de la audiencia y la del usuario no coinciden, ancla las
horas a la de la audiencia.

## La ronda de interacción, que no es opcional

20 minutos al día, antes de publicar, no después. Haz una lista de 10:

- **5 de alcance**: cuentas con la audiencia que el usuario quiere, donde un
  buen comentario se ve. Comenta pronto, antes de que el hilo tenga 200
  comentarios.
- **3 pares**: mismo tamaño, mismo sector. Es el grupo que devuelve la
  interacción.
- **2 compradores**: gente que de verdad podría comprar. Comenta durante
  semanas antes de mandar ningún DM, y nunca vendas en un comentario.

Pásale la lista a `/ig-comment`.

## Salida

```
SEMANA DEL 15 DE SEPTIEMBRE

LUN  solo interacción  (20 min, lista abajo)
MAR  19:30  REEL      PRUEBA   #5  El tiempo comprimido   - propuesta de 5 h a 20 min
MIÉ  solo historias + interacción
JUE  19:00  CARRUSEL  ENSEÑAR  texto función B            - la cláusula en 4 diapositivas
VIE  19:30  REEL      OPINIÓN  #2  La orden negativa      - deja de hacer llamadas de descubrimiento
SÁB  -
DOM  18:00  REEL      RELATO   #21 Empezar a media frase  - el correo del reembolso

HISTORIAS  todos los días, de 3 a 5 pantallas, sticker de preguntas el jueves.

INTERACCIÓN  (5 alcance / 3 pares / 2 compradores)
  ...

Di "escribe el martes" y te lo redacto.
```

Escribe el plan en `~/.claude/instagram/plan.md` para que las demás skills
puedan leerlo. No se programa ni se publica nada en ningún sitio. Esto es un
plan, y quien lo ejecuta es el usuario.
