.. _bvpSimple:

*******************************
Solving Boundary Value Problems
*******************************

In addition to finding solutions for an IVP and estimate the unknown parameters, this package also allows you to solve BVP with a little bit of imagination.  Here, we are going to show how a BVP can be solved by treating it as a parameter estimation problem.  Essentially, a shooting method where the first boundary condition defines the initial condition of an IVP and the second boundary condition is an observation.  Two examples, both from MATLAB [1], will be shown here.

Simple model 1
==============

We are trying to find the solution to the second order differential equation

.. math::
    \nabla^{2} y + |y| = 0
    
subject to the boundary conditions :math:`y(0) = 0` and :math:`y(4) = -2`.  Convert this into a set of first order ODE

.. math::

    \frac{d y_{0}}{dt} &= y_{1} \\
    \frac{d y_{1}}{dt} &= -|y_{0}|
    
using an auxiliary variable :math:`y_{1} = \nabla y` and :math:`y_{0} = y`.  Setting up the system below

.. ipython::

    In [1]: from pygom import Transition, TransitionType, OperateOdeModel, SquareLoss

    In [1]: import matplotlib.pyplot as plt

    In [2]: stateList = ['y0', 'y1']

    In [3]: paramList = []
    
    In [4]: ode1 = Transition(origState='y0',
       ...:                   equation='y1',
       ...:                   transitionType=TransitionType.ODE)

    In [5]: ode2 = Transition(origState='y1', 
       ...:                   equation='-abs(y0)',
       ...:                   transitionType=TransitionType.ODE)
                              
    In [6]: model = OperateOdeModel(stateList,
       ...:                         paramList,
       ...:                         odeList=[ode1, ode2])    

    In [7]: model.getOde()
    
We check that the equations are correct before proceeding to set up our loss function.  
    
.. ipython::

    In [1]: import numpy
    
    In [2]: from scipy.optimize import minimize

    In [2]: initialState = [0.0, 1.0]

    In [3]: t = numpy.linspace(0, 4, 100)

    In [4]: model = model.setInitialValue(initialState, t[0])
    
    In [5]: solution = model.integrate(t[1::])
    
    In [6]: f = plt.figure()
    
    @savefig bvp1_random_guess_plot.png
    In [7]: model.plot()
    
    In [8]: plt.close()

Setting up the second boundary condition :math:`y(4) = -2` is easy, because that is just a single observation attached to the state :math:`y_{1}`.  Enforcing the first boundary condition require us to set it as the initial condition.  Because the condition only states that :math:`y(0) = 0`, the starting value of the other state :math:`y_1` is free.  We let our loss object know that it is free through the targetState input argument.
    
.. ipython::

    In [7]: theta = [0.0]
    
    In [8]: obj = SquareLoss(theta=theta, 
       ...:                  ode=model, 
       ...:                  x0=initialState, 
       ...:                  t0=t[0], 
       ...:                  t=t[-1], 
       ...:                  y=[-2],
       ...:                  stateName=['y0'],
       ...:                  targetState=['y1'])
                             
    In [9]: thetaHat = minimize(fun=obj.costIV, x0=[0.0])
    
    In [9]: print(thetaHat)
    
    In [9]: model = model.setInitialValue([0.0] + thetaHat['x'].tolist(), t[0])
    
    In [5]: solution = model.integrate(t[1::])
    
    In [6]: f = plt.figure()
    
    @savefig bvp1_solution_plot.png
    In [7]: model.plot()
    
    In [7]: plt.close()
    
We are going to visualize the solution, and also check the boundary condition.  The first became our initial condition, so it is always satisfied and only the latter is of concern, which is zero (subject to numerical error) from thetaHat.  

Simple model 2
==============

Our second example is different as it involves an actual parameter and also time.  We have the Mathieu's Equation

.. math::

    \nabla^{2} y + \left(p - 2q \cos(2x)\right)y = 0

and the aim is to compute the fourth eigenvalue :math:`q=5`.  There are three boundary conditions

.. math::

    \nabla y(0) = 0, \quad \nabla y(\pi) = 0, \quad y(0) = 1

and we aim to solve it by converting it to a first order ODE and tackle it as an IVP.  As our model object does not allow the use of the time component in the equations, we introduce a anxiliary state :math:`\tau` that replaces time :math:`t`.  Rewrite the equations using :math:`y_{0} = y, y_{1} = \nabla y` and define our model as

.. ipython::

    In [1]: stateList = ['y0', 'y1', 'tau']

    In [2]: paramList = ['p']

    In [3]: ode1 = Transition('y0', 'y1', TransitionType.ODE)

    In [4]: ode2 = Transition('y1', '-(p - 2*5*cos(2*tau))*y0', TransitionType.ODE)

    In [5]: ode3 = Transition('tau', '1', TransitionType.ODE)

    In [6]: model = OperateOdeModel(stateList,paramList,odeList=[ode1, ode2, ode3])

    In [7]: theta = [1.0, 1.0, 0.0]

    In [7]: p = 15.0

    In [7]: t = numpy.linspace(0, numpy.pi)

    In [8]: model = model.setParameters([('p',p)]).setInitialValue(theta,t[0])

    In [8]: solution = model.integrate(t[1::])
    
    In [9]: f = plt.figure()

    @savefig bvp2_random_guess_plot.png
    In [9]: model.plot()

    In [7]: plt.close()

Now we are ready to setup the estimation.  Like before, we setup the second boundary condition by pretending that it is an observation.  We have all the initial conditions defined by the first boundary condition

.. ipython::

    In [1]: obj = SquareLoss(15.0, model, x0=[1.0, 0.0, 0.0], t0=0.0, t=numpy.pi, y=0.0, stateName='y1')

    In [2]: xhatObj = minimize(obj.cost,[15])

    In [3]: print(xhatObj)

    In [4]: model = model.setParameters([('p',xhatObj['x'][0])]).setInitialValue([1.0, 0.0, 0.0], t[0])

    In [5]: solution = model.integrate(t[1::])
    
    In [6]: f = plt.figure()

    @savefig bvp2_solution_plot.png
    In [7]: model.plot()
    
    In [8]: plt.close()

The plot of the solution shows the path that satisfies all boundary condition.  The last subplot is time which obvious is redundant here but the :meth:`OperateOdeModel.plot` method is not yet able to recognize the time component.  Possible speed up can be achieved through the use of derivative information or via root finding method that tackles the gradient directly, instead of the cost function.

**Reference**

[1] http://uk.mathworks.com/help/matlab/ref/bvp4c.html
