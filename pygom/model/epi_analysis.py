import sympy

from .stochastic import SimulateOdeModel

def getDFE(ode, diseaseState):
    '''
    Returns the disease free equilibrium from an ode object

    Parameters
    ----------
    ode: :class:`BaseOdeModel`
        a class object from pygom
    diseaseState: array like
        name of the disease states
    
    Returns
    -------
    e: array like
        disease free equilibrium

    References
    ----------
    .. [1] Chapter 6, Mathematical Epidemiology, Lecture Notes in Mathematics,
           Brauer Fred, Springer 2008
    '''

    eqn = ode.getOde()
    index = ode.getStateIndex(diseaseState)
    states = [s for s in ode._iterStateList()]
    statesSubs = {states[i]:0 for i in index}
    eqn = eqn.subs(statesSubs)

    DFE = sympy.solve(eqn, states)
    for s in states:
        if s not in statesSubs.keys() and s not in DFE.keys():
            DFE.setdefault(s, 0)
            # if s not in DFE.keys():
            #     DFE.setdefault(s, 0)
    return DFE

def getR0(ode, diseaseState):
    '''
    Returns the basic reproduction number, in symbolic form when
    the parameter values are not available

    Parameters
    ----------
    ode: :class:`BaseOdeModel`
        a class object from pygom
    diseaseStateIndex: array like
        name of the disease states
    
    Returns
    -------
    e: array like
        R0

    See Also
    --------
    :func:`getDiseaseProgressionMatrices`, :func:`getR0GivenMatrix`

    References
    ----------
    .. [1] Chapter 6, Mathematical Epidemiology, Lecture Notes in Mathematics,
           Brauer Fred, Springer 2008
    '''

    F, V = getDiseaseProgressionMatrices(ode, diseaseState)
    index = ode.getStateIndex(diseaseState)
    e = getR0GivenMatrix(F, V)
    DFE = getDFE(ode, diseaseState)
    e = [eig.subs(DFE) for eig in e]
    if ode.getParameters() is not None:
        e = [eig.subs(ode.getParameters()) for eig in e]

    e = filter(lambda x: sympy.Integer(-1) not in x.args, e)
    return (e if len(e) > 1 else e[0])

def getR0GivenMatrix(F, V, diseaseState=None):
    '''
    Returns the symbolic form of the basic reproduction number

    Parameters
    ----------
    F: :class:`sympy.Matrices`
        secondary infection rates        
    V: :class:`sympy.Matrices`
        disease progression rates
    diseaseState: list like, optional
        list of the disease state as :class:`sympy.Symbol`.  Defaults
        to None which assumes that F,V had been differentiated
    
    Returns
    -------
    e: :class:`sympy.Matrices`
        the eigenvalues of FV^{-1} for the disease states

    See Also
    --------
    :func:`getDiseaseProgressionMatrices`, :func:`getR0`

    References
    ----------
    .. [1] Chapter 6, Mathematical Epidemiology, Lecture Notes in Mathematics,
           Brauer Fred, Springer 2008
    '''

    if diseaseState is None:
        dF = F
        dV = V
    else:
        dF = F.jacobian(stateList)
        dV = F.jacobian(stateList)

    K = dF * dV.inv()
    e = K.eigenvals().keys()
    e = filter(lambda x: x!= 0, e)
    return e

def getDiseaseProgressionMatrices(ode, diseaseState, diff=True):
    '''
    Returns (F,V), the secondary infection rates and disease progression rate
    respectively.

    Parameters
    ----------
    ode: :class:`BaseOdeModel`
        an ode class in pygom
    diseaseStates: array like
        the name of the disease states
    diff: bool, optional
        if the first derivative of the matrices are return, defaults to true
    
    Returns
    -------
    (F, V): tuple
        the progression matrices

    References
    ----------
    .. [1] Chapter 6, Mathematical Epidemiology, Lecture Notes in Mathematics,
           Brauer Fred, Springer 2008
    '''
    diseaseIndex = ode.getStateIndex(diseaseState)
    stateList = list()
    for i, s in enumerate(ode._iterStateList()):
        if i in diseaseIndex:
            stateList.append(s)
    n = len(diseaseIndex)

    FList = list()
    for t in ode.getTransitionList():
        orig = _getSingleStateName(t.getOrigState())
        dest = _getSingleStateName(t.getDestState())
        # if hasattr(orig, '__iter__'):
        #     orig = orig[0] if len(orig) == 1 else None
        # if hasattr(dest, '__iter__'):
        #     dest = dest[0] if len(dest) == 1 else None
        # if isinstance(orig, (str, sympy.Symbol)) and isinstance(dest, (str, sympy.Symbol)):
        if isinstance(orig, str) and isinstance(dest, str):
            if orig not in diseaseState and dest in diseaseState:
                FList.append(t)

    ode2 = SimulateOdeModel(ode.getStateList(), 
                            ode.getParamList(), 
                            transitionList=FList)

    F = ode2.getOde().row(diseaseIndex)
    V = F - ode.getOde().row(diseaseIndex)

    if diff:
        dF = F.jacobian(stateList)
        dV = V.jacobian(stateList)
        # dF = sympy.zeros(n,n)
        # dV = sympy.zeros(n,n)
        # for j, s in enumerate(ode._iterStateList()):
        #     if j in index:
        #         for i, Fi in enumerate(F):
        #             dF[i,diseaseIndex.index(j)] = sympy.diff(Fi, s)
        #             dV[i,diseaseIndex.index(j)] = sympy.diff(V[i], s)
        return dF, dV
    else:
        return F,V


def _getSingleStateName(state):
    if hasattr(state, '__iter__'):
        state = state[0] if len(state) == 1 else None
    if isinstance(state, str):
        return state
    elif isinstace(state, sympy.Symbol):
        return str(state)
    else:
        return None