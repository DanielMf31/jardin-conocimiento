# 01 — Lexer, parser, AST

> 📚 **Doc 1 del cluster Compilers (Tier 3 opcional)**. Cómo cualquier lenguaje de programación entiende tu código. La frontera entre "texto que escribes" y "instrucciones que la CPU ejecuta".
> 🎓 **Para quién**: opcional para grandes tecnologicas SWE típico, útil para roles compilers/lenguajes/DSLs/parsing tools.
> ⏱️ **Tiempo de lectura estimado**: 35-50 min.

---

## 1. Por qué entender compilers (aunque no escribas uno)

A primera vista esto es muy académico. Pero los conceptos aparecen en lugares prácticos:

- **JSON / YAML / TOML parsers**: lexer + parser + AST.
- **SQL queries**: tu DB tiene un lexer, parser, planner.
- **Regex engines**: lexer + parser + automaton.
- **Templating engines** (Jinja, Handlebars): mini-compiler.
- **Linters y formatters** (ruff, prettier): trabajan sobre AST.
- **DSLs custom** (config files, query languages): tienes que parsearlos.
- **GraphQL**: query language complete con compiler.

Saber el modelo mental de "código → tokens → AST → ejecución" te ayuda a entender herramientas, debuggear DSLs custom, y construir tools propias.

---

## 2. Las fases clásicas de un compiler

Un compiler clásico tiene varias fases que transforman tu código fuente:

1. **Lexer (scanner)**: divide el código en **tokens** (palabras significativas).
2. **Parser**: combina tokens en una **estructura jerárquica** (AST).
3. **Semantic analyzer**: verifica reglas (tipos, scoping, etc.).
4. **IR generator**: traduce AST a **representación intermedia** (más fácil de optimizar).
5. **Optimizer**: transforma IR para que sea más eficiente.
6. **Code generator**: emite código máquina o bytecode.

Este doc cubre las fases 1-3. La 4-6 son del doc siguiente.

---

## 3. Lexer (lexical analysis / scanning / tokenization)

El **lexer** lee el código fuente como un stream de caracteres y produce un stream de **tokens**. Cada token es una unidad significativa: identificador, número, operador, keyword, etc.

### Ejemplo

Código fuente:
```python
x = 2 + 3 * 4
```

Tokens producidos:
```
IDENT("x")
ASSIGN("=")
INT(2)
PLUS("+")
INT(3)
STAR("*")
INT(4)
NEWLINE
```

El lexer no entiende **estructura** (no sabe que `*` tiene mayor precedencia que `+`). Solo identifica las palabras.

### Cómo se implementa

Lexer típicamente es un **state machine**:

1. Inicia en estado "start".
2. Lee carácter. Según carácter, transiciona a estado.
3. Acumula caracteres hasta completar token.
4. Emite token. Vuelve a "start".

Para tokens complejos (literales de string con escapes, números con notación científica, comentarios anidados) la state machine puede ser sofisticada.

### Lexer generators

Para no escribir lexers a mano, hay **generators** que toman regex y producen el código del lexer:
- **lex / flex** (C clásico).
- **ANTLR** (Java/multi-lenguaje).
- **rply** (Python, RPython).

En la práctica, lexers a mano son comunes porque son simples y dan más control. ~200 líneas para un lexer de un lenguaje pequeño.

### Decisiones del lexer

El lexer toma decisiones que parecen triviales pero importan:

- **Whitespace significativo o no**: en Python sí (indentación). En la mayoría de lenguajes no (whitespace solo separa tokens).
- **Comentarios**: descartados, no son tokens.
- **Keywords vs identifiers**: ambas matchean `[a-zA-Z_][a-zA-Z0-9_]*`. El lexer mira tabla de keywords para distinguir.
- **String literals**: manejar escapes (`\n`, `\"`).
- **Números**: ¿soportas `0x1F` hex? `1_000_000` con underscores? `1.5e10` científica?

---

## 4. Parser (syntactic analysis)

El **parser** toma el stream de tokens del lexer y produce una **estructura jerárquica** que captura la gramática del lenguaje.

Esa estructura suele ser un **AST (Abstract Syntax Tree)**.

### Ejemplo

Tokens: `x = 2 + 3 * 4`.

AST resultante:

```
Assign
├── target: Identifier("x")
└── value: BinaryOp("+")
    ├── left: Integer(2)
    └── right: BinaryOp("*")
        ├── left: Integer(3)
        └── right: Integer(4)
```

Notar que la estructura captura **precedencia**: `*` está más profundo que `+`, así que se evalúa primero.

### Gramáticas formales

Los parsers se construyen sobre una **gramática formal** (BNF, EBNF, PEG).

Ejemplo gramática simplificada para expresiones aritméticas:

```
expression  := term ('+' term | '-' term)*
term        := factor ('*' factor | '/' factor)*
factor      := number | '(' expression ')'
number      := [0-9]+
```

La estructura jerárquica de la gramática **directamente codifica precedencia**: `expression` contiene `term`, `term` contiene `factor`. Por eso `*` (en term) ata más fuerte que `+` (en expression).

### Tipos de parsers

**Recursive descent (top-down, hand-written)**: cada regla de gramática es una función Python que llama a otras. Simple y elegante para gramáticas pequeñas.

```python
def parse_expression():
    left = parse_term()
    while peek() in ['+', '-']:
        op = consume()
        right = parse_term()
        left = BinaryOp(op, left, right)
    return left

def parse_term():
    left = parse_factor()
    while peek() in ['*', '/']:
        op = consume()
        right = parse_factor()
        left = BinaryOp(op, left, right)
    return left
```

**LL(k), LR(k), LALR**: parsers más sofisticados generados por tools (yacc/bison, ANTLR). Pueden manejar gramáticas más complejas pero el código es opaco.

**PEG (Parsing Expression Grammars)**: alternativa moderna. Python desde 3.9 usa parser PEG (reemplazando el LL(1) histórico). Permite gramáticas más expresivas.

**Pratt parsers**: técnica elegante para parsing de expresiones con precedencia. Cada token tiene "binding power" left/right.

### El problema clásico — precedencia y asociatividad

`2 + 3 * 4` puede parsearse como `(2 + 3) * 4 = 20` o `2 + (3 * 4) = 14`. La gramática + parser deben elegir.

**Precedencia**: `*` ata más que `+`. Solucionado por jerarquía de gramática (factor más profundo que term).

**Asociatividad**: `2 - 3 - 4` puede ser `(2 - 3) - 4 = -5` (left-associative) o `2 - (3 - 4) = 3` (right-associative). Lo decide la gramática.

Para operaciones aritméticas estándar: left-associative para `-`, `/`, right-associative para `**` (exponentiation).

---

## 5. AST (Abstract Syntax Tree)

El **AST** es la estructura jerárquica producida por el parser. **Abstract** porque omite detalles sintácticos triviales (paréntesis, comas, semicolons) y captura solo la **estructura semántica**.

Cada nodo del AST representa una construcción del lenguaje: assignment, binary op, function call, etc.

### Por qué AST y no parse tree

**Parse tree** (concrete syntax tree): captura toda la sintaxis, incluso paréntesis y delimitadores.

**AST**: captura solo lo que importa para semántica. Más limpio y útil para fases siguientes.

Ejemplo: `(2 + 3)` y `2 + 3` producen el mismo AST `BinaryOp(+, 2, 3)`. Los paréntesis del parse tree desaparecen porque no añaden info semántica.

### Operaciones sobre AST

Una vez tienes el AST, puedes hacer mucho:

- **Walking** (visitor pattern): recorrer el árbol para ejecutar, transformar, analizar.
- **Transformation**: optimizaciones (constant folding: `2 + 3` → `5`).
- **Pretty-printing**: convertir AST de vuelta a texto (formatters).
- **Type checking**: anotar tipos.
- **Code generation**: emitir bytecode/asm.

En Python, `ast` module te da el AST de cualquier código:

```python
import ast
tree = ast.parse("x = 2 + 3 * 4")
print(ast.dump(tree, indent=2))
```

Output:
```
Module(
  body=[
    Assign(
      targets=[Name(id='x')],
      value=BinOp(
        left=Constant(value=2),
        op=Add(),
        right=BinOp(
          left=Constant(value=3),
          op=Mult(),
          right=Constant(value=4)))])])
```

Tools como `ruff`, `black`, `mypy` operan sobre este AST.

---

## 6. Semantic analysis

Después de parsing, el AST puede ser **sintácticamente válido pero semánticamente incorrecto**. Por ejemplo:

```python
x = y + 1   # error: y no está definido
```

El parser no detecta esto (la sintaxis es válida). La **semantic analysis** lo detecta.

### Cosas típicas en semantic analysis

- **Symbol table**: tracking de qué identificadores están definidos en cada scope.
- **Scoping rules**: variable nueva, shadowing, closure capture.
- **Type checking**: ¿`"hello" + 5` es error o tiene sentido (Python str + int es error, JS lo permite)?
- **Resolución de imports**: encontrar dependencies.
- **Const folding básico**: `2 + 3` puede reducirse a `5` aquí.

Para lenguajes **estáticamente tipados** (Java, Rust, TypeScript), type checking es masivo y complejo. Para **dinámicamente tipados** (Python, JS), mucho de esto se difiere a runtime.

---

## 7. Errores y diagnósticos

Buenos compilers no solo detectan errores — los **comunican bien al programador**.

### Error de compilers viejos vs modernos

```
gcc clásico:
  test.c:5: error: expected ';' before '}' token

Rust moderno:
  error: expected `;`, found `}`
   --> src/main.rs:5:18
    |
  4 |     let x = 5
    |              - expected `;` here
  5 | }
    | ^ unexpected token
```

Rust te muestra el contexto, sugiere el fix, usa color. Esto requiere mucho trabajo pero **mejora drásticamente la experiencia developer**.

Tools modernos (TypeScript, Rust, Elm) son ejemplares en mensajes de error. Hay todo un sub-campo de research en "diagnostic quality".

---

## 8. Aplicación al perfil del usuario

### Construir un calculadora — proyecto sugerido

Si te interesa profundizar, construye un evaluador de expresiones aritméticas. ~300 líneas Python:

1. Lexer (tokenize "2 + 3 * 4").
2. Parser (recursive descent → AST).
3. Evaluator (visitor pattern sobre AST).

Esto te da el modelo mental completo. Después puedes extender: variables, funciones, condicionales, bucles → tienes un mini-lenguaje.

### Para tu Phone Book FastAPI

Cuando uses FastAPI, Pydantic está parsing JSON → tu modelo. Internamente: lexer + parser. Saber esto te ayuda cuando JSON viene mal formateado y debugeas el error.

### En entrevistas tecnicas

Compilers raramente sale en interviews SWE típicos. Sale en:
- Roles de compiler engineer (LLVM, V8, Rustc) — críticos.
- Roles de DevX/tooling.
- Preguntas tipo "diseña un parser de queries" en system design.

**Pregunta común**: "Diseña un calculator que evalúa expresiones tipo `2 + 3 * (4 - 1)`".

Tu respuesta: lexer (tokenize) + parser (recursive descent que respeta precedencia via gramática jerárquica) + evaluator (visitor sobre AST).

---

## 9. Trampas típicas

**"Lexer y parser son lo mismo"**: NO. Lexer tokeniza. Parser estructura. Pueden estar en mismo proceso pero conceptualmente distintos.

**"Regex puede parsear cualquier cosa"**: NO. Regex es regular grammar (potencia limitada). Lenguajes de programación necesitan context-free grammars o más. Por eso lexer regex pero parser no.

**"AST y parse tree son sinónimos"**: AST es abstracta (sin trivia). Parse tree es concreta. Diferentes tools usan distintos.

**"Parser generators son siempre mejores"**: para gramáticas complejas sí. Para parsers pequeños, recursive descent a mano es más simple y comprensible.

**"Buenos errores son fáciles"**: NO. Errores claros con sugerencias requieren mucho trabajo. Es por qué Rust se diferencia.

**"Compilers son magia"**: son solo state machines + transformaciones de árboles. Conceptualmente accesibles. Lo difícil es manejar todos los edge cases del lenguaje.

---

## 10. Preguntas típicas de interview

**Diferencia compiler vs interpreter**: compiler traduce todo el código a target (típicamente código máquina) ANTES de ejecutar. Interpreter ejecuta directamente. Híbridos (Python compila a bytecode + interpreta) son comunes.

**AST**: representación jerárquica del código. Estructura semántica. Nodos para cada construcción.

**Cómo se maneja precedencia en parser**: gramática jerárquica donde reglas más profundas tienen mayor precedencia.

**Recursive descent vs parser generator**: simple a mano vs robusto para gramáticas grandes.

**Lexer en regex vs parser en otra cosa**: lexer puede usar regex (regular grammar). Parser necesita más potencia (context-free).

---

## 11. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Las fases típicas de un compiler.
- Lexer: stream char → stream token. State machine.
- Parser: tokens → AST. Recursive descent o generator.
- AST vs parse tree.
- Cómo gramática captura precedencia jerárquicamente.
- Semantic analysis (symbol table, type check, scoping).
- Por qué errores diagnostics importa.

Si no puedes → relee.

---

## Conexiones

- [[02-runtime-y-vm]] — qué pasa después del AST
- [[../02_operating_systems/04-syscalls-y-kernel]] — el target final
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Crafting Interpreters** (Robert Nystrom, gratis online en craftinginterpreters.com) — el mejor libro moderno. Construyes 2 implementaciones de un lenguaje (treewalker en Java, bytecode VM en C).
- **Python `ast` module docs** — explora ASTs de Python real.
- **Compilers: Principles, Techniques, and Tools** ("Dragon book", Aho et al.) — el clásico académico, denso.
- **Engineering a Compiler** (Cooper & Torczon) — alternativa moderna al Dragon.
- **ANTLR** (antlr.org) — parser generator popular.
- **Lark** (Python) — parsing library moderna.
