---
title: Manifiesto Agil y mentalidad
date: 2026-06-13
tags: [programacion/agile, programacion/proceso-software, programacion/metodologias]
type: nota
status: en-progreso
source: claude-code
aliases: [Manifiesto Agil, Agile, mentalidad agil]
---

# Manifiesto Agil y mentalidad

## ¿Por qué existe el Manifiesto?

En los años 90, el desarrollo de software seguia el modelo **Waterfall** (cascada): análisis completo → diseño completo → implementación → pruebas → entrega. El problema es que para cuando el software llegaba al cliente, los requisitos habían cambiado, el mercado había evolucionado, o el equipo había malinterpretado lo que se pedía. Se entregaba tarde, por encima del presupuesto, y a menudo no era lo que el cliente necesitaba.

En febrero de 2001, 17 desarrolladores experimentados se reunieron en Utah (EEUU) y redactaron el **Manifiesto Agil**: un documento de dos páginas que captura una forma diferente de entender el trabajo de software. No es un framework ni un proceso: es una **declaración de valores y principios**.

> El Manifiesto Agil no resuelve el problema de "cómo organizar el trabajo". Resuelve el problema de **"qué priorizar cuando hay tension entre dos cosas buenas"**.

---

## Los 4 Valores

El Manifiesto dice literalmente: *"Valoramos los elementos de la izquierda por encima de los de la derecha."* Importante: no dice que los de la derecha no tengan valor. Dice qué gana cuando hay tensión.

### Valor 1 — Individuos e interacciones **sobre** procesos y herramientas

**El problema que resuelve:** los equipos que siguen el proceso "porque así es como se hace" sin pensar, o que dependen de la herramienta para coordinarse en lugar de hablar.

**Qué significa en la práctica:**
- Una conversación de 5 minutos entre dos personas vale más que un ticket de Jira perfectamente documentado.
- Si el proceso impide que dos personas colaboren bien, cambia el proceso.
- Las herramientas sirven al equipo; el equipo no sirve a las herramientas.

**Ejemplo:** Tienes un bug que bloquea a un compañero. Según el proceso, debes abrir un ticket, asignarlo, esperar la reunión de priorización. Mentalidad agil: le preguntas directamente si lo resuelves ahora, y si tiene sentido, lo haces. El proceso existe para coordinar, no para bloquear.

**Lo que NO significa:** ignorar los procesos o las herramientas. Significa que si hay un conflicto, las personas y su colaboración ganan.

---

### Valor 2 — Software funcionando **sobre** documentación exhaustiva

**El problema que resuelve:** equipos que pasan meses documentando requisitos en documentos de 200 páginas que quedan obsoletos al primer cambio real.

**Qué significa en la práctica:**
- La medida de progreso es software que funciona y aporta valor, no documentos aprobados.
- La documentación debe ser suficiente para el objetivo, no exhaustiva por protocolo.
- Mejor un prototipo funcional que un spec perfecto en papel.

**Ejemplo:** En tu app web, en lugar de documentar durante 2 semanas todos los endpoints posibles antes de escribir código, construyes el endpoint de registro de comidas, lo pruebas con el usuario real, y ajustas. La documentación útil (README, decisiones de arquitectura) se escribe conforme hace falta.

**Lo que NO significa:** no documentar nada. Significa que si tienes que elegir entre entregar código que funciona o entregar un documento, el código gana. La documentación que nadie lee no aporta valor.

---

### Valor 3 — Colaboración con el cliente **sobre** negociación de contratos

**El problema que resuelve:** la dinámica adversarial de "el cliente pide X, firmamos X, y si cambia de opinión nos paga más". Esta dinámica incentiva al cliente a especificarlo todo desde el principio (imposible) y al equipo a resistirse a cambios.

**Qué significa en la práctica:**
- El cliente no es alguien a quien entregarle un producto al final: es parte del proceso continuo.
- Las demos frecuentes, el feedback temprano y la conversación regular son más valiosos que un contrato blindado.
- El objetivo compartido es software que resuelva el problema real, no cumplir literalmente el contrato.

**Ejemplo:** En un proyecto freelance, en lugar de fijar absolutamente todo al inicio y luego facturar extras, trabajas en ciclos cortos, muestras avances y ajustas. El cliente ve valor antes, tú reduces el riesgo de construir lo incorrecto.

**Lo que NO significa:** no tener contratos ni acuerdos. Significa que la relación y la comunicación continua son más valiosas que el blindaje contractual.

---

### Valor 4 — Responder al cambio **sobre** seguir un plan

**El problema que resuelve:** equipos que siguen el plan original aunque el contexto haya cambiado, porque "así lo planificamos". El plan se convierte en el objetivo en lugar de ser un medio.

**Qué significa en la práctica:**
- El mundo cambia: el mercado, la tecnología, el conocimiento del problema. El plan debe adaptarse.
- Planificar en el corto plazo con precisión y en el largo plazo con holgura.
- Cambiar de dirección cuando tienes nueva información no es fracasar: es aprender.

**Ejemplo analogía hardware:** Diseñas un PCB y en la revisión descubres que el sensor elegido tiene un lead time de 6 meses. No sigues el plan original porque "ya lo habías especificado". Adaptas: buscas alternativa, replanteas. En software, el equivalente es cuando aprendes que una tecnología no escala o que el usuario no usa la feature que construiste.

**Lo que NO significa:** no planificar. Significa que el plan es un artefacto vivo, no un contrato sagrado. *Agile no es ausencia de plan: es capacidad de actualizar el plan con nueva información.*

---

## Los 12 Principios

Los principios son la aplicación concreta de los valores. Se agrupan naturalmente en cuatro bloques temáticos:

### Bloque A — Entrega de valor

| # | Principio | Clave práctica |
|---|---|---|
| 1 | Satisfacer al cliente entregando software de valor de forma continua y temprana | No esperes al final para mostrar; entrega valor incremental |
| 2 | Bienvenidos los cambios en los requisitos, incluso en etapas tardías | El cambio no es el enemigo; la incapacidad de adaptarse sí |
| 3 | Entregar software funcionando con frecuencia (semanas, no meses) | Ciclos cortos = feedback rápido = menos riesgo |

### Bloque B — Colaboración

| # | Principio | Clave práctica |
|---|---|---|
| 4 | Negocio y desarrolladores deben trabajar juntos diariamente | No el cliente "al inicio" y "al final"; durante todo el proceso |
| 5 | Construir proyectos con personas motivadas, darles el entorno y la confianza | Los equipos necesitan autonomía, no microgestión |
| 6 | La comunicación más eficiente es cara a cara (o su equivalente) | Una llamada supera a 20 mensajes de texto |

### Bloque C — Excelencia técnica y diseño

| # | Principio | Clave práctica |
|---|---|---|
| 7 | Software funcionando es la medida principal de progreso | No "tareas completadas" ni "horas trabajadas" |
| 8 | Agile promueve el desarrollo sostenible (ritmo constante indefinidamente) | El sprint eterno de 80h/semana destruye equipos y calidad |
| 9 | Atención continua a la excelencia técnica y el buen diseño | La deuda técnica (*technical debt*: atajos que cuestan más después) mata la agilidad |

> **Deuda técnica** (jerga importante): cuando escribes código rápido pero "sucio" para entregar antes, acumulas "deuda". Como deuda financiera, tiene intereses: cada cambio futuro cuesta más. Agile no ignora esto; lo gestiona activamente.

### Bloque D — Reflexión y mejora

| # | Principio | Clave práctica |
|---|---|---|
| 10 | Simplicidad: maximizar el trabajo que NO se hace | No sobre-construyas; construye lo mínimo que resuelve el problema (YAGNI: *You Aren't Gonna Need It*) |
| 11 | Las mejores arquitecturas, requisitos y diseños emergen de equipos auto-organizados | El equipo que hace el trabajo sabe cómo hacerlo mejor que un gerente externo |
| 12 | El equipo reflexiona regularmente sobre cómo ser más efectivo y ajusta su comportamiento | Las **retrospectivas** (retros) son el mecanismo de mejora continua |

---

## Mentalidad Agil vs. ejecutar rituales

Esta es la distinción más importante y la que más se malentiende en la industria.

### El error común: "Hacemos Agile"

Muchos equipos hacen las ceremonias de Scrum o Kanban y creen que "son ágiles":
- Daily standup de 30 minutos donde cada uno recita lo que hizo
- Sprint planning donde el manager decide qué va en el sprint
- Retrospectiva donde nadie dice nada importante porque no hay seguridad psicológica
- Backlog de 300 items que nadie ha revisado en 6 meses

Esto se llama **Cargo Cult Agile**: copiar la forma externa sin entender el propósito.

### La mentalidad es el núcleo

| Ritual sin mentalidad | Mentalidad Agil |
|---|---|
| Daily para reportar al manager | Daily para sincronizar y desbloquear entre iguales |
| Backlog para controlar qué hace el equipo | Backlog para capturar y priorizar valor pendiente |
| Sprint para entregar todo lo planeado | Sprint para aprender qué funciona y ajustar |
| Retro como ritual vacío | Retro como mecanismo real de mejora del equipo |
| Cambio de requisitos = problema | Cambio de requisitos = nueva información valiosa |

> **Test rápido de mentalidad**: cuando llega un cambio de requisitos a mitad de iteración, ¿la reacción es "no puede ser, ya lo planificamos" o "veamos qué aprendimos y cómo lo incorporamos"? La primera es ritual; la segunda es mentalidad.

---

## [NO] Qué NO es ser Agil

Estos malentendidos son extremadamente comunes, especialmente viniendo de formación más estructurada (ingeniería clásica, hardware):

| Mito | Realidad |
|---|---|
| Agile = sin planificar | Agile planifica continuamente, en horizontes más cortos y con más información |
| Agile = sin documentación | Agile documenta lo necesario, en el momento necesario; evita documentación que envejece sin usarse |
| Agile = sin arquitectura | La arquitectura emerge y evoluciona; no desaparece. Los principios de diseño importan más que nunca |
| Agile = sprints eternos de velocidad máxima | El principio 8 dice explícitamente: ritmo sostenible. El burn-out no es agile |
| Agile = el manager decide todo en las ceremonias | Los equipos se auto-organizan; las ceremonias son del equipo, no del manager |
| Agile solo funciona en software | Los valores aplican a cualquier trabajo del conocimiento; pero el Manifiesto se escribió para software |

---

## Errores comunes al adoptar Agile

1. **Confundir velocidad (velocity) con progreso real**: el equipo "completa muchos puntos" pero no entrega valor al usuario.
2. **El cliente desaparece después del kick-off**: se contrata Agile pero el cliente solo aparece al final. Rompe el valor 3.
3. **No hay retrospectivas reales**: se hace la retro pero nadie actúa sobre los puntos de mejora. El equipo deja de creer en el proceso.
4. **La deuda técnica se ignora**: se acelera siempre, nunca se paga deuda. En 6 meses, cada cambio tarda el doble.
5. **El "Agile Coach" como policía de rituales**: alguien que verifica que se hacen las ceremonias pero no trabaja en la mentalidad ni la cultura.

---

## Aplícalo a tus proyectos

### app web (React + FastAPI + Docker)
- **Valor 2 en práctica**: en lugar de documentar todos los endpoints antes de escribir, define el contrato mínimo (OpenAPI schema básico) e itera. Documenta las decisiones de arquitectura que SÍ importan (por qué MongoDB para alimentos, por qué Redis para caché).
- **Principio 10 (YAGNI)**: ¿Necesitas el módulo de recetas en la v1? ¿O primero validas que el usuario registra lo que come? Construye lo mínimo viable primero.
- **Principio 3 (entregas frecuentes)**: aunque trabajes solo, establece ciclos de 1-2 semanas donde puedas "demostrar" (aunque sea a ti mismo o a un beta tester) algo funcionando. Evita el modo "desarrollo en oscuridad" de meses sin validar.
- **Principio 12 (retro personal)**: al final de cada ciclo, 15 minutos: ¿qué funcionó? ¿qué me bloqueó? ¿qué cambio en el siguiente ciclo?

### proyecto embebido (PlatformIO / Embedded)
- **Valor 4 (responder al cambio)**: en hardware es más costoso cambiar tarde, pero el principio aplica igual. Si a mitad del diseño del PCB descubres que un componente no encaja, el Manifiesto Agil diría: acepta la nueva información y ajusta, no fuerces el plan original.
- **Valor 1 (individuos sobre procesos)**: si trabajas con otros en el proyecto, la comunicación directa supera al issue tracker. Pero el issue tracker ayuda cuando no estáis coordinados en tiempo real.

### Proyectos de aprendizaje en general
- **Principio 10 (simplicidad)**: cuando aprendas un nuevo concepto, construye el ejemplo mínimo que lo demuestre. No construyas el sistema completo para probar una idea.
- **Principio 12 (reflexión)**: la retro personal al final de un módulo de estudio es una herramienta de aprendizaje, no solo de proceso de equipo.

---

## Conexiones

- [[MOC_Desarrollo_Software]]
- [[01-sdlc-e-historia]]
- [[03-scrum]]
- [[04-kanban-y-lean]]
- [[05-historias-de-usuario-y-backlog]]
- [[06-otros-marcos]]
- [[11-equipo-retros-y-antipatrones]]
