// Ejecuta Python en el navegador con Pyodide (WASM), sin servidor.
// Los bloques los emite gen_course.py como <div class="pyodide-run" data-code="base64(codigo)">
// con un boton, una cajita de entrada (stdin) y un <pre> de salida.
const PYODIDE_VERSION = "0.26.4"

function loadPyodideOnce(): Promise<any> {
  const w = window as any
  if (w.__pyodidePromise) return w.__pyodidePromise
  w.__pyodidePromise = (async () => {
    await new Promise<void>((resolve, reject) => {
      const s = document.createElement("script")
      s.src = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/pyodide.js`
      s.onload = () => resolve()
      s.onerror = () => reject(new Error("no se pudo cargar Pyodide"))
      document.head.appendChild(s)
    })
    return await w.loadPyodide()
  })()
  return w.__pyodidePromise
}

function decodeB64(b64: string): string {
  return new TextDecoder().decode(Uint8Array.from(atob(b64), (c) => c.charCodeAt(0)))
}

async function runBlock(block: HTMLElement) {
  const btn = block.querySelector(".pyodide-btn") as HTMLButtonElement
  const out = block.querySelector(".pyodide-out") as HTMLPreElement
  const stdinEl = block.querySelector(".pyodide-stdin") as HTMLTextAreaElement | null
  const code = decodeB64(block.getAttribute("data-code") || "")
  btn.disabled = true
  out.hidden = false
  out.textContent = "Cargando Python (la primera vez tarda unos segundos)…"
  try {
    const py = await loadPyodideOnce()
    let buf = ""
    py.setStdout({ batched: (s: string) => (buf += s + "\n") })
    py.setStderr({ batched: (s: string) => (buf += s + "\n") })
    const lines = (stdinEl?.value ?? "").split("\n")
    py.globals.set("__stdin_lines__", lines)
    // input() lee de la cajita, linea a linea (sin dialogos que bloqueen)
    await py.runPythonAsync(
      "import builtins\n" +
        "__it__ = iter(list(__stdin_lines__))\n" +
        "def __input__(prompt=''):\n" +
        "    print(prompt, end='')\n" +
        "    try:\n" +
        "        v = next(__it__)\n" +
        "    except StopIteration:\n" +
        "        v = ''\n" +
        "    print(v)\n" +
        "    return v\n" +
        "builtins.input = __input__\n",
    )
    try {
      await py.runPythonAsync(code)
    } catch (e) {
      buf += String(e)
    }
    out.textContent = buf.replace(/\n+$/, "") || "(sin salida)"
  } catch (e) {
    out.textContent = "Error cargando Python: " + String(e)
  } finally {
    btn.disabled = false
  }
}

function setup() {
  document.querySelectorAll(".pyodide-run").forEach((el) => {
    const block = el as HTMLElement
    if (block.getAttribute("data-wired")) return
    block.setAttribute("data-wired", "1")
    const btn = block.querySelector(".pyodide-btn")
    btn?.addEventListener("click", () => runBlock(block))
  })
}

document.addEventListener("nav", setup)
