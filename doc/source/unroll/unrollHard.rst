.. _unrollHard:

Hard Problem
============

Now we turn to a harder problem that does not have a one to one mapping between all the transitions and the terms in the ODEs.  We use the model in :func:`Influenza_SLIARN`, defined by 

.. math::
    \frac{dS}{dt} &= -S \beta (I + \delta A) \\    
    \frac{dL}{dt} &= S \beta (I + \delta A) - \kappa L \\  
    \frac{dI}{dt} &= p \kappa L - \alpha I \\
    \frac{dA}{dt} &= (1 - p) \kappa L - \eta A \\
    \frac{dR}{dt} &= f \alpha I + \eta A \\
    \frac{dN}{dt} &= -(1 - f) \alpha I. 

The outflow of state **L**, :math:`\kappa L`, is composed of two transitions, one to **I** and the other to **A** but the ode of **L** only reflects the total flow going out of the state.  Same can be said for state **I**, where the flow :math:`\alpha I` goes to both **R** and **N**.  Graphically, it is a rather simple process as shown below. 

.. graphviz::

	digraph SLIARD_Model {
		labelloc = "t";
	    label = "Original transitions";
		rankdir=LR;
		size="8"
		node [shape = circle];
		S -> L [ label = "-S&beta;(I + &delta;A)/N" ];
		L -> I [ label = "&kappa;Lp" ];
		L -> A [ label = "&kappa;L(1-p)" ];
		I -> R [ label = "&alpha;If" ];
		I -> D [ label = "&alpha;I(1-f)" ];
		A -> R [ label = "&eta;A" ];
	}

We slightly change the model by introducing a new state **D** to convert it into a closed system.  The combination of state **D** and **N** is a constant, the total population.  So we can remove **N** and this new system consist of six transitions.  We define them explicitly as ODEs and unroll them into transitions.

.. ipython::

    In [1]: from pygom import SimulateOdeModel, Transition, TransitionType

    In [1]: stateList = ['S', 'L', 'I', 'A', 'R', 'D']

    In [2]: paramList = ['beta', 'p', 'kappa', 'alpha', 'f', 'delta', 'epsilon', 'N']

    In [3]: odeList = [
       ...:            Transition(origState='S', equation='- beta*S/N*(I + delta*A)', transitionType=TransitionType.ODE),
       ...:            Transition(origState='L', equation='beta*S/N*(I + delta*A) - kappa*L', transitionType=TransitionType.ODE),
       ...:            Transition(origState='I', equation='p*kappa*L - alpha*I', transitionType=TransitionType.ODE),
       ...:            Transition(origState='A', equation='(1 - p)*kappa * L - epsilon*A', transitionType=TransitionType.ODE),
       ...:            Transition(origState='R', equation='f*alpha*I + epsilon*A', transitionType=TransitionType.ODE),
       ...:            Transition(origState='D', equation='(1 - f)*alpha*I', transitionType=TransitionType.ODE) ]

    In [4]: ode = SimulateOdeModel(stateList, paramList, odeList=odeList)

    In [5]: ode.getTransitionMatrix()

    In [6]: ode2 = ode.returnObjWithTransitionsAndBD()

    In [7]: ode2.getTransitionMatrix()
    
    In [8]: ode2.getOde()

After unrolling the odes, we have the following transition graph

.. ipython::
    
    @savefig sir_unrolled_transition_graph_hard.png
    In [1]: ode2.getTransitionGraph()
    
    In [2]: plt.close()
    
    In [3]: print(sum(ode.getOde() - ode2.getOde()).simplify()) # difference

which is exactly the same apart from slightly weird arrangement of symbols in some of the equations.  The last line with a value of zero also reaffirms the result.