# UAT-IA

## Requirements:

- Python >= 3.11
- Python-venv
- Docker
- (GPU support) nvidia-container-toolkit

## Installation:

To use this app, first you need to install [Docker](https://docs.docker.com/engine/install/ubuntu/)

For the GPU compatibilty, you need to install also [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

To install python, you can do it using this command:

```bash
sudo apt install python3.11
sudo apt install python3.11-venv
```

## Running the project

The project has multiple options:
- Create a file called pdfs.json which has all the articles by term
- Train models by term
- Predict keywords for a article
- Find the shortest path between 2 files

For the *option 4*, there's no need to use docker. You can run it as a simple python project by using the following commands:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This creates a virtual environment, and install the dependencies called in the file `pyproject.toml`

Then, just run the file `term_path_finder.py` (Check that you're using the venv as interpreter).

For the *other options* you need a `.env` file with the variable `MODE` with the values:
- generate
- train
- predict

Also, you need a variable `DB_URL` with the value:
```bash
postgresql://user:password@db:5432/UAT_IA
```

Then you need to run the docker compose file. This can be achieved by doing:

```bash
COMPOSE_PROFILES=gpu docker compose up --build
```

If you want to run it with GPU capabilities, or:

```bash
COMPOSE_PROFILES=non_gpu docker compose up --build
```

If you don't.

This docker compose file uses a Dockerfile which installs all the dependencies from the file `requierements.txt` inside the container.

## Generate option

_Note_: There's no need to use gpu capabilities for this option.

For using this option, you need to create a folder `PDFs` inside the `data` folder. That's where all the articles (PDFs files) are supposed to be.

This will retrieve all the data needed from every article and save it in a database.

If the articles are inside subfolders, you need to run the file `move_files.py`. That script removes all the files from subfolders and leaves them in the `PDFs` folder.

Also, the file `UAT-filtered.json` must be inside the `data` folder.

To export the data generated, you must create a dump file. This can be achieved by running on a terminal (With the container up):

```bash
docker exec -t postgres_db pg_dump -U user -d UAT_IA -t files -t keywords > dump.sql
```

To import a dump file, you must place the dump file in the root directory and run the following commands:

```bash
docker cp dump.sql postgres_db:/dump.sql
docker exec -i postgres_db psql -U user -d UAT_IA -f /dump.sql
```

NOTE: It may happen that a keyword had no files for one person, but it had for another. So, when importing the dump file, you can run:
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


## Train option

For this option, you just need to make sure the variable is set to MODE=train

Also, the file `UAT-filtered.json` must be inside the `data` folder.

## Predict option

For this option, you need to make sure the variable is set to MODE=predict

For using this option, you need another environment variable called `FILE_TO_PREDICT` and the value is the file name from the article you want to predict the keywords. This article must be placed inside `data/prediction_files`.
