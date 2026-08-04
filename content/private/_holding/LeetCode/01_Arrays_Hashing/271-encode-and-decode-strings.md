---
title: "LeetCode 271 — Encode and Decode Strings"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/arrays-hashing, patron/serializacion, patron/length-prefix, embebido]
type: nota
status: en-progreso
source: claude-code
aliases: [Encode Decode Strings, LC 271, Codec design, Length-prefix encoding]
problem_id: 271
difficulty: medium
patron: arrays-hashing
neetcode_order: 6
---

# LeetCode 271 — Encode and Decode Strings

> **Sexto problema del NeetCode 150 en Arrays & Hashing**. Distinto del resto: es un problema de **diseño de protocolo de serialización**. La técnica clave (**length-prefix encoding**) es **exactamente la que tú usas en el protocolo binario embebido** — la conexión es directa.
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.
> Originalmente "Premium" en LeetCode — disponible gratis en NeetCode y en LintCode #659.

## Enunciado

Diseña un algoritmo para **codificar** una lista de strings en una sola string, y **decodificar** esa string de vuelta a la lista original.

```python
class Codec:
    def encode(self, strs: List[str]) -> str:
        ...
    def decode(self, s: str) -> List[str]:
        ...
```

El uso será:
```python
# Sender
codec = Codec()
encoded = codec.encode(strs)
# ... transmite 'encoded' por red ...
# Receiver
decoded = Codec().decode(encoded)
assert decoded == strs
```

**Ejemplo 1:**
```
Input:  ["hello", "world"]
Output: ["hello", "world"]    (después de encode + decode)
```

**Ejemplo 2:**
```
Input:  ["", "abc", ""]
Output: ["", "abc", ""]
```

**Restricciones:**
- `1 <= strs.length <= 200`
- `0 <= strs[i].length <= 200`
- `strs[i]` puede contener **cualquier carácter** (UTF-8 / ASCII completo). **Esto es crítico**: no puedes asumir que un carácter no aparece en las strings.

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué problema resuelve? | Serializar una colección heterogénea para transmisión / persistencia |
| ¿Hay carácter "seguro" para usar como separador? | **NO** — las strings pueden contener cualquier carácter |
| ¿Strings vacíos permitidos? | Sí — el codec debe distinguir `["", "a"]` de `["a"]` |
| ¿La codificación debe ser óptima en bytes? | El problema no lo pide; piden corrección. Optimización es follow-up |
| ¿Es el receptor de confianza? | Sí (no es problema de seguridad; encode no necesita firmar) |

> **El reto**: encontrar un esquema que sea **inyectivo** (cada lista da una string distinta) sobre cualquier alfabeto, sin asumir nada de las strings.

---

## Solución 1 — Separador "seguro" (FALLA si las strings tienen alfabeto libre)

Si **garantizas** que un carácter (e.g. `,`) no aparece en las strings, puedes hacer:

```python
class Codec:
    def encode(self, strs):
        return ','.join(strs)
    def decode(self, s):
        return s.split(',')
```

**Por qué falla:** si `strs = ["a,b", "c"]`, encode da `"a,b,c"`, y decode lo parte en `["a", "b", "c"]` — **incorrecto**. Cualquier carácter elegido como separador puede aparecer en los datos.

> **Lección general**: en cualquier protocolo de serialización, **nunca confíes en que un carácter no aparezca en los datos** salvo que lo controles explícitamente (e.g. base64 garantiza solo `A-Za-z0-9+/=`).

---

## Solución 2 — Length-prefix encoding (la canónica)

**La idea**: prefijar cada string con su **longitud + un delimitador** que separa la longitud del contenido. Por ejemplo, `["hello", "world"]` se codifica como `"5#hello5#world"`.

Para decodificar: leer dígitos hasta `#`, luego leer exactamente esa longitud de caracteres como string, repetir.

```python
class Codec:
    def encode(self, strs: List[str]) -> str:
        return ''.join(f"{len(s)}#{s}" for s in strs)

    def decode(self, s: str) -> List[str]:
        result, i = [], 0
        while i < len(s):
            j = s.find('#', i)                  # busca el siguiente #
            length = int(s[i:j])                # parsea la longitud
            result.append(s[j+1 : j+1+length])  # lee 'length' caracteres
            i = j + 1 + length                  # avanza al siguiente bloque
        return result
```

**Trace mental con `["hello", "wo#rld"]`**:

| Paso | Acción | i | Encoded |
|---|---|---|---|
| 1 | Encode "hello" | — | `"5#hello"` |
| 2 | Encode "wo#rld" | — | `"5#hello6#wo#rld"` |
| 3 | Decode: i=0, j=1 (find # desde 0) | 0 | length=5, append "hello" |
| 4 | Decode: i=7, j=8 (find # desde 7) | 7 | length=6, append "wo#rld" |

**¿Por qué funciona aunque las strings contengan `#`?** Porque en `decode`, una vez que sabes la longitud, lees **exactamente** esos caracteres sin mirar su contenido. El `#` dentro de "wo#rld" no se interpreta como delimitador — solo como dato.

**Análisis:**
- **Tiempo encode: O(n)** total (n = suma de longitudes).
- **Tiempo decode: O(n)** total — `s.find('#', i)` es lineal en cada iteración, pero las iteraciones cubren cada carácter una sola vez.
- **Espacio: O(n)** en ambos.
- **Veredicto:** [OK] **la respuesta canónica**. Funciona con cualquier alfabeto. Es **literalmente lo que hacen** protocolos binarios reales (HTTP/1.1 chunked encoding, Protocol Buffers de Google, etc.).

### Desglose detallado del decode — sintaxis por sintaxis

Si la línea `length = int(s[i:j])` o `j = s.find('#', i)` te resulta extraña, esta es la explicación pieza por pieza. Las tres operaciones que aparecen son:

#### `s.find(sub, start)` — buscar a partir de un índice

Método de string que **busca la primera aparición de `sub`** dentro de `s`, **empezando desde el índice `start`**. Devuelve el índice donde la encuentra, o `-1` si no.

```python
texto = "hola#mundo#fin"

texto.find('#')          # 4   (primera aparición desde el inicio)
texto.find('#', 5)       # 10  (busca desde índice 5 → segundo #)
texto.find('#', 11)      # -1  (no hay # desde 11 en adelante)
```

El segundo argumento es opcional. Sin él, busca desde el principio. **En decode, lo usamos para no encontrar el `#` del bloque ya procesado.**

> **Variante**: `s.index(sub, start)` hace lo mismo pero **lanza `ValueError` si no encuentra**. Para decoding, prefiere `find()`.

#### `s[i:j]` — slicing recordatorio

`s[i:j]` te da el substring desde el índice `i` hasta `j` (sin incluir `j`).

```python
texto = "hello"
#        0  1  2  3  4

texto[0:3]       # "hel"   (índices 0, 1, 2 — 3 NO incluido)
texto[2:5]       # "llo"
texto[1:1]       # ""      (cuando i==j, slice vacío)
```

Tres reglas: el índice inicial **se incluye**, el final **no**; la longitud del slice es `j - i`; si `i == j`, el slice es vacío.

#### `int(string)` — convertir substring a entero

Si `s[i:j]` produce un substring que representa un número, `int()` lo convierte:

```python
int("5")         # 5
int("42")        # 42
int("0042")      # 42 (los ceros a la izquierda se ignoran)
```

Combinado con slicing: `int(s[i:j])` es **"extrae el substring de dígitos y conviértelo a entero"**.

### Trace visual con `["hello", "world"]`

`encode` produce `"5#hello5#world"`. Vamos a verla con todos los índices:

```
Índice:  0  1  2  3  4  5  6  7  8  9 10 11 12 13
Char:   '5''#''h''e''l''l''o''5''#''w''o''r''l''d'
        └┬─┘ └────┬───┘  └┬─┘ └─────┬─────┘
       len#1   data1    len#2     data2
```

`len(s) = 14`.

**Iteración 1** (estado inicial: `i = 0`, `result = []`):

```
(a) j = s.find('#', i) = s.find('#', 0)
    Busca '#' desde índice 0 → lo encuentra en índice 1.
    j = 1

(b) length = int(s[i:j]) = int(s[0:1]) = int("5") = 5

    Visualización de s[0:1]:
    Índice:  0  1  2  3 ...
    Char:   '5''#''h''e' ...
            └┘
            s[0:1] = "5"

(c) result.append(s[j+1 : j+1+length])
                       = s[1+1 : 1+1+5]
                       = s[2 : 7]

    Visualización de s[2:7]:
    Índice:  0  1  2  3  4  5  6  7 ...
    Char:   '5''#''h''e''l''l''o''5' ...
                  └────────────┘
                  s[2:7] = "hello"
                  (índices 2, 3, 4, 5, 6 — 7 NO incluido)

    result = ["hello"]

(d) i = j + 1 + length = 1 + 1 + 5 = 7

    El nuevo i apunta al primer dígito del SIGUIENTE bloque:
    Índice:  0  1  2  3  4  5  6  7  8  9 10 11 12 13
    Char:   '5''#''h''e''l''l''o''5''#''w''o''r''l''d'
                                  ↑
                                  i = 7
```

**Iteración 2** (`i = 7`, `result = ["hello"]`):

```
(a) j = s.find('#', i) = s.find('#', 7)
    Busca '#' desde índice 7 → lo encuentra en índice 8.
    j = 8

(b) length = int(s[i:j]) = int(s[7:8]) = int("5") = 5

(c) result.append(s[j+1 : j+1+length])
                       = s[8+1 : 8+1+5]
                       = s[9 : 14]

    Visualización de s[9:14]:
    Índice:  7  8  9 10 11 12 13
    Char:   '5''#''w''o''r''l''d'
                  └────────────┘
                  s[9:14] = "world"

    result = ["hello", "world"]

(d) i = j + 1 + length = 8 + 1 + 5 = 14
```

**Comprobación de salida del while**: `i = 14`, `len(s) = 14`. `14 < 14` es `False` → sale del while.

Return `result = ["hello", "world"]` [OK].

### Por qué cada `+1` y `+length` aparecen donde aparecen

Esta es la parte que más confunde. La estructura de un bloque encoded es:

```
                  ┌─────┐
Índice:    ...  i ...  j  j+1  ...  j+length  ...
Char:      ... [dígitos][#][   data       ][siguiente]
                └──┬──┘  │  └──────┬──────┘
                  len    │       length chars
                         │
                  separador (1 carácter)
```

| Expresión | Significado |
|---|---|
| `s[i:j]` | Los dígitos de la longitud. **Hasta `j` (no incluido)** porque `j` es el `#` |
| `j + 1` | Saltar el `#` (el `#` ocupa **1 carácter**) |
| `j + 1 + length` | Final del data: avanzar `length` caracteres desde `j+1` |
| `i = j + 1 + length` | El siguiente bloque empieza justo donde termina el data actual |

**Intuición clave**: el `#` ocupa exactamente un carácter. Después del `#` empiezan los `length` caracteres del dato. Por eso siempre ves `j+1` (saltar el `#`) y `j+1+length` (final del dato).

### Caso "el dato contiene `#`" — por qué la magia funciona

Lo crucial es entender: una vez que conoces `length`, **lees `length` caracteres SIN MIRAR su contenido**. Si dentro hay un `#`, no se confunde con un separador, porque ya no estás "buscando" más `#` en ese bloque — solo leyendo `length` caracteres con slicing directo.

```
encode(["hello", "wo#rld"]) = "5#hello6#wo#rld"

Índice:  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14
Char:   '5''#''h''e''l''l''o''6''#''w''o''#''r''l''d'

Iter 1: i=0, j=1, length=5
        s[2:7] = "hello"
        i = 7

Iter 2: i=7
        s.find('#', 7) → encuentra el '#' en índice 8 (NO el de índice 11)
        j = 8
        length = int(s[7:8]) = 6
        s[9:15] = "wo#rld"   ← incluye el '#' como dato, NO como separador
```

Esto es **exactamente** la idea de length-prefix: la longitud te dice cuántos caracteres leer, sin importar lo que sean.

---

## Solución 3 — Length como entero de tamaño fijo (variante)

Si quieres evitar el delimitador `#` (y el `find()`), puedes prefijar cada string con su longitud como **entero de N bytes fijos**.

```python
class Codec:
    def encode(self, strs):
        # 4 bytes = hasta 2^32 longitud — más que suficiente
        return ''.join(f"{len(s):04d}{s}" for s in strs)

    def decode(self, s):
        result, i = [], 0
        while i < len(s):
            length = int(s[i:i+4])
            result.append(s[i+4 : i+4+length])
            i += 4 + length
        return result
```

**Análisis:** mismo O(n) que Solución 2, pero **sin necesidad de `find()`**. Más rápido en la práctica si las strings son cortas (porque saltas exactamente 4 bytes en lugar de buscar el `#`).

> **Esta variante es exactamente la cabecera de tu protocolo binario embebido**: longitud + payload. Lo único distinto es que tú usas big-endian de 2 bytes en binario en vez de 4 dígitos decimales en string.

---

## Solución 4 — JSON dump (la "trampa")

```python
import json
class Codec:
    def encode(self, strs):
        return json.dumps(strs)
    def decode(self, s):
        return json.loads(s)
```

**Análisis:** funciona, pero el entrevistador rara vez la acepta porque "delegas el problema en una librería". Es como decir "uso `import this`". Útil mencionarla como "obvio que en producción usarías JSON o protobuf, pero el ejercicio es entender el mecanismo".

---

## El patrón general — "Length-prefix framing"

**Cuándo aplicar**:

> Cuando necesitas serializar una **secuencia de elementos de longitud variable** sobre un canal que solo entiende streams (red, fichero, string), y los elementos pueden contener cualquier byte/char.

**Plantilla mental**:

```
[len_1][delimitador?][data_1][len_2][delimitador?][data_2] ...
```

**Variantes en producción real**:

| Sistema | Formato de length |
|---|---|
| HTTP/1.1 chunked | hexadecimal + `\r\n` |
| Protocol Buffers | varint (1-10 bytes) |
| MessagePack | 1-5 bytes según tipo |
| **Tu embebido** | 2 bytes big-endian + payload |
| Redis RESP | `$<n>\r\n<data>\r\n` |
| Memcached | similar a HTTP |

**Tres señales** del patrón:

1. Datos heterogéneos a transmitir/persistir.
2. No hay carácter seguro para separar.
3. El receptor debe poder reconstruir la secuencia exactamente.

---

## Variaciones del problema

| Problema | Variación |
|---|---|
| **535. Encode and Decode TinyURL** | Mapeo bidireccional URL ↔ código corto (no es serialización pero sí codec) |
| **449. Serialize and Deserialize BST** | Lo mismo aplicado a árboles binarios |
| **297. Serialize and Deserialize Binary Tree** | Más general (cualquier árbol binario, con `null`s) |

---

## Conceptos a interiorizar

### `str.find(char, start)`

```python
"hello#world".find('#')          # 5
"hello#world".find('#', 6)       # -1 (no encontrado, devuelve -1)
"hello#world".find('#', 0)       # 5 (mismo que sin start)
```

Devuelve `-1` si no encuentra. Útil para parsing de bloques.

### Slicing strings

```python
s = "5#hello"
s[0:1]                # "5"
s[2:7]                # "hello"
s[2:]                 # "hello"
s[-5:]                # "hello"
```

Slicing es O(k) donde k es la longitud del resultado.

### f-strings con format spec

```python
f"{42:04d}"          # "0042" — relleno con ceros, 4 dígitos
f"{42:08b}"          # "00101010" — binario, 8 bits
f"{'abc':<10}"       # "abc       " — alineado izquierda, ancho 10
```

---

## Comparación final de las 4 soluciones

| Solución | Funciona con alfabeto libre | Complejidad | Veredicto |
|---|---|---|---|
| 1. Separador "seguro" | [NO] | O(n) | [NO] Falla casos |
| 2. **Length + delimitador `#`** | [OK] | O(n) | [OK] La canónica |
| 3. **Length de tamaño fijo** | [OK] | O(n) | [OK] Más rápida en práctica |
| 4. JSON dump | [OK] | O(n) | "Trampa", no es ejercicio |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** (length + `#`) desde cero. Tanto `encode` como `decode`.
2. Justifica por qué el `#` puede aparecer dentro de las strings sin romper la decodificación.
3. Trace mental con `strs = ["", "12#3", ""]`:
   - Estado de la string codificada.
   - Pasos del decode con valores de `i` y `j`.
4. **Bonus** — implementa la Solución 3 (length de 4 bytes fijos). ¿Cuándo conviene cada una?
5. **Conexión embebido** — describe en una frase el paralelismo entre este length-prefix y la cabecera binaria de tu protocolo.

---

## Cosas que te pueden preguntar en entrevista

- **"¿Y si las strings fueran enormes (megabytes)?"** → No cambia el algoritmo, solo la representación de la longitud (4 bytes fijos vs delimitador). Para strings >10MB, usar 8 bytes.
- **"¿Cómo lo extenderías a un diccionario `Dict[str, str]`?"** → Codificar como lista alternada [k1, v1, k2, v2, ...] con la misma técnica. O length-prefix dos niveles (length de pares).
- **"¿Y si necesitaras enviar la longitud por la red en bytes (no en string)?"** → Usar `int.to_bytes()` y `int.from_bytes()` con un endianness fijo (big-endian es el estándar de red). Esto es **exactamente lo que haces en embebido**.
- **"¿Cómo manejarías corrupción del stream?"** → Añadir CRC al final de cada bloque (cabecera + length + data + CRC). Los datasets como Parquet hacen esto.

---

## Conexiones

- **Tu protocolo binario embebido** — usas length-prefix con cabecera de 2 bytes y CRC. Este problema es la versión "string-based" del mismo concepto. Ver Capítulo 3 (Protocolo) de la documentación técnica de embebido.
- — el protocolo binario de embebido ilustra el mismo patrón en producción.
- [[1-two-sum]] — patrón anterior del NeetCode 150.
- Próximo: [[238-product-of-array-except-self]] — prefix/suffix products.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 (encode + decode) desde cero
- [ ] Justificado por qué el `#` puede aparecer en las strings sin romper
- [ ] Implementada Solución 3 (length de tamaño fijo)
- [ ] Articulada la conexión con el protocolo binario embebido
- [ ] Resuelto en LeetCode/NeetCode con éxito
