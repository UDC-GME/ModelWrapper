import numpy as np
from scipy.optimize import minimize
from ModelWrapper import ModelWrapper

model = ModelWrapper('models/3bar', ['A1', 'A2'])

# Other parameters
model.setParameters({'P': 1.0, 'L': 1.0})

objM = model.getFun('volume')
consList = model.getFun('stress')


def obj(x):
    result = objM(x)
    return result

# Maximun stress in each bar
sigmaM = 1


def cons1(x):
    return consList(x)[0] - sigmaM


def cons2(x):
    return consList(x)[1] - sigmaM


def cons3(x):
    return consList(x)[2] - sigmaM


cons = (
        {'type': 'ineq',
         'fun': cons1,
		 'jac': None,
         },
        {'type': 'ineq',
         'fun': cons2,
		 'jac': None,
         },
        {'type': 'ineq',
         'fun': cons3,
		 'jac': None,
         },
       )

x0 = np.array([0.1, 0.1])

options = {'ftol': 1e-6, 'disp': True, 'maxiter': 100, 'eps': 0.1}
res = minimize(obj, x0, method='SLSQP', jac = None, constraints=cons,
               options=options)
               

