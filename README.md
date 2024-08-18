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

For the *options 1 and 4*, there's no need to use docker. You can run it a simple python project by using the following commands:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This creates a virtual environment, and install the dependencies called in the file `pyproject.toml`

Then, just run the file `main-old.py` (Check that you're using the venv as interpreter).

For the *options 2 and 3* you need a `.env` file with the variable `MODE` with the values "train" or "predict".

Also, you need to create a docker volume, by using the following commands:

Once installed, first you need to create a new image for the app. This can be made writing:

```bash
docker build -t uat_ia .
```

This Dockerfile installs all the dependencies from the file `requierements.txt` inside the container.

Then you can run the project using:

```bash
docker run --gpus all -it --name uat_ia -p 8080:8080 -v /path_to_project/UAT-IA:/app uat_ia
```

Note: The flag `--gpus all` is necessary if you want to use your GPU inside the docker container.

## Train option

For using this option, you need to create a folder `PDFs` inside the `data` folder. That's where all the articles (PDFs files) are supposed to be. 

If the articles are inside subfolders, you need to run the file `move_files.py`. That script removes all the files from subfolders and leaves them in the `PDFs` folder.

Also, the file `UAT-filtered.json` must be inside the `data` folder.

## Predict option

For using this option, you need another environment variable called `FILE_TO_PREDICT` and the value is the file name from the article you want to predict the keywords. This article must be placed inside `data/prediction_files`.
