# Benchmark generator

#####A GUI tool for generation of configuration problem's encodings in ASP.

### Requirements
 - Python 3.7 with tkinter _(the standard GUI library for Python)_
 - [PyPubSub](https://pypi.org/project/PyPubSub/ "PyPubSub on PyPI") >= 4.0.3
 - [clingo](https://anaconda.org/potassco/clingo "Clingo on anaconda") >= 5.4.0

### Setup 
Setup requires using packages from both: PyPI (PyPubSub) and Anaconda (Clingo).\
Example (replace ENVIRONMENT_NAME with the desired environment name):
1. Create new conda environment with Python 3.7 (using Anaconda Prompt):
    ```sh
    (base) >conda create -n ENVIRONMENT_NAME python=3.7
    ```
2. Install pip in the newly created environment
    ```sh
    (base) >conda install -n ENVIRONMENT_NAME pip
    ```
3. Activate the environment:
    ```sh
    (base) >conda activate ENVIRONMENT_NAME
    ```
4. Install clingo (from Anaconda):
    ```sh
    (ENVIRONMENT_NAME) >conda install -c potassco clingo
    ```
5. Install PyPubSub (from PyPI):
    ```sh
    (ENVIRONMENT_NAME) >pip install PyPubSub
    ```
That should do it. To make sure packages have been installed in correct environment, one can execute:
```sh
(ENVIRONMENT_NAME) >conda list
```
on the active environment. When both pypubsub and clingo appear on the list, we should be good to go.
   
### Running
Execute the [main.py](../asp-benchmark-generator/main.py) script, eg:
```sh
$ python3 main.py
```
##Usage

#### Table of Contents
**[1. Initial window](#initial-window)**\
**[2. Component's hierarchy](#component's-hierarchy)**\
**[3. Associations](#associations)**\
**[4. Ports](#ports)**\
**[5. Resources](#resources)**\
**[6. Constraints](#constraints)**\
**[7. Generation](#generation)**\
**[8. Solving](#solving)**

#### Initial Window

#### Component's Hierarchy

#### Associations

#### Ports

#### Resources 

#### Constraints

#### Generation

#### Solving






