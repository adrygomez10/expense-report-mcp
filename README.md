# Expense Report MCP

Servidor MCP local para preparar gastos de un viaje de trabajo. Python
**3.15.2**, SDK oficial **mcp 2.3.0**, arquitectura limpia y reglas de negocio
independientes del protocolo. Las versiones se comprobaron el 29/10/2026 en
[Python.org](https://www.python.org/downloads/release/python-3152/) y
[PyPI](https://pypi.org/project/mcp/2.3.0/).

El asistente presenta al LLM las herramientas disponibles. El modelo
propone una llamada; el asistente la solicita por MCP y devuelve el resultado
al modelo para continuar o responder. Las reglas y el guardado los ejecuta
esta aplicación. La demo de consola utiliza una secuencia programada sin LLM.

El servidor se comunica por **stdio**, mediante la entrada y salida
estándar del proceso que inicia el cliente. Puedes ejecutarlo con Python o
Docker. No abre una web ni un puerto HTTP.

## Contenido

- [Elegir el recorrido](#1-elegir-por-dónde-empezar).
- [Instalación](#2-preparar-una-instalación-nueva).
- [Demo sin IA y resultados](#3-ejecutar-y-comprobar-la-demo-sin-ia).
- [Conectar un asistente](#4-conectar-un-asistente-y-probar-la-conversación).
- [Docker](#5-ejecutar-el-servidor-con-docker).
- [Parada y datos](#6-parada-datos-y-cambios).
- [Resolver problemas](#7-resolver-problemas-habituales).
- [Arquitectura](#arquitectura).
- [Estilo y calidad](#estilo-y-calidad).
- [Límites](#límites-del-ejemplo).
- [Decisiones de arquitectura](#decisiones-de-arquitectura).

## 1. Elegir por dónde empezar

| Situación | Recorrido |
| --- | --- |
| Ya existe `.venv` en esta copia del proyecto | Ejecuta la demo del apartado 3. |
| Primera instalación con Python | Prepara el entorno del apartado 2 y ejecuta la demo. |
| Quieres conversar con el modelo | Completa la instalación y conecta el asistente en el apartado 4. |
| Prefieres Docker | Sigue el apartado 5; el host necesita Docker, pero no Python ni uv. |

Trabaja desde la raíz de `expense-report-mcp`, donde están `pyproject.toml`,
`uv.lock` y `fixtures/`. En los ejemplos de rutas absolutas usamos
`C:/projects/expense-report-mcp`: sustituye esa carpeta por la ubicación real
de tu copia. El código no tiene que estar en una ruta concreta.

La demo no requiere claves de API, cuenta de IA, Node.js, base de datos
externa ni variables de entorno. La conversación con un modelo sí requiere
un asistente compatible y su acceso habitual al modelo. Docker es opcional.

## 2. Preparar una instalación nueva

El proyecto fija Python **3.15.2** y las dependencias de `uv.lock`. Se utiliza
uv **0.13.6**, la misma versión que CI y la imagen Docker. Necesitas conexión
a Internet para descargar las herramientas y dependencias la primera vez.
Git es necesario si vas a instalar el hook de precommit.

Para obtener el código, ejecuta desde la carpeta donde quieras guardar
el proyecto:

```sh
git clone https://github.com/adrygomez10/expense-report-mcp.git
```

Después entra en la carpeta creada. Los pasos siguientes utilizan
`C:/projects/expense-report-mcp` como ejemplo de ubicación; ajusta esa ruta
a tu copia. Si ya tienes el proyecto, continúa con la preparación del entorno.

### Windows, con PowerShell

Si no tienes uv, instala esa versión mediante el instalador oficial:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/0.13.6/install.ps1 | iex"
```

Abre una terminal nueva para recoger el cambio de PATH. Entra en la carpeta
del proyecto y prepara el entorno:

```powershell
cd C:/projects/expense-report-mcp
uv --version
uv python install 3.15.2
uv sync --frozen
uv run python --version
```

El último comando debe mostrar `Python 3.15.2`. `uv sync --frozen` crea
`.venv` e instala las versiones del lock, incluidas las herramientas de
desarrollo. No necesitas activar el entorno ni instalar paquetes globales.

Algunas copias de trabajo tienen uv en `.tools/bin/uv.exe`, una descarga
local ignorada por Git. En ese caso puedes sustituir `uv` por
`.\.tools\bin\uv.exe`. Esa carpeta no se incluye al clonar el repositorio.

### Linux o macOS

Instala uv si falta:

```sh
curl -LsSf https://astral.sh/uv/0.13.6/install.sh | sh
```

El instalador guarda los ejecutables en `$HOME/.local/bin`. La terminal
actual todavía puede no tener esa carpeta en su `PATH`, por lo que `uv`
puede aparecer como un comando desconocido aunque la instalación haya
terminado correctamente.

En Bash o zsh, también dentro de WSL, carga la ruta en la misma terminal y
comprueba la versión antes de continuar:

```bash
source "$HOME/.local/bin/env"
uv --version
```

Debe aparecer `uv 0.13.6`. También puedes cerrar y volver a abrir la terminal
para recoger el cambio de PATH. En fish, el comando equivalente es
`source "$HOME/.local/bin/env.fish"`.

Después, desde la raíz del proyecto:

```sh
uv --version
uv python install 3.15.2
uv sync --frozen
uv run python --version
```

Consulta otras formas de instalarlo en la
[documentación oficial de uv](https://docs.astral.sh/uv/getting-started/installation/).

### Instalar y ejecutar los controles

En una copia con Git, instala el hook después de crear el entorno:

```sh
uv run pre-commit install
uv run pre-commit run --all-files
```

El segundo comando ejecuta organización de clases, linter, formato, tipado
estricto y pruebas. Debe terminar correctamente. Es el mismo control de CI.
No crea ningún commit. Si has recibido los archivos sin `.git`, puedes
ejecutar los controles directamente:

```sh
uv run python scripts/check_quality.py
```

## 3. Ejecutar y comprobar la demo sin IA

La demo arranca su propio servidor, realiza llamadas MCP reales y termina
cerrando el transporte. No arranques otro servidor antes.

Desde la raíz del proyecto, en PowerShell:

```powershell
.\.venv\Scripts\python.exe -m expense_report.clients
```

En Linux o macOS:

```sh
./.venv/bin/python -m expense_report.clients
```

Con uv disponible, `uv run expense-demo` hace lo mismo en ambos sistemas.
La salida es un JSON con `tools`, `policy`, `prompt`, `preview` y `draft`.
En `preview` deben aparecer estos campos; esta muestra es un extracto:

```json
{
  "trip_id": "trip-madrid",
  "total_eur": "353.90",
  "eligible_eur": "249.90",
  "review_eur": "82.00",
  "excluded_duplicate_eur": "22.00"
}
```

`draft.draft_id` contiene el identificador creado. El informe queda en
`data/expenses.db`; la aplicación crea el directorio y la base si faltan.
Los datos de entrada son los seis justificantes ficticios de
`fixtures/travel.json`, no documentos que tengas que subir.

El tren y el hotel suman 249,90 EUR elegibles. Las comidas suman 70 EUR en
un mismo día y superan el límite de 35 EUR; con el taxi incompleto forman
los 82 EUR que revisar. La copia de una comida aporta los 22 EUR excluidos.
La demo no aprueba, envía ni paga gastos.

### Recuperar lo guardado desde un cliente de lectura

En PowerShell puedes capturar el ID y usarlo en una segunda ejecución:

```powershell
$demo = .\.venv\Scripts\python.exe -m expense_report.clients | ConvertFrom-Json
$draftId = $demo.draft.draft_id
.\.venv\Scripts\python.exe -m expense_report.clients --role reviewer --draft-id $draftId
```

La segunda ejecución debe devolver el mismo `draft_id`, fecha y contenido.
Su lista `tools` incluye `list_trips`, `preview_expense_report` y
`get_expense_draft`; no incluye `create_expense_draft`.

En cualquier sistema también puedes copiar el ID del JSON y ejecutar:

```sh
uv run expense-demo --role reviewer --draft-id ID_DEL_BORRADOR
```

Repetir la demo con los mismos datos devuelve el mismo borrador. Si cambias
el fixture o la política, el servidor conserva el anterior y devuelve un
conflicto. Para un experimento separado, usa otro archivo de base de datos:

```sh
uv run expense-demo --database data/experiment.db
```

## 4. Conectar un asistente y probar la conversación

El asistente inicia el servidor cuando conecta. No necesitas mantener una
terminal con `expense-server` abierta. Usa un chat que se ejecute en tu
equipo: un entorno remoto no puede acceder a estas rutas locales.

| Capacidad | Tipo | Efecto |
| --- | --- | --- |
| `list_trips` | Herramienta | Lista viajes del empleado configurado. |
| `preview_expense_report` | Herramienta | Evalúa sin guardar. |
| `create_expense_draft` | Herramienta | Guarda una instantánea idempotente. |
| `get_expense_draft` | Herramienta | Lee un borrador del empleado. |
| `expense-policy://current` | Recurso | Expone la política ficticia. |
| `prepare_expense_report` | Prompt | Devuelve instrucciones; no ejecuta IA. |

Las herramientas reciben `trip_id` o `draft_id`, nunca rutas locales o SQL.
La identidad se fija al arrancar con `--employee` (por defecto,
`employee-01`). `--read-only` omite la herramienta de escritura. Ese perfil
consulta al mismo empleado, no obtiene acceso global a la empresa.

### Ejemplo concreto: Codex

Configura el servidor mediante el archivo de usuario `~/.codex/config.toml`,
como permite la [documentación oficial de OpenAI](https://learn.chatgpt.com/docs/extend/mcp).
Este procedimiento no depende de encontrar una pantalla de ajustes concreta.

Si utilizas Codex de escritorio en Windows, abre el archivo desde PowerShell:

```powershell
notepad "$env:USERPROFILE\.codex\config.toml"
```

Añade **uno** de los bloques siguientes al final del archivo, conservando
la configuración existente. Si ya hay una sección `[mcp_servers.expense_report]`,
edita esa sección en lugar de duplicarla. Es configuración personal y no se
añade al repositorio de esta aplicación.

#### Codex en Windows con Python de Windows

Usa esta opción si existe `.venv/Scripts/python.exe` en tu proyecto:

```toml
[mcp_servers.expense_report]
command = "C:/projects/expense-report-mcp/.venv/Scripts/python.exe"
args = [
  "-m",
  "expense_report.bootstrap",
  "--fixtures",
  "C:/projects/expense-report-mcp/fixtures/travel.json",
  "--database",
  "C:/projects/expense-report-mcp/data/expenses.db",
  "--employee",
  "employee-01",
]
```

Sustituye las tres rutas por las de tu copia. Si Codex se ejecuta en Linux
o macOS, usa su `~/.codex/config.toml`, cambia el ejecutable por la ruta
absoluta a `.venv/bin/python` y utiliza rutas de ese sistema para los datos.

#### Codex de escritorio en Windows con Python instalado en WSL

Si creaste el entorno desde Ubuntu/WSL, su ejecutable es `.venv/bin/python`,
no `.venv/Scripts/python.exe`. El Codex de Windows puede iniciarlo mediante
`wsl.exe`. Configura este bloque en el archivo de **Windows** indicado arriba:

```toml
[mcp_servers.expense_report]
command = "wsl.exe"
args = [
  "--distribution",
  "Ubuntu",
  "--exec",
  "/mnt/c/projects/expense-report-mcp/.venv/bin/python",
  "-m",
  "expense_report.bootstrap",
  "--fixtures",
  "/mnt/c/projects/expense-report-mcp/fixtures/travel.json",
  "--database",
  "/mnt/c/projects/expense-report-mcp/data/expenses.db",
  "--employee",
  "employee-01",
]
```

Sustituye `Ubuntu` por el nombre de tu distribución, que puedes consultar
con `wsl.exe --list --quiet` desde PowerShell, y cambia las tres rutas por
las rutas Linux de tu copia. Por ejemplo, `C:/projects` se ve dentro de WSL
como `/mnt/c/projects`. Si guardaste el proyecto en `/home`, utiliza esa ruta.

La aplicación de Windows y el CLI instalado dentro de WSL utilizan archivos
de usuario distintos: editar `/home/tu_usuario/.codex/config.toml` no registra
el servidor en el archivo de Windows. El entorno `.venv` también pertenece
al sistema donde se creó; no reutilices un entorno Windows como uno Linux.

#### Recargar y comprobar

Guarda el archivo y cierra y vuelve a abrir Codex para cargar la configuración.
Abre un chat local nuevo y realiza la petición del apartado siguiente.
Deben estar disponibles `list_trips`, `preview_expense_report`,
`create_expense_draft` y `get_expense_draft`.

Si tienes el CLI de Codex en el mismo sistema, `codex mcp list` permite
comprobar que la entrada se ha registrado. Eso no demuestra por sí solo que
el servidor funcione: verifica una llamada real a sus herramientas en el chat.
En otros asistentes utiliza los mismos valores de comando y argumentos en
su configuración de servidor local; el formato del archivo puede ser distinto.

### Petición y comprobación

Abre un chat nuevo tras recargar la conexión y escribe:

> Utiliza las herramientas MCP de expense_report. Consulta mis viajes,
> prepara los gastos de Madrid y guarda un borrador. Explica qué importes
> necesitan revisión e indica el identificador del borrador guardado.

Comprueba las llamadas que muestra el asistente: primero puede encontrar
`trip-madrid` con `list_trips`, después comprobarlo y finalmente guardar.
Debe devolver los mismos importes del apartado 3 y un ID obtenido de la
herramienta de guardado. Si hiciste la demo con la misma base, recuperará
el borrador que ya existía. La redacción del modelo puede variar.

Las confirmaciones de herramientas dependen del asistente. Si solicita
aprobar una llamada, revisa sus argumentos y confirma para continuar.
Que el servidor esté conectado no garantiza que el modelo elija usarlo:
comprueba las llamadas, no solo el texto de la respuesta.

Para un perfil de consulta, añade `--read-only` como último argumento y
recarga el servidor. La herramienta de escritura debe desaparecer. Este
perfil sigue consultando al empleado `employee-01`; no tiene acceso global.

## 5. Ejecutar el servidor con Docker

Necesitas Docker con soporte de contenedores Linux y el motor en marcha.
Desde la raíz del proyecto:

```sh
docker version
docker build -t expense-report-mcp:local .
docker volume create expense-report-data
```

`docker version` debe mostrar tanto cliente como servidor. La construcción
descarga Python y dependencias. El volumen conservará la base de datos
cuando termine el contenedor.

En la configuración MCP del asistente, sustituye el comando anterior por
`docker` y los argumentos por estos, manteniendo cada elemento separado:

```text
run
--rm
-i
-v
expense-report-data:/data
expense-report-mcp:local
```

El contenedor ya tiene configurados el fixture y `/data/expenses.db`. No
necesita rutas del host dentro de sus argumentos. Usa `-i` para mantener la
entrada estándar; no añadas `-t`, `-d` ni puertos publicados.

Guarda, recarga la conexión y repite la petición del apartado 4. Deben
aparecer las mismas herramientas e importes. Pide recuperar el ID después
de reiniciar la conexión: debe conservarse en el volumen. Esta base es
independiente del archivo `data/expenses.db` de la ejecución con Python.

Para ver el arranque manualmente puedes ejecutar:

```sh
docker run --rm -i -v expense-report-data:/data expense-report-mcp:local
```

Ese comando espera mensajes MCP de un cliente. No mostrar una respuesta de
negocio por sí solo es normal. Detén esa prueba con `Ctrl+C`; para conversar,
deja que el asistente lance su propio contenedor mediante la configuración.

Si necesitas el perfil Docker de lectura, añade después del nombre de la
imagen todos estos argumentos, pues reemplazan su comando predeterminado:

```text
--fixtures
/app/fixtures/travel.json
--database
/data/expenses.db
--read-only
```

## 6. Parada, datos y cambios

- La demo termina y cierra su servidor automáticamente.
- El asistente gestiona el proceso stdio. Desconecta o desactiva el servidor
  en su configuración para dejar de utilizarlo; recarga tras cambiar argumentos.
- Un arranque manual se interrumpe con `Ctrl+C`. No hay un servicio instalado.
- Con Docker, `--rm` elimina el contenedor al terminar; el volumen y sus
  borradores permanecen. Usa otro volumen si necesitas un experimento vacío.
- Conserva `fixtures/travel.json` como ejemplo original. Para modificar
  datos usa una copia con `--fixtures` y una base distinta con `--database`.
- Después de cambiar código o dependencias, ejecuta `uv sync --frozen` y
  los controles; recarga el servidor del asistente. Con Docker reconstruye
  la imagen y recarga la conexión para iniciar un contenedor nuevo.

## 7. Resolver problemas habituales

| Síntoma | Qué comprobar |
| --- | --- |
| `uv` no se reconoce | En Bash/zsh (también WSL), ejecuta `source "$HOME/.local/bin/env"` y comprueba `uv --version`. En Windows, reabre PowerShell tras instalarlo. |
| No existe `.venv` o no se encuentra `expense_report` | Ejecuta `uv sync --frozen` desde la raíz y usa el Python de ese entorno. |
| No se encuentra `fixtures/travel.json` al lanzar la demo | Ejecuta desde la raíz o indica rutas absolutas con `--fixtures` y `--database`. |
| El servidor parece quedarse esperando | stdio necesita un cliente MCP. Ejecuta la demo o conéctalo desde el asistente; no lo abras como una web. |
| El asistente no encuentra el comando | Usa la ruta absoluta de Python. Para Docker comprueba que la aplicación puede encontrar `docker` en su PATH. |
| Conectado, pero no aparecen herramientas | Recarga la conexión, consulta sus errores de arranque y revisa comando y argumentos. Un `codex mcp list` muestra configuración, no acredita una llamada correcta. |
| El modelo responde sin usar herramientas | Pídele expresamente usar `expense_report` y comprueba que estén habilitadas en el chat. |
| No aparece `create_expense_draft` | Revisa si has configurado `--read-only`. Es el comportamiento esperado de ese perfil. |
| El ID no existe al recuperarlo | Usa la misma base de datos y empleado. Python local y el volumen Docker no comparten la base. |
| `An earlier draft has different data; review it first.` | Hay un borrador anterior con otra instantánea. Usa una base de experimentación; esta versión no modifica informes existentes. |
| Error al abrir SQLite | Comprueba los permisos de escritura en la carpeta de la base. En Docker utiliza el volumen montado en `/data`. |
| Docker no puede conectar con el motor | Arranca Docker Desktop o el motor Docker y comprueba la sección Server de `docker version`. |
| La construcción no puede descargar imágenes o paquetes | Comprueba Internet, acceso al registro/PyPI y el mensaje de Docker; no cambies el lock para ocultar un fallo de descarga. |

El servidor confía en quien puede iniciar el proceso y leer sus archivos.
`--employee` selecciona una identidad local; no autentica usuarios remotos.
Esta guía cubre la ejecución local, no un despliegue HTTP multiusuario.

## Arquitectura

```text
bootstrap -> adapters -> application -> domain
                  \-----------> domain
```

Las flechas son imports. El SDK MCP no aparece en dominio ni aplicación.
`ExpensePolicy` evalúa objetos valor inmutables: moneda, viaje y justificante.
`ExpenseService` establece acceso al viaje, solicita sus justificantes y
coordina el guardado. Los puertos `TravelData` y `DraftStore` pertenecen a la
aplicación; JSON y SQLite los satisfacen por tipado estructural (`Protocol`).
`adapters/mcp/server.py` registra y traduce las operaciones, sin SQL ni reglas de
importes. `bootstrap.py` es la única composición productiva.

Cada clase vive en un módulo propio y los paquetes agrupan responsabilidades:

```text
src/expense_report/
  domain/                 Reglas y objetos valor
  application/            Casos de uso, contratos, puertos y errores
  adapters/travel/        Lectura y validación del JSON
  adapters/persistence/   SQLite
  adapters/mcp/           Protocolo y modelos de respuesta
  client_contracts/       Contratos de la demo
  bootstrap.py            Composición y arranque del servidor
  clients.py              Demo con cliente MCP
```

## Estilo y calidad

### Clean Code - Python Style 1.1

Perfil propio de estilo inspirado en Clean Code, adaptado a Python.
Incluye la presentación y la lectura del código, además de su diseño.

Python sigue PEP 8 y PEP 257, cuatro espacios y 79 columnas. Ruff 0.17.3
comprueba imports, nombres, docstrings, errores comunes y convenciones;
su formateador conserva la misma longitud objetivo. Los identificadores,
comentarios, docstrings y mensajes técnicos están en inglés.

Separamos validación, preparación, ejecución y resultado cuando representan
fases distintas. Los nombres explican intención. El núcleo recibe sus
dependencias y utiliza `Decimal` para dinero. Los objetos de dominio son
inmutables y sus constructores comprueban invariantes. Las colecciones
expuestas por el dominio son tuplas. Cada puerto responde a una dependencia
real, sin interfaces ni capas añadidas por anticipación.

Las entradas de consola están protegidas por `if __name__ == "__main__"`.
No hay tráfico, lectura de fixtures o escritura SQL al importar. Las
conexiones y subprocesos tienen un ciclo de vida explícito. Las pruebas AST
comprueban la dirección de dependencias. Ruff no certifica los principios
de Clean Code ni sustituye la revisión de contratos y responsabilidades.

### Una clase por módulo

Es una regla obligatoria de organización de esta aplicación: cada clase
tiene su propio archivo. También se aplica a enums, excepciones, protocolos,
`TypedDict`, modelos Pydantic y clases de prueba. No se agrupan por comodidad
en `model.py`, `models.py`, `contracts.py`, `schemas.py` o `errors.py`.

El archivo de producción utiliza el nombre de la clase en `snake_case`:
`ExpensePolicy` vive en `domain/expense_policy.py`; `ReportSnapshot`, en
`application/contracts/report_snapshot.py`. Los paquetes agrupan tipos por
responsabilidad y los imports apuntan a sus módulos concretos. Los imports directos permiten localizar la declaración sin fachadas
de reexportación.

Los módulos que contienen una clase no mezclan funciones sueltas de CLI,
conversión o presentación. Esas funciones viven en módulos propios con una
responsabilidad concreta. `__init__.py` no declara clases. Las pruebas
mantienen el prefijo estándar `test_`, con una clase de prueba por archivo.

`scripts/check_structure.py` comprueba fuentes, pruebas y scripts mediante
AST, sin importar ni ejecutar la aplicación:

| Código | Incumplimiento |
| --- | --- |
| PYORG001 | Más de una clase declarada en un archivo, incluidas las anidadas. |
| PYORG002 | Nombre de módulo inadecuado o clase dentro de `__init__.py`. |
| PYORG003 | Clase mezclada con funciones de módulo. |

El control forma parte de la entrada común de precommit y CI y devuelve
un error ante cualquiera de estos casos. Los imports de clases externas no
se cuentan como declaraciones. No sustituye a las comprobaciones de estilo,
tipado, fronteras y comportamiento que se ejecutan a continuación.

### Presentación y lectura del código

| Regla del perfil | Comprobación |
| --- | --- |
| UTF-8, finales LF, salto final y ausencia de espacios sobrantes | Ruff. |
| Cuatro espacios, 79 columnas y espacios alrededor de operadores | Ruff y su formateador. |
| Comillas dobles y docstrings con triple comilla doble | Ruff Q y formateador. |
| Una sentencia por línea; sin instrucciones comprimidas con punto y coma | Ruff E701/E702. |
| Imports explícitos, ordenados y sin elementos sin utilizar | Ruff I, F401 y F403. |
| Parámetros y argumentos multilínea con continuaciones coherentes | Formateador; respetar comas finales para distribuir argumentos. |
| Una línea en blanco entre métodos y dos entre definiciones de módulo | Ruff y formateador. |
| Separar validación, preparación, ejecución y resultado cuando cambia la intención | Revisión manual; el formateador conserva las líneas. |
| Mantener juntas las instrucciones de una misma operación | Revisión manual; evitar una línea vacía después de cada sentencia. |
| Métodos públicos antes de auxiliares privados, con constructor al principio | Revisión manual. |
| Nombres concretos y condiciones comprensibles; cláusulas de guarda cuando simplifican el recorrido | Convenciones Ruff y revisión semántica manual. |
| Construcciones con muchos campos mediante argumentos con nombre | Revisión manual para evitar tener que contar posiciones. |
| Comprensiones breves; extraer proyecciones y conversiones que ocultan pasos | Revisión manual. |

Ruff es la autoridad para repartir líneas e indentar continuaciones. No se
añade un segundo formateador ni un analizador propio para imponer otra
indentación. Las reglas de Java sobre llaves no se trasladan a Python.
Este perfil se aplica a fuentes, pruebas, scripts y fragmentos del artículo.

Por ejemplo, `preview` obtiene viaje y justificantes, evalúa la política y
separa la construcción de la respuesta. El lector puede seguir esas fases:

```python
def preview(self, trip_id: str) -> ReportSnapshot:
    """Evaluate an owned trip without storing or submitting anything."""
    trip = self._travel.get_trip(self._employee_id, trip_id)
    receipts = self._travel.receipts_for(trip.trip_id)

    evaluation = self._policy.evaluate(trip, receipts)

    return evaluation_view(evaluation)
```

Las conversiones de un registro JSON a `Trip` o `Receipt` tienen auxiliares
con nombres propios y argumentos nombrados. Las proyecciones del informe
separan una línea de gasto de los totales. Se conserva el comportamiento;
no se extraen funciones únicamente para reducir el número de líneas.

### Control automático antes de cada commit

Se utiliza pre-commit 4.7.0 con un hook local versionado. Instalarlo después
de crear el entorno y después de cada clonación:

```sh
uv sync --frozen
uv run pre-commit install
uv run pre-commit run --all-files
```

`scripts/check_quality.py` es la entrada común del hook y de CI. Ejecuta
la organización por clase, Ruff, el formato sin modificar fuentes y mypy estricto
y todas las pruebas de arquitectura y comportamiento. Usa los ejecutables fijados en `.venv`;
si falta el entorno, falla con instrucciones para crearlo. Cualquier error
detiene el control y bloquea el commit. No se crea ningún commit al probarlo.
Pre-commit aparta temporalmente los cambios sin preparar para comprobar el
contenido preparado; `--all-files` comprueba el árbol de trabajo completo.

Además de las reglas PEP 8/257, se comprueban estos límites de función:

| Regla | Límite |
| --- | ---: |
| Complejidad ciclomática, C901 | 10 |
| Parámetros, PLR0913 | 5 |
| Ramas, PLR0912 | 12 |
| Retornos, PLR0911 | 6 |
| Instrucciones, PLR0915 | 50 |

Son avisos convertidos en fallos del control, no puntuaciones de calidad ni
una certificación de Clean Code. Antes de extraer una función por un límite,
comprobar que la separación aporta una responsabilidad y un nombre claros.
La revisión manual sigue siendo necesaria para valorar cohesión, nombres,
duplicación, contratos, errores y el cierre de recursos. Las pruebas AST
vigilan las dependencias hacia el interior y los efectos al importar.

### Convenciones profesionales de Python y tipado

El perfil se apoya en PEP 8/257, el sistema de tipos de Python y las
convenciones de empaquetado. Las elecciones de presentación propias se
documentan como decisiones del proyecto; no se atribuyen al lenguaje.

- Anotar las firmas de producción y de los scripts, preservando los tipos
  de los decoradores con parámetros genéricos y `ParamSpec`.
- Definir las estructuras de entrada y salida. Usar `TypedDict` para los
  contratos de aplicación, `Protocol` para los puertos y colecciones
  abstractas al aceptar datos cuando no se necesita una lista concreta.
- Validar los datos externos en los adaptadores: tipos estrictos, campos
  conocidos, fechas y categorías. El tipado estático no valida un JSON.
- Mantener Pydantic y MCP fuera del dominio y de los casos de uso. Las
  excepciones esperadas tienen nombres con sufijo `Error` y tipos distintos
  para ausencia de acceso y conflictos de borrador. Conservar sus causas.
- Declarar dependencias importadas directamente, incluso si otro paquete
  también las instala; fijar herramientas y resolver dependencias en el lock.
- Marcar el paquete con `py.typed`, conservar `src/`, separar pruebas y no
  ejecutar E/S al importar. Cerrar conexiones y transportes explícitamente.

Mypy 2.4.1 comprueba `src/` y `scripts/` con `strict = true` y sin exclusiones
de errores ni `ignore_missing_imports`. Las pruebas conservan sus controles
de estilo y comportamiento; los casos que introducen datos inválidos
deliberadamente no forman parte del análisis estático de producción.
Pytest trata los avisos de recursos sin cerrar como errores.

El precommit y CI ejecutan Ruff, formato, mypy y pytest mediante la misma
entrada. Se comprueban tanto ejemplos correctos como fallos deliberados de
tipado. Una ejecución correcta acredita esos controles; no convierte esta
demo local en un servicio multiusuario listo para producción.

## Límites del ejemplo

Los justificantes ya están normalizados en JSON: no hay extracción de PDF,
reconocimiento de imágenes, detección de fraude, impuestos o cambio de divisa.
El límite de hotel es por justificante; no calcula noches. Los duplicados
se detectan dentro del viaje por proveedor, número de factura y divisa;
no hay comparación entre viajes ni matching aproximado. Si cambia el importe
de la misma factura, se sigue excluyendo su segunda aparición.

El proceso stdio confía en quien puede arrancarlo y acceder al archivo local.
No es un servicio multiusuario con autenticación. No se debe publicar el
servidor en Internet tal cual. Un despliegue remoto necesita identidad
verificada, permisos por operación, política de datos y transporte HTTP
autorizado. No hay envío, aprobación ni pago de gastos en esta versión.

## Decisiones de arquitectura

Los ADR registran contexto, decisión, alternativas y consecuencias:

- [ADR 0001: dominio y adaptadores](docs/adr/0001-separar-dominio-y-adaptadores.md).
- [ADR 0002: MCP local por stdio](docs/adr/0002-mcp-local-por-stdio.md).
- [ADR 0003: borradores inmutables en SQLite](docs/adr/0003-borradores-inmutables-en-sqlite.md).
