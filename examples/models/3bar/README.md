# 3 Bar Truss

+ Static Analysis
+ Truss Elements

 File                                   | Contents    
 :-------------                         | :-------------
 [parameters.yaml](parameters.yaml)     | Yaml file with the parameters of the problem
 [analysis_t.comm](analysis_t.comm)     | Code Aster command file template for analysis
 [mesh_t.geo](mesh_t.geo)               | Gmsh geometry and mesh template
 [post_t.comm](post_t.comm)             | Code Aster command file template for postprocessing
 [analysis.export](analysis.export)     | Export file for the analysis
 [post.export](post.export)             | Export file for the postprocessing
 [Makefile](Makefile)                   | Makefile for running the analysis

## Model Description

Classical truss problem used to illustrate structural optimization

![](refs/3bar.png)

The initial defined parameters are the following:

Parameters   | Value
:----------  | :-------------
P            | 1 N
theta        | 45 degrees
E            | 2.1e9 N/m^2
nu           | 0.3
rho          | 7800 kg/m^3
L            | 1 m
A1           | 0.1 m^2
A2           | 0.1 m^2

## How to run it

To launch the study modify the `parameters.yaml` file and execute make:
```
$ make
```

A `results.json` file will be generated containing the volume and stresses of the bars.
