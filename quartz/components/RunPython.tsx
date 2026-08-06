// @ts-ignore
import script from "./scripts/runpython.inline"
import styles from "./styles/runpython.scss"
import { QuartzComponent, QuartzComponentConstructor } from "./types"

// Componente invisible: solo inyecta el script y los estilos que hacen funcionar los
// bloques <div class="pyodide-run"> (ejecutar Python en el navegador con Pyodide).
const RunPython: QuartzComponent = () => null

RunPython.afterDOMLoaded = script
RunPython.css = styles

export default (() => RunPython) satisfies QuartzComponentConstructor
