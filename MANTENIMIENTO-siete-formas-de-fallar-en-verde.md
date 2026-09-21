# Siete formas de fallar en verde

Documento de mantenimiento. Los siete patrones que hicieron daño en este
repositorio y que **volvieron a aparecer dentro de una misma jornada de
trabajo**. No son bugs: son formas de construir que se leen bien, pasan los
tests, y no sostienen lo que aparentan.

Cada uno viene con las veces que se lo vio, no porque esos casos importen —
están arreglados y archivados— sino como prueba de que el patrón es real y no
una precaución teórica.

Escrito 2026-09-20.

---

## 1. Una exigencia sin forma de contestarla

Una máquina pide algo y no provee cómo dárselo. Quien la usa tiene dos salidas:
inventar un valor para pasar, o quedarse trabado.

**Siempre elige inventar.** Y el valor inventado queda con cara de decisión
tomada.

> Es la aguja pegada: el mecánico arregla el testigo del combustible, pero para
> cerrar el trabajo pega la aguja en "medio tanque". El testigo anda y el tanque
> miente para siempre.

**Visto dos veces el mismo día.** Un cambio hizo que escribir un bloque exigiera
saber de qué sección sale, sin construir nada que lo grabara: el único camino
era editar a mano un archivo que se reparte. Después, otro exigió una
declaración de raíz que tampoco tenía verbo que la escribiera, y el hueco lo
tapaba un agente escribiendo JSON por fuera.

**La prueba:** parate en el momento en que la máquina rehúsa y preguntá *"¿con
qué contesto esto?"*. Si la respuesta es "editando un archivo" o "un agente lo
escribe", la llave no existe.

**El arreglo tiene tres partes y ninguna sobra:** que exista dónde ponerlo, que
exista **cómo** ponerlo —un verbo, no un editor—, y que la negativa **nombre**
ese cómo.

---

## 2. Un guard que no puede dispararse

Un guard presente y un guard alcanzable se leen idéntico. El código está, el
test pasa, el roster lo lista — y nunca corre.

**Cuatro maneras de que pase, las cuatro vistas acá:**

- **Cableado solo a un verbo de solo-lectura.** El reporte avisa y el camino que
  escribe pasa de largo. Van nueve casos medidos en este repo; casi hubo un
  décimo.
- **Ordenado después de algo más estricto.** Un chequeo de concesión puesto
  detrás del rechazo estructural nunca llega a dispararse: el otro intercepta
  todo primero.
- **Invisible para el derivador.** El roster se arma con un escaneo estático.
  Re-lanzar un rechazo con una variable en vez de un texto literal hace que el
  guard funcione y el roster no lo vea jamás.
- **Con una fórmula que no distingue.** Una mutación probada contra un caso
  donde la versión correcta y la rota dan el mismo número no prueba nada. Hizo
  falta un caso de tres para separarlas.

**La prueba, y es la única:** rompé el guard y mirá el test ponerse rojo. Un
test que pasa contra el motor sano no dice nada sobre si el guard sostiene.

Y dos trampas al ejecutar mutaciones: una mutación del mismo tamaño puede reusar
el bytecode viejo, así que el código mutado nunca corre; y `git diff --stat` no
prueba nada sobre un archivo no versionado.

---

## 3. Prosa que sobrevive a su mecanismo

Un documento afirma un comportamiento. El comportamiento cambia, o nunca se
implementó. El documento sigue ahí, afirmándolo.

**Un documento no se ejecuta.** Por eso no se entera.

**Cuatro casos en un día, y el dato que más importa: a los cuatro los encontró
un cambio posterior yendo a apoyarse ahí. Ninguno lo encontró su propia
verificación.** Un diseño archivado prometía que una función devolvía algo que
su firma declaraba `None`. Una tarea tildada decía que un dato salía por tres
verbos y no salía por ninguno. Una propuesta afirmaba un insumo que el diseño
nunca ruteó. Un conteo de verbos nació viejo el día que se lo "arregló".

**Las dos reglas:**

> No heredes ninguna afirmación de un artefacto anterior sin volver a medirla.
> Si vas a apoyarte en que algo funciona, corrélo.

> La prueba de que algo se ve es **correr el verbo y leer lo que imprime**.
> Afirmar que un campo existe en un objeto es exactamente el test que dejó pasar
> una tarea tildada a medias.

---

## 4. Decidir en lugar de preguntar

Una decisión que le pertenece a una persona la termina tomando una máquina, un
agente leyendo prosa, o una conversación armada para destrabar otra cosa.

Pasa sin mala intención: alguien necesita seguir, la decisión parece obvia, y
queda tomada.

**Tres formas, las tres vistas:**

- **Un agente deriva y graba.** Leyó la prosa de un contrato, dedujo un valor y
  lo escribió. Nadie lo eligió.
- **Yo trasladé la invención como pregunta.** En vez de leer que la máquina había
  obligado a inventar, le llevé la invención al dueño para que la ratificara.
- **Una concesión por amabilidad.** Un agente que acepta la propuesta del dueño
  porque es del dueño, no porque sea mejor.

**La regla:** una decisión se toma **usando** la skill, nunca editando un
archivo, nunca en una charla armada para destrabar una reparación. Que alguien
diga "sí" mirando una tabla no es lo mismo que la máquina parándolo en el
momento justo, con el material delante.

**Y el corolario estructural:** si el artefacto de una negociación lleva un
campo que diga de quién es cada propuesta, la máquina no puede verificarlo — es
un reclamo de autoridad disfrazado de esquema. Que no lo lleve, y que las dos se
puntúen igual.

---

## 5. Un número elegido, presentado como medido

Un umbral, un piso, un conteo. Se elige por criterio, se escribe sin marca, y
seis meses después nadie sabe que fue una decisión. Un número que nadie puede
discutir es un número que nadie midió.

**Los dos lados, los dos vistos:**

- **Elegido y declarado como tal.** Un umbral de repetición se fijó en 16 porque
  el 8 original se había calibrado contra papers de otros autores y no
  transfería. Quedó escrito que es un fallo, con qué lo falsificaría, y el piso
  se **reporta en cada respuesta** para que sea contestable.
- **Medido cuando se podía medir.** Un piso de versión de Python se derivó
  escaneando qué construcciones usa el código, en vez de elegir un número
  razonable.

**La regla:** si se puede medir, medilo. Si no, decí que es un fallo y escribí
qué lo cambiaría. Y cuando el número gobierna un comportamiento, **reportalo en
la salida**: es lo que lo vuelve discutible el día que haya datos.

Y una forma de sostenerlo que funciona mejor que la buena voluntad: si una frase
tiene que decir la verdad en cuatro lugares, hacela **una constante única** con
un test que exija que los cuatro coincidan. Decirlo mal pasa a ser un test rojo
en vez de algo que un revisor tiene que notar.

---

## 6. Arreglar la instancia y dejar la clase

Se encuentra un defecto, se arregla donde se lo vio, y la misma forma queda en
pie en otros dos lugares.

**Tres veces:**

- Una función que normalizaba texto dejaba pasar las ecuaciones. Había **dos
  copias** con el mismo error, y la segunda alimentaba un guard distinto.
- El guard de vocabulario derivaba su lista prohibida leyendo **una sola** raíz
  de producto. Los nombres de las otras le eran invisibles, y por eso catorce
  líneas entraron a archivos que se reparten con toda la suite en verde.
- Un conteo clavado protegía a una skill y no a sus hermanas.

**La pregunta, cada vez:** *¿qué más tiene esta misma forma?*

**Y el arreglo correcto no es tocar los dos lugares: es que algo derivado los
encuentre.** Una lista de dos envejece cuando alguien escribe el tercero. Un
barrido que introspecciona todos los módulos, no.

---

## 7. Un test que ratifica una decisión en vez de verificar una propiedad

Un test cuenta cuántos elementos hay en una lista, o transcribe cuáles son.
Pasa. Y desde ese momento la lista **no se puede cambiar sin ponerlo rojo** —
aunque nadie haya decidido nunca que fuera esa lista.

El test deja de proteger un comportamiento y pasa a **custodiar una elección**.
Peor: el nombre del test la enuncia como si fuera un requisito.

**El caso:** una skill declaraba tres carpetas de origen. Un test se llamaba
*"tres fuentes están declaradas: el paper de datos y la propuesta son
obligatorias, el benchmark del área no"* y afirmaba `sources.length === 3`.
Cuando el dueño dijo *"ese benchmark nunca lo autoricé"*, sacarlo puso el test
en rojo. El test no estaba defendiendo una propiedad de la skill: estaba
defendiendo que alguien, una vez, había escrito tres.

> Es la aguja pegada otra vez, pero al revés: acá no se falsea el dato para que
> el testigo pase — se atornilla el testigo para que el dato no se pueda mover.

**Cómo distinguirlos.** Preguntale al test *"¿qué se rompería en producción si
esto fuera distinto?"*

- *"Nada, sería otra decisión igual de válida"* → está ratificando.
- *"El motor leería una fuente que no existe"* → está verificando.

**El arreglo no es borrar el test, es cambiar qué afirma.** En vez de contar
elementos, afirmá la propiedad que la lista tiene que cumplir pase lo que pase:
que toda fuente declarada exista, que la fuente que acota las afirmaciones sea
una de las declaradas y sea obligatoria, que ninguna ruta se escape del
repositorio. Esas siguen siendo ciertas con dos fuentes, con tres o con siete —
y siguen poniéndose rojas cuando algo se rompe de verdad.

**Y el corolario, que es el que más cuesta:** un conteo en un test es el lugar
donde una decisión no tomada se vuelve indistinguible de un requisito. Si el
número tiene que estar, que el test diga **por qué es ese número**, y que el
comentario nombre a quién lo decidió y cuándo. Un conteo sin esa línea es una
decisión anónima con fuerza de ley.

---

## Cómo se ven juntos

Los siete comparten una raíz: **algo se lee como una garantía sin serlo.**

```
1  una exigencia se lee como una regla        y obliga a inventar
2  un guard se lee como protección            y no puede dispararse
3  un documento se lee como el estado         y describe otro
4  un valor se lee como una decisión          y lo puso una máquina
5  un número se lee como medido               y fue elegido
6  un arreglo se lee como cerrado             y la clase sigue abierta
7  un test se lee como un requisito           y custodia una elección
```

Por eso ninguno se detecta leyendo. Los seis se detectan **corriendo**: el verbo
y su salida, la mutación y su rojo, el documento contra el código, la negativa
contra lo que hay para contestarla.

---

## Qué preguntar antes de dar un cambio por cerrado

- ¿Algo que este cambio **exige** tiene forma de contestarse usando la skill?
- Cada rechazo nuevo, ¿lo vi ponerse **rojo** bajo mutación, o solo pasa verde?
- ¿Algún rechazo queda alcanzable solo desde un verbo que no escribe?
- ¿Algún documento que toqué afirma algo que no corrí?
- ¿Alguna decisión de este cambio la tomó un agente, o yo, en vez de la persona
  usando la skill?
- ¿Algún número nuevo se presenta como medido sin serlo?
- El defecto que arreglé, ¿tiene hermanos con la misma forma? ¿Y lo que los
  encuentra es derivado o es una lista?
- Cada test nuevo que cuenta o enumera, ¿qué se rompería en producción si el
  número fuera otro? Si la respuesta es "nada", está ratificando una decisión,
  no verificando una propiedad.
