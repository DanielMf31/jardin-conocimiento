---
title: Prácticas de Ingeniería de Software
date: 2026-06-13
tags: [programacion/agile, programacion/git, programacion/testing, programacion/clean-code, programacion/devex]
type: nota
status: en-progreso
source: claude-code
aliases: [practicas ingenieria, engineering practices, xp practices]
---

# Prácticas de Ingeniería de Software

> Las metodologías (Scrum, Kanban) dicen *qué* hacer y *cuándo*. Las prácticas de ingeniería dicen *cómo* hacerlo bien. Son el nivel técnico que convierte un proceso ágil en software que no colapsa.

Sin buenas prácticas de ingeniería, un equipo ágil solo falla más rápido con más reuniones.

---

## 1. Control de Versiones y Workflows de Git

### El problema que resuelve

Múltiples personas modificando el mismo código simultáneamente. Sin sistema: se sobreescriben cambios, no hay historial, no se puede revertir a un estado bueno. Git resuelve esto con un grafo de snapshots (commits) que permite trabajar en paralelo y fusionar después.

**Conceptos clave de Git** (si vienen de hardware: piensa en branching como bifurcaciones de diseño en un esquemático — cada rama es una versión alternativa que luego se fusiona):

| Término | Qué es |
|---|---|
| **commit** | Snapshot del estado del código en un momento |
| **branch** | Puntero a un commit; línea de desarrollo independiente |
| **merge** | Fusionar dos branches en una |
| **rebase** | Reescribir el historial de commits sobre otra base |
| **PR / MR** | Pull Request / Merge Request — propuesta formal de fusionar una branch |

Para profundizar en el modelo interno de Git: [[git-por-dentro]].

---

### Los tres workflows principales

#### Gitflow

**Cuándo nació:** 2010 (Vincent Driessen). Pensado para software con versiones discretas y releases planificados (librerías, apps de escritorio, firmware).

```
main ──────────────────────────────────────────────────► (producción)
         ↑                    ↑
develop ─────────────────────────────────────────────► (integración)
         ↑          ↑
feature/A ──────────┤   feature/B ──────────┤
                  merge                   merge
```

**Ramas principales:**
- `main` — solo código en producción, nunca se toca directamente
- `develop` — integración continua de features

**Ramas temporales:**
- `feature/*` — una por funcionalidad, nace de `develop`
- `release/*` — preparar una versión (solo bugfixes), nace de `develop`, muere en `main` + `develop`
- `hotfix/*` — arreglos urgentes en producción, nace de `main`, muere en `main` + `develop`

**Ventajas:** historial muy explícito, soporte de múltiples versiones en paralelo.

**Desventajas:** burocrático para equipos pequeños o servicios web con deploy continuo. Las branches viven demasiado tiempo → conflictos enormes al fusionar.

---

#### GitHub Flow

**Cuándo usarlo:** servicios web que se despliegan frecuentemente (SaaS, APIs). El más sencillo.

```
main ──────────────────────────────────────────────────► (producción)
         ↑          ↑          ↑
feature-A ──────────┤          │
              PR+merge         │
                   feature-B ──┤
                         PR+merge
```

**Reglas:**
1. `main` siempre está deployable
2. Cualquier cambio va en una branch descriptiva (`fix/login-bug`, `feat/user-auth`)
3. Se abre un PR en cuanto quieras feedback, aunque no esté terminado
4. Merge solo tras code review y CI verde
5. Se deploya inmediatamente al hacer merge a `main`

**Es el workflow más adecuado para tus proyectos personales con CI/CD.**

---

#### Trunk-Based Development (TBD)

**Filosofía:** todos los desarrolladores hacen commit directamente a `main` (trunk) varias veces al día. Las branches, si existen, duran menos de un día.

**¿Cómo se evita romper producción?** Con *feature flags* (interruptores en código que activan/desactivan funcionalidades sin redeploy) y una suite de tests robustísima.

```
main ────commit────commit────commit────commit────► (siempre verde)
              ↑ dev A    ↑ dev B   ↑ dev A
```

**Cuándo usarlo:** equipos maduros con CI/CD muy rápido y alta cobertura de tests. Google, Facebook lo usan internamente.

**Cuándo NO:** si no tienes tests robustos o el equipo no tiene disciplina suficiente. Es fácil romper todo.

---

### Comparativa rápida

| | Gitflow | GitHub Flow | Trunk-Based |
|---|---|---|---|
| **Complejidad** | Alta | Baja | Media (requiere feature flags) |
| **Ideal para** | Versiones discretas, firmware | SaaS/APIs, equipos pequeños | Equipos grandes, CI/CD maduro |
| **Frecuencia de deploy** | Release-based | Continua | Continua (varias al día) |
| **Riesgo de conflictos** | Alto (branches largas) | Medio | Bajo |
| **Overhead** | Alto | Mínimo | Mínimo |

**Recomendación para proyectos personales:** GitHub Flow. Simple, directo, compatible con CI/CD en GitHub Actions.

---

## 2. Pull Requests y Code Review

### Por qué el code review importa

No es solo "encontrar bugs". Es:
1. **Difundir conocimiento** — el revisor aprende cómo funciona esa parte del código
2. **Coherencia** — mantener un estilo y arquitectura uniforme
3. **Capturar errores lógicos** — los tests no atrapan todo
4. **Documentación viva** — los comentarios de PR quedan como historial de decisiones

### Qué mirar en un code review

**Nivel 1 — Correctitud:**
- ¿El código hace lo que dice que hace?
- ¿Hay casos borde no cubiertos (null, lista vacía, concurrencia)?
- ¿Los tests existen y son significativos?

**Nivel 2 — Diseño:**
- ¿La abstracción elegida tiene sentido? ¿Está en el nivel correcto?
- ¿Se viola el principio de responsabilidad única (una función/clase, una razón para cambiar)?
- ¿Hay duplicación que debería extraerse?

**Nivel 3 — Mantenibilidad:**
- ¿Un nuevo desarrollador entendería esto en 6 meses?
- ¿Los nombres de variables/funciones son descriptivos?
- ¿Hay comentarios donde el *por qué* no es obvio?

**Nivel 4 — Seguridad y rendimiento** (solo cuando aplica):
- ¿Hay inputs sin validar? ¿SQL/comandos construidos con strings?
- ¿Hay N+1 queries (loop que lanza una query por iteración)?

### Buenas prácticas del revisor

- **Distingue bloqueantes de sugerencias.** `[bloqueante]` vs `[nit]` (nitpick: mejora menor, no bloquea merge).
- **Explica el por qué**, no solo el qué cambiar: "sugiero renombrar a `user_id` porque en el resto del codebase usamos snake_case para IDs".
- **Revisa en máximo 400-500 líneas por sesión.** La efectividad de detectar bugs cae drásticamente después.
- **Aprueba aunque haya nits pendientes** si no son bloqueantes. No bloquees por estilo cuando existe un linter.

### Buenas prácticas del autor

- **PRs pequeños.** Una sola cosa. Si tienes que escribir más de 3 párrafos de descripción, probablemente son dos PRs.
- **Describe el *por qué***, no el *qué* (el diff ya muestra el qué). "Extraigo esta función para poder testearla en aislamiento" es útil; "añado función helper" no.
- **Añade capturas/GIFs** para cambios de UI.
- **Marca como WIP/Draft** si quieres feedback temprano antes de terminar.

---

## 3. Testing

### El problema que resuelve

Sin tests, cada cambio podría romper algo existente sin que te enteres hasta que el usuario lo reporta. Con tests, tienes una red de seguridad que te permite refactorizar y añadir features con confianza.

### La Pirámide de Tests

Metáfora clásica de Mike Cohn. La forma importa: más tests rápidos y baratos abajo, menos lentos y caros arriba.

```
          /\
         /E2E\         ← Pocos. Lentos. Costosos. Prueban flujos completos.
        /------\
       /Integrac.\     ← Moderados. Prueban que módulos se conectan bien.
      /------------\
     /  Unit Tests  \  ← Muchos. Rápidos. Prueban una unidad en aislamiento.
    /________________\
```

**Si la pirámide se invierte** (más E2E que unit) tienes el "cono de helado": suite lenta, frágil, difícil de debuggear. Error común en proyectos sin cultura de testing.

---

### Tipos de tests en detalle

#### Tests unitarios (Unit Tests)

Prueban **una sola unidad de código** (función, clase, método) en total aislamiento. Cualquier dependencia externa (DB, red, sistema de archivos) se reemplaza con *mocks* o *stubs* (objetos falsos que simulan el comportamiento).

```python
# Ejemplo: función pura, fácil de testear
def calcular_imc(peso_kg: float, altura_m: float) -> float:
    return peso_kg / (altura_m ** 2)

def test_imc_normal():
    resultado = calcular_imc(70, 1.75)
    assert abs(resultado - 22.86) < 0.01
```

**Cuándo son suficientes:** lógica de negocio pura, algoritmos, transformaciones de datos.

**Cuándo no bastan:** integración con DB real, comportamiento de red, interacciones de UI.

---

#### Tests de integración (Integration Tests)

Prueban que **dos o más módulos funcionan juntos correctamente**. Pueden involucrar DB real (en contenedor), servicios externos mockeados, o múltiples capas de la aplicación.

```python
# Ejemplo con FastAPI + DB de test
def test_crear_usuario(client, db_test):
    response = client.post("/users/", json={"email": "a@b.com"})
    assert response.status_code == 201
    assert db_test.query(User).count() == 1
```

**Son más lentos** porque levantan infraestructura real o semi-real. Suelen requerir setup/teardown (preparar y limpiar el entorno antes/después de cada test).

---

#### Tests End-to-End (E2E)

Prueban **el sistema completo desde la perspectiva del usuario**, simulando acciones reales en el navegador o cliente. Herramientas: Playwright, Cypress, Selenium.

```python
# Playwright — automatiza un navegador real
def test_login_flujo_completo(page):
    page.goto("http://localhost:3000/login")
    page.fill("#email", "user@example.com")
    page.fill("#password", "secret")
    page.click("button[type=submit]")
    expect(page).to_have_url("/dashboard")
```

**Son los más lentos y frágiles** (cualquier cambio de CSS puede romperlos). Úsalos solo para los *happy paths* críticos del negocio.

---

### TDD — Test-Driven Development

**Qué es:** escribir el test *antes* del código que lo hace pasar. Ciclo: Red → Green → Refactor.

```
1. Red    → Escribe un test que falla (la feature no existe aún)
2. Green  → Escribe el mínimo código para que el test pase
3. Refactor → Limpia el código manteniendo los tests en verde
```

**Por qué funciona:** te fuerza a pensar en la API pública de tu código antes de implementarla. Resultado: interfaces más limpias, código más testeable por diseño.

**Cuándo NO aplicarlo literalmente:**
- Prototipos o exploración de diseño (el diseño cambia demasiado rápido)
- Tests E2E (el ciclo es demasiado lento)
- Código de infraestructura muy acoplado al entorno

---

### BDD — Behaviour-Driven Development

**Qué es:** extensión de TDD donde los tests se escriben en lenguaje casi-natural comprensible por no-técnicos (PMs, QA, cliente). Formato **Given/When/Then**.

```gherkin
Feature: Login de usuario

  Scenario: Login con credenciales válidas
    Given que el usuario "ana@test.com" existe en el sistema
    When envío POST /login con email "ana@test.com" y password "1234"
    Then la respuesta tiene status 200
    And el body contiene un token JWT
```

**Herramientas:** Cucumber, Behave (Python), pytest-bdd.

**Cuándo aporta valor real:** cuando hay colaboración intensa con stakeholders no técnicos que necesitan entender los tests. Para proyectos personales o equipos técnicos puros, el overhead de Gherkin rara vez compensa.

---

### Cobertura de tests (coverage)

Métrica que indica qué porcentaje de líneas/ramas de código son ejecutadas por los tests. **No es un objetivo en sí misma:**

- 100% coverage no significa ausencia de bugs (puedes ejecutar código sin hacer assertions útiles)
- 70-80% suele ser el punto de retorno decreciente para la mayoría de proyectos

Úsala como herramienta para encontrar zonas no testeadas, no como KPI.

---

## 4. Clean Code, Refactoring y Deuda Técnica

### Clean Code — qué es y qué no es

**No es** código perfectamente formateado con comentarios en cada línea. Es código que **comunica su intención claramente** a quien lo lee después (incluido tú mismo en 6 meses).

Principios clave:

| Principio | Qué significa en la práctica |
|---|---|
| **Nombres descriptivos** | `calcular_dosis_diaria()` no `calc()`. Variables: `usuario_activo` no `u` |
| **Funciones pequeñas** | Una función hace una cosa. Si necesita "y" en el nombre, probablemente son dos funciones |
| **Sin comentarios redundantes** | `i += 1  # incrementa i en 1` no aporta. Comenta el *por qué*, no el *qué* |
| **Evitar efectos secundarios ocultos** | `obtener_usuario()` no debería también actualizar un log silenciosamente |
| **DRY (Don't Repeat Yourself)** | Si copias y pegas código, extrae una función o clase |
| **YAGNI (You Aren't Gonna Need It)** | No implementes funcionalidades "por si acaso". Implementa lo que necesitas ahora |

---

### Refactoring

**Definición precisa:** cambiar la estructura interna del código sin cambiar su comportamiento externo observable. El comportamiento antes y después es idéntico; solo mejora el diseño interno.

**No es refactoring:** cambiar funcionalidad al mismo tiempo que reestructuras. Eso es peligroso sin tests.

**Cuándo refactorizar:**
- Antes de añadir una feature (haz el código más fácil de modificar primero)
- Después de que los tests pasen en TDD (paso "Refactor" del ciclo)
- Cuando tocas código que ya huele mal (*code smells*)

**Code smells comunes** (señales de que algo necesita refactoring):

| Smell | Señal | Solución típica |
|---|---|---|
| **Función larga** | >20-30 líneas | Extraer funciones |
| **Clase grande (God Object)** | Hace demasiadas cosas | Dividir en clases con responsabilidad única |
| **Duplicación** | Mismo bloque en dos sitios | Extraer y parametrizar |
| **Parámetros en exceso** | Función con >3-4 params | Agrupar en objeto/dataclass |
| **Comentarios que explican código confuso** | El comentario existe porque el código no se entiende solo | Renombrar/restructurar hasta que el código sea autoexplicativo |
| **Feature Envy** | Una función usa más datos de otra clase que de la propia | Mover la función a la clase que usa |

---

### Deuda Técnica

**Metáfora** (Ward Cunningham, creador de la wiki): tomar atajos en el diseño del código es como tomar deuda financiera. Vas más rápido ahora, pero pagas *intereses* continuamente (cada cambio futuro cuesta más) hasta que *amortizas* la deuda (refactorizas).

**Tipos de deuda técnica:**

```
                    DELIBERADA           INADVERTIDA
                 ┌─────────────────┬──────────────────┐
   IMPRUDENTE    │ "No tenemos     │ "¿Qué son las    │
                 │ tiempo para     │ capas de         │
                 │ diseñarlo bien" │ abstracción?"    │
                 ├─────────────────┼──────────────────┤
   PRUDENTE      │ "Sabemos que    │ "Ahora entendemos│
                 │ es temporal,    │ que deberíamos   │
                 │ lo anotamos"    │ haberlo hecho    │
                 │                 │ diferente"       │
                 └─────────────────┴──────────────────┘
```

La deuda **deliberada y prudente** es legítima: tomas un atajo consciente, lo documentas, y lo pagas después. La imprudente e inadvertida es la que destruye proyectos.

**Cómo gestionarla:**
1. **Haznla visible**: registra en el backlog los items de deuda con una etiqueta `tech-debt`. Lo invisible no se paga.
2. **La regla del Boy Scout**: "deja el código un poco más limpio de como lo encontraste". Mejoras incrementales en cada PR.
3. **Budget de refactoring**: reserva un porcentaje del sprint (20% es común) para deuda técnica. Si no lo haces explícito, siempre pierde frente a las features.
4. **No refactorices sin tests**: es el mayor error. Sin net de seguridad, refactorizar introduce bugs.

---

## Cuándo usar / cuándo NO

| Práctica | Úsala cuando... | Evítala / adapta cuando... |
|---|---|---|
| **Gitflow** | Software con versiones numeradas, firmware, librerías | Servicios web con deploy continuo |
| **GitHub Flow** | API REST, apps web, proyectos personales | Múltiples versiones en producción simultáneas |
| **TDD estricto** | Lógica de negocio compleja, librería pública | Prototipado rápido, E2E tests |
| **BDD/Gherkin** | Colaboración intensa con stakeholders no técnicos | Equipo 100% técnico, proyectos personales |
| **Refactoring agresivo** | Código con buena cobertura de tests | Sin tests — mejor añadir tests primero |

---

## Errores comunes

- **"Refactorizo y añado features a la vez"** — mezclar los dos hace que si algo falla no sabes qué lo causó.
- **"El código es autoexplicativo, no necesito tests"** — los tests no documentan el código, documentan el *comportamiento esperado*. Son cosas distintas.
- **"Coverage al 100% como objetivo"** — leads a tests que no assercionan nada útil solo para subir el número.
- **"Hago el PR gigante para no interrumpir el flujo"** — los PRs grandes no se revisan bien. La revisión real ocurre en PRs de <300 líneas.
- **"La deuda técnica la pagamos cuando tengamos tiempo"** — ese tiempo nunca llega sin reservarlo explícitamente.
- **"Trunk-based sin feature flags ni tests"** — es romper producción sistemáticamente.

---

## Aplícalo a tus proyectos

### app web (React + FastAPI + MongoDB + Redis)

- **Workflow:** GitHub Flow es el natural. Una branch por feature/fix, PR a `main`, CI verde antes de merge.
- **Testing backend:** pirámide clásica — muchos tests unitarios para la lógica de cálculo del producto (macros, porciones), tests de integración con MongoDB en contenedor Docker para los repositorios, pocos E2E para los flujos críticos (login → registrar comida → ver resumen).
- **Testing frontend:** tests de componentes con Vitest + React Testing Library para componentes de formulario; E2E con Playwright para el flujo completo.
- **Deuda técnica:** cuando hagas el scaffolding rápido para tener algo funcionando, añade las tareas de refactor al backlog con etiqueta `tech-debt` desde el principio.

### proyecto embebido (PlatformIO / firmware)

- **Workflow:** Gitflow tiene más sentido aquí — el firmware tiene versiones discretas que se flashean. `develop` para integración, `release/v1.x` para preparar una versión estable.
- **Testing:** para firmware, considera tests de lógica pura en host (sin hardware) con CMock/Unity o pytest + simuladores. Los tests de integración en hardware real son costosos — minimízalos.
- **Clean code en C/C++:** el coste de los code smells es mayor que en Python porque el compilador no te protege de muchas cosas. Nombres de funciones descriptivos y funciones pequeñas son especialmente críticos.

### Proyectos de aprendizaje / Build Things

- **TDD es ideal aquí** — no hay presión de deadline, y practicar el ciclo Red-Green-Refactor construye el hábito para cuando haya presión real.
- **Code review solo:** revisa tu propio código 24h después de escribirlo. Sorprende lo que encuentras con distancia temporal.

---

## Conexiones

- [[MOC_Desarrollo_Software]]
- [[01-sdlc-e-historia]]
- [[02-manifiesto-agil]]
- [[03-scrum]]
- [[08-devops-y-cicd]]
- [[09-metricas-y-seguimiento]]
- [[11-equipo-retros-y-antipatrones]]
- [[git-por-dentro]]
