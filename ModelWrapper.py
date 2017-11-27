import os
import sys
import yaml
import json
import re
import subprocess
import numpy as np

# Loader to interpret floating point notation in yaml file
loader = yaml.SafeLoader
loader.add_implicit_resolver(
    u'tag:yaml.org,2002:float',
    re.compile(u'''^(?:
     [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
    |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
    |\\.[0-9_]+(?:[eE][-+][0-9]+)?
    |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
    |[-+]?\\.(?:inf|Inf|INF)
    |\\.(?:nan|NaN|NAN))$''', re.X),
    list(u'-+0123456789.'))


class ModelWrapper:

    def __init__(self, path, dv):
        if (not os.path.isdir(path)):
            sys.exit('%s is not a directory' % path)
        self.path = path
        if (not all(isinstance(xvar, str) for xvar in dv)):
            sys.exit('Desing variables must be a list of strings')
        self.dv = dv
        # List containng all the evaluations parameters of the model
        self.x_history = []
        # List containng all the results of the model
        self.result_history = []
        # Parameters file
        self.param_file = os.path.join(self.path, 'parameters.yaml')
        # Parameters file
        self.result_file = os.path.join(self.path, 'results.json')
        # Check if desing variables are in the parameters file
        # Generate an empty dict with the keys only for checking
        self._checkParameters(dict.fromkeys(dv))
        # Truncate error and log file
        with open('model-out.log', 'w') as out, \
                open('model-err.log', 'w') as err:
            out.truncate(); err.truncate()

    def _checkParameters(self, params):
        """
            Check if the parameters are in parameters.yaml
        """
        with open(self.param_file, 'r') as f:
            dic = yaml.load(f, Loader=loader)
        try:
            for key in params.keys():
                dic[key]
        except KeyError:
            raise KeyError('Parameter {} not in parameters file'.format(key))

    def run(self):
        if (not len(self.x) == len(self.dv)):
            sys.exit('x array has to be of size equal to the number of '
                     'desing variables = %s' % len(self.dv))
        self.modifyDesign()
        # Run simulation and wait for it to finish
        with open('model-out.log', 'a') as out, \
                open('model-err.log', 'a') as err:
            p = subprocess.Popen('make', cwd=self.path, shell=True,
                                 stdout=out, stderr=err)
            p.wait()
        if (p.returncode is not 0):
            sys.exit("Model didn't execute correctly. "
                     "See model-err.log for details")
        # Collect results
        with open(self.result_file) as f:
            return json.load(f)

    def eval(self, x):
        self.x = x
        # Check if x was previously calculated
        # Relative tolerance comparing numpy arrays
        # must be less than the tolerance of the optimization algorithm
        if not any(np.allclose(self.x, x_old, rtol=1e-7)
                   for x_old in self.x_history):
            # Store a copy of self.x so later modifications doesn't alter
            # the list
            self.x_history.append(self.x.copy())
            self.result_history.append(self.run())
            # Return last calculated result
            return self.result_history[-1]
        else:
            # Return the previously calculated result
            # Get the index where the value is sufficiently close
            index = next(i for i, val in enumerate(self.x_history)
                         if np.allclose(self.x, val, rtol=1e-7))
            return self.result_history[index]

    # Closure to get the desired function
    def getFun(self, name):
        def fun(x):
            return self.eval(x)[name]
        return fun

    def setParameters(self, newValuesDict):
        self._checkParameters(newValuesDict)
        with open(self.param_file, 'r') as f:
            dic = yaml.load(f, Loader=loader)
        gen = (key for key in dic.keys() if key in newValuesDict)
        # Convert numpy array to float to being able to render it  in yaml file
        for key in gen:
            dic[key] = float(newValuesDict[key])
        with open(self.param_file, 'w') as f:
            yaml.dump(dic, f, default_flow_style=False)

    def modifyDesign(self):
        newValuesDict = dict(zip(self.dv, self.x))
        with open(self.param_file, 'r') as f:
            dic = yaml.load(f, Loader=loader)
        gen = (key for key in dic.keys() if key in newValuesDict)
        # Convert numpy array to float to being able to render it  in yaml file
        for key in gen:
            dic[key] = float(newValuesDict[key])
        with open(self.param_file, 'w') as f:
            yaml.dump(dic, f, default_flow_style=False)

    def getNumberOfVariables(self):
        return len(self.dv)
