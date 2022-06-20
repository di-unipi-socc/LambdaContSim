# λ-FogSim (LambdaFogSim)

![example workflow](https://github.com/alessiomatricardi/LambdaFogSim/actions/workflows/pylint.yml/badge.svg)

## Requirements

Make sure to have installed `Python 3.10` or above.

You also have to install [SWI-Prolog](https://www.swi-prolog.org/download/stable) for your platform.

## Instructions

### Enviroment setup and requirements installation

It's recommended to setup a virtual enviroment where launch the application.

Install `virtualenv` in order to be able to create one. You can do it by executing

```
pip3 install virtualenv
```

Run this command inside the project's root in order to setup a virtual enviroment and install requirements.

```
virtualenv -p python3 venv && source venv/bin/activate && pip install -r requirements.txt
```

### Run the simulator

To run the simulator you have to open a terminal and execute the following command:
`python3 lambdafogsim.py`

### Options

`-c, --config <configuration file>` define your own configuration file. Default is `config.py`

`-p, --physical <infrastructure configuration file>` define your own physical infrastructure config file. Default is `infrastructure_config.yaml`

`-l, --logical <Prolog infrastructure file>` logical infrastructure config file

`Note` -p and -l options are mutually exclusive

