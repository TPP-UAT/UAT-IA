# 📄 UAT-IA

## Requisitos:

- Python >= 3.11  
- Python-venv  
- Docker  
- (Soporte GPU) nvidia-container-toolkit

## 🧠 ¿Qué hace este repositorio?

Tiene dos opciones que sirven para poder generar los modelos de NLP, necesarios para predecir los términos claves en los artículos de astronomía. Estas opciones son:

```
- generate
- train
```

## 🛠️ Instalación:

Para usar esta app, primero necesitás instalar [Docker](https://docs.docker.com/engine/install/ubuntu/)

Para la compatibilidad con GPU, también necesitás instalar el [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

Para instalar Python, podés usar los siguientes comandos:

```bash
sudo apt install python3.11
sudo apt install python3.11-venv
```

## ▶️ Ejecución

Para poder utilizar las opciones mencionadas previamente, es necesario crear un archivo `.env` y agregar las variables de entorno:

```
MODE=generate/train
DB_URL=url_de_la_base_de_datos
```

Después, tenés que ejecutar el archivo docker compose. Esto se logra con el siguiente comando:

```bash
COMPOSE_PROFILES=gpu docker compose up --build
```

Si querés ejecutarlo con capacidades de GPU, o:

```bash
COMPOSE_PROFILES=non_gpu docker compose up --build
```

Si no.

Este archivo docker compose utiliza un Dockerfile que instala todas las dependencias desde el archivo `requierements.txt` dentro del contenedor.

## Opción generate

_Nota_: No es necesario usar capacidades de GPU para esta opción.

Para usar esta opción, necesitás crear una carpeta `PDFs` dentro de la carpeta `data`. Ahí es donde deben estar todos los artículos (archivos en formato PDF).

Esto recuperará toda la información necesaria de cada artículo y la guardará en una base de datos.

Si los artículos están dentro de subcarpetas, necesitás ejecutar el archivo `move_files.py`. Ese script mueve todos los archivos desde subcarpetas a la carpeta `PDFs`.

Para exportar la información generada, debés crear un archivo de volcado (dump). Esto se puede lograr ejecutando en una terminal (con el contenedor activo):

```bash
docker exec -t postgres_db pg_dump -U user -d UAT_IA -t files -t keywords > dump.sql
```

Para importar un archivo dump, colocá el archivo dump en el directorio raíz y ejecutá los siguientes comandos:

```bash
docker cp dump.sql postgres_db:/dump.sql
docker exec -i postgres_db psql -U user -d UAT_IA -f /dump.sql
```

NOTA: Puede suceder que una palabra clave no tenga archivos para una persona, pero sí para otra. Entonces, al importar el archivo dump, podés ejecutar:

```
DELETE FROM keywords k
WHERE file_id IS NULL
  AND EXISTS (
    SELECT 1
    FROM keywords k2
    WHERE k2.keyword_id = k.keyword_id
      AND k2.file_id IS NOT NULL
);
```

Todos los procesos realizados se almacenan en un archivo de log, que se encuentra en `logs/file_generation.log`.

## Opción train

Esta opción se encarga de entrenar todos los modelos de NLP, en base a los archivos almacenados en la base de datos.

Los modelos generados los almecena en la carpeta raíz del proyecto: 

```
./models/
├── abstract/
│   ├── 102
│   └── 104
├── summarize /
│   └── ...
```

_Nota_: En el archivo `.gitignore` se ignora esta carpeta, por lo tanto es necesario copiarla y pegarla en el proyecto `predictions-api` para que resulte útil.

Para poder seleccionar que método de entrenamiento se desea realizar, es necesario modificar el archivo `trainer.py`, seleccionando cual de ellos en el siguiente array (Si se desea entrenar momentáneamente uno solo de los dos, se debe comentar el que no se quiere utilizar):

```
self.input_creators = [
    AbstractInputCreator(database)
    SummarizeInputCreator(database)
]
```

Todos los procesos realizados se almacenan en un archivo de log, que se encuentra en `logs/trainer.log`.
