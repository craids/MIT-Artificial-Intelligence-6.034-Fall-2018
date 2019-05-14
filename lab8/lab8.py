# MIT 6.034 Lab 8: Bayesian Inference
# Written by 6.034 staff

from nets import *


#### Part 1: Warm-up; Ancestors, Descendents, and Non-descendents ##############

def get_ancestors(net, var):
    "Return a set containing the ancestors of var"
    ancestors = set()
    for parent in net.get_parents(var):
        ancestors.add(parent)
        ancestors = ancestors.union(get_ancestors(net, parent))
    return ancestors

def get_descendants(net, var):
    "Returns a set containing the descendants of var"
    descendants = set()
    for parent in net.get_children(var):
        descendants.add(parent)
        descendants = descendants.union(get_descendants(net, parent))
    return descendants

def get_nondescendants(net, var):
    "Returns a set containing the non-descendants of var"
    nondescendants = set()
    descendants = get_descendants(net, var)
    for v in net.get_variables():
        if v not in descendants:
            nondescendants.add(v)
    nondescendants.remove(var)
    return nondescendants


#### Part 2: Computing Probability #############################################

def simplify_givens(net, var, givens):
    """
    If givens include every parent of var and no descendants, returns a
    simplified list of givens, keeping only parents.  Does not modify original
    givens.  Otherwise, if not all parents are given, or if a descendant is
    given, returns original givens.
    """
    sg = dict()
    pr = net.get_parents(var)
    dsc = get_descendants(net, var)
    g = set(givens.keys())
    if pr.issubset(g):
        for k in g.difference(pr):
            if k in dsc:
                return givens
        for k in g:
            if k in pr:
                sg.setdefault(k,givens[k])
        return sg
    return givens
    
def probability_lookup(net, hypothesis, givens=None):
    "Looks up a probability in the Bayes net, or raises LookupError"
    if givens is None:
        try:
            pr = net.get_probability(hypothesis)
            return pr
        except ValueError:
            raise LookupError
    g = simplify_givens(net, list(hypothesis)[0], givens)
    try:
        pr = net.get_probability(hypothesis, g)
        return pr
    except ValueError:
        raise LookupError

def probability_joint(net, hypothesis):
    "Uses the chain rule to compute a joint probability"
    variables = net.topological_sort()
    variables.reverse()
    conditionals = hypothesis.copy()
    pr= 1.0

    for v in variables:
        val = conditionals.pop(v)
        if conditionals == dict():
            term = probability_lookup(net, {v: val}, None)
        else:
            term = probability_lookup(net, {v: val}, conditionals)
        pr *= term
    return pr
    
def probability_marginal(net, hypothesis):
    "Computes a marginal probability as a sum of joint probabilities"
    joint_pr = net.combinations(net.get_variables(), hypothesis)
    pr = 0
    for jp in joint_pr:
        pr += probability_joint(net, jp)
    return pr

def probability_conditional(net, hypothesis, givens=None):
    "Computes a conditional probability as a ratio of marginal probabilities"
    if givens is None:
        return probability_marginal(net, hypothesis)
    for h in hypothesis:
        if h in givens:
            if hypothesis[h] != givens[h]:
                return 0
            
    num = probability_marginal(net, dict(hypothesis, **givens))
    denom = probability_marginal(net, givens)
    return num/denom
    
def probability(net, hypothesis, givens=None):
    "Calls previous functions to compute any probability"
    return probability_conditional(net, hypothesis, givens)


#### Part 3: Counting Parameters ###############################################

def number_of_parameters(net):
    """
    Computes the minimum number of parameters required for the Bayes net.
    """
    n = 0
    all_variables = net.get_variables()

    for v in all_variables:
        domain_v = len(net.get_domain(v)) - 1
        parents = net.get_parents(v)
        
        if len(parents) == 0:
            n += domain_v 
        else:
            s = 1
            for p in parents:
                s *= len(net.get_domain(p))
            n += domain_v * s
    return n


#### Part 4: Independence ######################################################

def is_independent(net, var1, var2, givens=None):
    """
    Return True if var1, var2 are conditionally independent given givens,
    otherwise False. Uses numerical independence.
    """
    combinations = net.combinations([var1, var2])
    
    for c in combinations:
        if givens is None:
            prA = probability(net, {var1: c[var1]}, None)
            prA_B = probability(net, {var1: c[var1]}, {var2: c[var2]})

        else:
            prA = probability(net, {var1: c[var1]}, givens)
            prA_B = probability(net, {var1: c[var1]}, dict(givens, **{var2: c[var2]}))

        if not(approx_equal(prA, prA_B, epsilon=0.0000000001)):
            return False
    return True
    
def is_structurally_independent(net, var1, var2, givens=None):
    """
    Return True if var1, var2 are conditionally independent given givens,
    based on the structure of the Bayes net, otherwise False.
    Uses structural independence only (not numerical independence).
    """
    ancestors = get_ancestors(net, var1).union(get_ancestors(net, var2))
    if givens is not None:
        for g in givens:
            ancestors = get_ancestors(net, g).union(ancestors)
        givens_list = list(givens.keys())
    else:
        givens_list = list()
    
    anc = list(ancestors)
    new_net = net.subnet(ancestors.union(set([var1, var2] + givens_list)))

    for a in ancestors:
        children_a = new_net.get_children(a)
        anc.remove(a)
        for b in anc:
            children_b = new_net.get_children(b)
            if len(children_a.intersection(children_b)) != 0:
                new_net.link(a, b)

    new_net = new_net.make_bidirectional()
    if givens is not None:
        for g in givens:
            new_net.remove_variable(g)
        
    path = new_net.find_path(var1, var2)

    return True if path is None else False


#### SURVEY ####################################################################

NAME = 'Rayden Y Chia'
COLLABORATORS = 'none'
HOW_MANY_HOURS_THIS_LAB_TOOK = '3'
WHAT_I_FOUND_INTERESTING = 'propagating probabilities thru the net'
WHAT_I_FOUND_BORING = 'determining conditional independence'
SUGGESTIONS = 'none'
