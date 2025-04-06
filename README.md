# TUNI-RAG

This is a minimal implementation of the RAG model for question answering.

## Requirements

Python 3.8 or later

1) Download and install Miniconda (anaconda minimal package manager ) [https://www.anaconda.com/docs/getting-started/miniconda/install]
2) Creaate a new env using the command:
```bash
$ conda create -n your_app_name python=3.8
```

3) Activate the env
```bash
$ conda activate
```
### (OPTIONAL) setup your command line interface for better readability

```bash
export PS1="\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "
```

## Installation

### Install required packages

```bash
pip install -r requirements.txt
```

### SETUP ENVIRONMENT VARIABLES

```bash
cp .env.example .env
```