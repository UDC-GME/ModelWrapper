# Model Wrapper

ModelWrapper is a Python module providing a class to manage scientific and 
engineering models in Python. Its principal functionalities are:

- Provides an interface to easily incorporate your model in your python 
code 
- It manages the execution of the model
- Makes sure that the model doesn't run twice if the same parameters
where previously calculated


## Preparation

For using the module it is necessary that the model is structured 
using a "black box" approach, in the following fashion:

- A file `parameters.yaml` that contains the parameters of the problem
using the `yaml` format. For example:
```yaml
A: 0.1
E: 2e9
nu: 0.3
```
- A `Makefile` which does:
    * Substitute the parameters in the model input files (using for example
the `jprepro` script.)
    * Executes the necesary commands to run the model
- Generates a file `results.json` which contains the results calculated in 
`json` format. Such as:
```json
{"volume": 0.38,
 "stress": [2.93, -7.07, -4.14]}
```
![](refs/model.png)

See the [examples/models](examples/models) folder for examples using this approach.

## Usage

We will use as an example the model of a three bar truss modeled using Code Aster,
located in [examples/models/3bar](examples/models/3bar). This models returns 
the resulting volume (`"volume"`) and a list with the stresses of each bar (`"stresses"`).
First we import the class that we will use
```python
from ModelWrapper import ModelWrapper
```
Then we intialize the model indicating which parameters will act as desing variables.
```python
model = ModelWrapper('models/3bar', ['A1', 'A2'])
```
An set other other parameters of the problem
```python
model.setParameters({'P': 5.0, 'theta': 45, 'L': 1.0, 
                     'E': 2.1e9, 'nu': 0.3, 'rho': 7800})
```
Now we can generate functions that take as an argument the value of the desing 
variables and return the desired response. For example to get the value of the 
volume:
```python
def vol(x):
    return model.getFun('volume')
```
Or the stresses:
```python
def stress(x):
    return model.getFun('stress')
```
A extended example can be found in [examples/3barOpt.py](examples/3barOpt.py), 
where a minimization of the volume subjected to a set of constraints are defined.
