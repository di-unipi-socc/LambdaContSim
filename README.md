# λFogSim (LambdaFogSim)

![example workflow](https://github.com/alessiomatricardi/LambdaFogSim/actions/workflows/pylint.yml/badge.svg)

## Requirements

Make sure to have installed `Python 3.10` or above.

You also have to install [SWI-Prolog](https://www.swi-prolog.org/download/stable) for your platform.

## Instructions

### 1. Clone repository

Clone the repository and all its submodules by executing
```
git clone --recursive https://github.com/di-unipi-socc/LambdaFogSim.git
```

Then open a terminal inside the project root folder and follow the next steps.

### 2. (OPTIONAL) Enviroment setup and requirements installation

It's recommended to setup a virtual enviroment where launch the application.

Install `virtualenv` via pip in order to be able to create one. You can do it by executing

```
pip3 install virtualenv
```

Run this command inside the project's root in order to setup a virtual enviroment.

```
virtualenv -p python3 venv && source venv/bin/activate
```

### 3. Requirements installation

Run this command to install requirements
```
pip install -r requirements.txt
``` 

### 4. Run the simulator

Inside the project root run the simulator with the following command:
```
python3 src/lambdafogsim.py
```

### Options

`-v, --verbose` verbose mode

`-c, --config <configuration file>` define your own configuration file. Default is `config.py`

`-p, --physical <infrastructure configuration file>` define your own physical infrastructure config file. Default is `infrastructure_config.yaml`

`-l, --logical <Prolog infrastructure file>` logical infrastructure config file

`Note` -p and -l options are mutually exclusive

