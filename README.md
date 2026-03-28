# Prueba técnica Unumbio
Esta es la prueba técnica para el puesto de Desarrollador de Python (WebScraping).

## 1. Instrucciones de instalación:

Antes de comenzar, asegúrate de tener instalado:
* **Python 3.12+**
* **pip** (gestor de paquetes de Python)
* **git** (opcional, para clonar el repo)

---

### 1.1 Clonar el repositorio:
```bash
git clone https://github.com/Maslow12/prueba-tecnica-unumbio.git
cd prueba-tecnica-unumbio.git
```

### 1.2 Crear un entorno virtual y activarlo:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Instalar dependencias:

Para ello se hace uso del archivo requirements.txt:

```Bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.4 Uso

Para ejecutar la aplicación, utiliza el siguiente comando:

```Bash
python main.py
```

En el caso de que se quieran incorporar más códigos se puede cambiar la siguiente variable ```default_values``` del tipo ```list```, o tambien se puede hacer uso del siguiente comando:

```bash
python main.py -i <filing_number-1> <filing_number-2> ...
```
 
## 2. Análisis de la página:

### 2.1 Obtención del ID a partir de filling_number:

Primeramente, se evaluó el funcionamiento de la página, al ser esta un SPA no se puede obtener la información con una simple petición HTTP, para ello inspeccionando la Network y la carga de la página se descubrió que las búsquedas hechas en la parte superior del buscador se obtenían a partir de una petición de la API la cual adjunto su URL

```
https://digitalip.cambodiaip.gov.kh/api/v1/web/trademark-search
```

Donde a partir de un payload ```Content-type application/json``` se pasan los parámetros del filtro, el payload se puede ver en el archivo ```properties.py```

> [!IMPORTANT]

Para que la petición sea correcta, se necesitan los siguientes headers:

```
{
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,es-VE;q=0.5',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://digitalip.cambodiaip.gov.kh',
}
```

Ya que de lo contrario no toma el filtro y sencillamente manda cualquier información.

La api responde con el resultado enlistado del filtro aplicado, a partir de ellos obtenemos el parametro ```id```

### 2.2 Obtención de la Imagen:

Con el ```id``` obtenido en el paso anterior, se puede hacer uso de esta URL la cual contiene la imagen de la compañía:

```
https://digitalip.cambodiaip.gov.kh/trademark-detail-logo/<id>?type=ts_logo_detail_screen
```

Esta url no necesita Cookies ni login, por lo tanto, se puede obtener la imagen como un ```bytes``` y guardarla

Para verificar la imagen se hizo uso de la librería ```Pillow```, inicialmente se analizaron 3 soluciones:

* Se verificaría el Content-Type a ver si era tipo "image/jpeg", pero debido a que aunque no existiera la imagen y mandara HTML mandaba el mismo Content-Type, entonces esta manera de analizar el contenido no era válida

* Se utilizaría una expresión regular (Regex), ya que si la imagen no existe el contenido generaba un HTML es por ello que se verificaría si el contenido era HTML o era un archivo encodeado tipo imagen, este método funcionaba, pero era poco robusto, ya que puede existir bytes parecidos a tags HTML

* Por último el método más robusto era obtener los bytes de la imagen y analizarlos con ```Pillow``` para verificar si era una imagen válida o no y así guardar archivo no corruptos. Ojo este método puede ser menos eficiente que los anteriores

### 2.3 Obtención del HTML de la página de detalle:

En ese caso se hizo uso de PlayWright tipo Headless, debido a que al ser una página SPA, se necesita renderizar para obtener el HTML, sin embargo, la página por detrás a partir de los query params, maneja los filtros encodeados para cargar el contenido, es por ello que es necesario obtener los filtros del paso anterior procesar la data y obtener esos parámetros encodeados. El parámetro ```afnb``` no debe ir encodeado, ya que genera problemas a la hora de renderizar la página.

> [!IMPORTANT]
> Otra consideracion es que cuando se realizan muchas peticiones desde una misma IP la pagina no carga, por lo tanto, es bueno implementar algun servicio de Proxy tipo Oxylab, SmartProxy, etc. 

## 3. Decisiones técnicas:

### 1. Uso de consultas HTTP:

A partir del análisis anterior se utilizó consultas HTTP a las rutas de la API, ya que no generaba bloqueo por consulta. Porque la prueba técnica exige un uso de módulos asíncronos se tomó la decisión de utilizar la librería ```aiohttp``` esto debido a su documentación, performance y experiencia previa utilizando esta librería. 

Para crear un app reutilizable y extrapolable a otro tipo de scrapers se crearon clases útiles tanto para lal utilización de las peticiones request (```RequestsScraper```) y lautilización de Playwright (```PlaywrightScraper```)

La clase ```RequestsScraper``` genera una sesión del tipo ```aiohttp.ClientSession``` esto para manejar las cookies, headers, …, de las peticiones anteriores. Esta clase cuenta con las utilidades básicas para la solución de esta prueba técnica ya sea la obtención de contenido tipo ```bytes``` y la obtención de contenido ```json``` y por último el uso de una método ```close``` para cerrar la sesión.

### 2. Uso de PlayWright Headless:

Ya que la página es un SPA y el contenido se carga dinámicamente, no se puede realizar solamente un HTTP (GET) para obtener el contenido, es por ello que se utiliza un navegador headless para renderizar este contenido y obtener todo el HTML completo.

### 3. Manejo de archivos:

Para realizar todos los procesos asíncronos, se hizo uso de una librería para manejar el proceso de guardado de archivos de manera asíncrona llamada ```aiofiles```, además se creó la clase ```FileManager``` la cual tiene métodos para guardar contenido con bytes y contenido de texto plano. Todo ello en el folder ```./output```

### 4. Decoradores:

Se creó un decorador retry (```@retry(retries=3, initial_delay=2)```) para las conexiones HTTP e intentar si existe algún fallo por conexión, se utilizó una clase Exception para capturar cualquier excepción, sin embargo, es mejor dividir las excepciones y hacer un log de los errores para mejor trazabilidad, esta consideración se realiza después a modo de mejorar el código, considerando que esto es una prueba técnica.

### 5. Uso de concurrencia asíncrona:

Se implementó ```asyncio.gather``` para optimizar la eficiencia del programa mediante la ejecución concurrente de tareas. Esto permite centralizar la gestión de múltiples corrutinas y unificar la obtención de sus resultados en una única estructura organizada.

### Consideraciones adicionales:

* En el caso del navegador headless solamente utiliza un ```wait_until="networkidle"``` esto significa que el navegador espera hasta que el network no tenga más conexiones, al ser una página SPA funciona muy bien, sin embargo, para mayor robustez se puede utilizar un ```wait_for_selector()``` para esperar que algún elemento cargue completamente

* Se creó un scraper basado en clases para tener metodos comunes como es el caso del método ```scrape()``` y ```close()``` esto, ya que se puede utilizar con un patrón de diseño singleton y reutilizarse distintos scrapers de distintas páginas con métodos comunes

* Se agregaron multiples filing_numbers a modo de prueba aqui se deja la lista:

```python3
default_values = [
    "KH/49633/12",
    "KH/59286/14",
    "KH/83498/19",
    "KF/388383/19", # Wrong Number,
    "KF/345354/19", # Wrong Number,
    "KH/122290/26", # No Image
]
```

* El tiempo de ejecucion se puede obtener en una terminar con ```bash``` de la siguiente manera:

```bash
time python main.py
```

El resultado con todos los ```filling_numbers``` de arriba:

```
real    0m33.853s
user    0m8.450s
sys     0m1.794s
```

Con solamente los 3 descritos en la prueba:

```
default_values = [
    "KH/49633/12",
    "KH/59286/14",
    "KH/83498/19",
]
```

```
real    0m14.521s
user    0m6.419s
sys     0m1.298s
```
