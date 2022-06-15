# λ-FogSim (LambdaFogSim)

![example workflow](https://github.com/alessiomatricardi/LambdaFogSim/actions/workflows/pylint.yml/badge.svg)

## Requirements

In order to execute LambdaFogSim, make sure to have installed `Python 3.10` or above.

You also have to install [SWI-Prolog](https://www.swi-prolog.org/download/stable) for your platform.

## Instructions

### Initialisation

Run this command inside the project's root in order to setup a virtual enviroment and install requirements.

```
virtualenv -p python3 venv && source venv/bin/activate && pip install -r requirements.txt
```

### Run the project

To run the project you have to open a terminal and execute the following command:
`python3 main.py`

### Configuration

You can also setup the provided configuration file `config.yaml` or build a new one. If you want, you can specify the configuration file by command line executing:

`python3 main.py -c <configuration file>`
