import yaml
import sys
import json
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from shutil import copy, rmtree
import subprocess
import pandas as pd
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

class Model:

    def __init__(self, path, dv, config={'commands': 'make', 'init': False,
                                         'clean': False}, 
                 name = 'model'):

        self.config = config
        if (not path.is_dir()):
            sys.exit('%s is not a directory' % path)
        self.path = path
        # Run folder
        self.runPath = self.path / 'run'
        if not self.runPath.exists():
            self.runPath.mkdir()

        if (not isinstance(name, str)):
            sys.exit('Name must be a string' % name)
        self.name = name

        if (not all(isinstance(xvar, str) for xvar in dv)):
            sys.exit('Model variables must be a list of strings')
        self.dv = dv
        
        parametersFile = path / 'parameters.yaml'
        if (not parametersFile.exists()):
            sys.exit('No parameters.yaml file in %s' % path)
        self.rootParametersFile = parametersFile

        self._checkParameters()

        # Init empty dataframe for history
        self.df = pd.DataFrame({})


    def getNumberOfVariables(self):
        return len(self.dv)
    
    def _checkParameters(self):
        """
            Check if the parameters are in parameters.yaml
        """
        with self.rootParametersFile.open('r') as f:
            dic = yaml.load(f, Loader=loader)
        try:
            for key in self.dv:
                dic[key]
        except KeyError:
            raise KeyError('Parameter {} not in parameters file'.format(key))

    def run(self, x):

        if (not len(x) == len(self.dv)):
            sys.exit('Input array has to be of size equal to the number of '
                     'model variables = %s' % len(self.dv))
        self.x = x

        launchPath = self._createLaunchFolder()
        self._modifyParameters(launchPath)
        if self.config['init']:
           initPaths = self._initFiles(launchPath)
        # Copy not initialized files to launchpath 
        self._copyNotInit(launchPath, initPaths)

        outLog = launchPath / 'model-out.log'
        errLog = launchPath / 'model-err.log'
        with outLog.open('w') as out, errLog.open('w') as err:
            for command in self.config['commands']:
                p = subprocess.Popen(command, cwd=str(launchPath), shell=True,
                                     stdout=out, stderr=err)
                p.wait()
                if (p.returncode is not 0):
                    sys.exit("The following command didn't execute correctly: \n"
                             "$ "+command+"\n"
                             "In folder: " + str(launchPath) + "\n"
                             "See model-err.log for details")
        # Collect results
        self.result_file = launchPath / 'results.json'
        # Function to convert strings to integers
        intHook = lambda d: {int(k) if k.lstrip('-').isdigit() 
                             else k: v for k, v in d.items()}
        with self.result_file.open('r') as f:
            self.results =  json.load(f, object_hook=intHook)

        # Add results to history
        self._appendResults()

        if self.config['clean'] :
            rmtree(str(launchPath))
            
            
    def _appendResults(self):
        if self.df.empty:
            self._initDataframe()
        rowDict = dict(zip(self.dv, self.x))
        resultsDict = flattenDict(self.results)
        rowDict.update(resultsDict)
        row = []
        row = [rowDict[key] for key in self.df.columns]
        self.df.loc[len(self.df)] = row

        
    def _initDataframe(self):
        flattenResultsDict = flattenDict(self.results)
        columns = self.dv + list(flattenResultsDict.keys())
        self.df = self.df.reindex(columns=columns)


    def _copyNotInit(self, launchPath, initPaths):
        setofFiles = set(self.path.glob('*'))
        setofFiles.remove(self.runPath)
        setofFiles.remove(self.rootParametersFile)
        [setofFiles.remove(p) for p in initPaths]
        for f in setofFiles:
            filestr = str(f)
            copy(filestr, str(launchPath))

    def _initFiles(self, launchPath):
        listofTemplates = list(self.path.glob('*_t.*'))
        for template in listofTemplates:
            outputFile = launchPath / template.name.replace('_t','')
            prepro(self.newParametersFile, template, outputFile)
        return listofTemplates


    def _modifyParameters(self, launchPath):

        # Convert to list so it can be rendered in the yaml file
        # Numpy arrays are not supported
        x = list(self.x)

        newValuesDict = dict(zip(self.dv, x))

        with self.rootParametersFile.open('r') as f:
            dic = yaml.load(f, Loader=loader)

        gen = (key for key in dic.keys() if key in newValuesDict)
        for key in gen:
	    value = newValuesDict[key]
	    # Convert numpy array of numpy floats to list of floats
	    if type(value) == np.ndarray: 
		value = [float(v) for v in value]
            dic[key] = value

        self.newParametersFile = launchPath / 'parameters.yaml'
        with  self.newParametersFile.open('w') as f:
            yaml.dump(dic, f, default_flow_style=False)


    def _createLaunchFolder(self):

        # Generate folder for the run
        listofFolders = list(self.runPath.glob(self.name+'-*'))
        if listofFolders: 
            lNumbers =  [int(str(a).split('-')[-1]) for a in listofFolders]
            number = max(lNumbers)+1
        else:
            number = 1
        dirName = self.name + '-' + str(number)
        launchPath = self.runPath  / dirName
        launchPath.mkdir()
        return launchPath
             

def prepro(paramFile, templateFile, resultFile):

    with paramFile.open('r') as stream:
        try:
            d = yaml.load(stream, Loader=loader)
        except yaml.YAMLError as exc:
            print(exc)            
    
    for key in d:
        if type(d[key]) == str:
            d[key]="'%s'" % d[key]
    
    templateParent = str(templateFile.parent)
    env = Environment(loader=FileSystemLoader(templateParent))
    template = env.get_template(templateFile.name)
    render = template.render(d)

    with resultFile.open('w') as f:
        f.write(render)


def flattenDict(d):
    resultDict = {}
    for key in d.keys():
        if isinstance(d[key] , dict):
            innerDict = flattenDict(d[key])
            tmpDict = {key+'-'+str(nkey):innerDict[nkey]  for nkey in innerDict.keys()}
            resultDict.update(tmpDict)
        else:
            resultDict[key] = d[key]

    return resultDict
