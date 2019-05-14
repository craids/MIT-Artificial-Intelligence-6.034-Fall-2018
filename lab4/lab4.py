# MIT 6.034 Lab 4: Constraint Satisfaction Problems
# Written by 6.034 staff

from constraint_api import *
from test_problems import get_pokemon_problem


#### Part 1: Warmup ############################################################

def has_empty_domains(csp) :
    """Returns True if the problem has one or more empty domains, otherwise False"""
    return list() in csp.domains.values()

def check_all_constraints(csp) :
    """Return False if the problem's assigned values violate some constraint,
    otherwise True"""
    asgn = csp.assignments
    c = csp.get_all_constraints()
    for constr in c:
        if (constr.var1 in asgn) and (constr.var2 in asgn):
            if not constr.constraint_fn(asgn[constr.var1], asgn[constr.var2]):
                return False
    return True


#### Part 2: Depth-First Constraint Solver #####################################

def solve_constraint_dfs(problem) :
    """
    Solves the problem using depth-first search.  Returns a tuple containing:
    1. the solution (a dictionary mapping variables to assigned values)
    2. the number of extensions made (the number of problems popped off the agenda).
    If no solution was found, return None as the first element of the tuple.
    """
    count = 0
    agenda = [problem]

    while agenda:
        csp = agenda.pop(0)
        count += 1
        if not has_empty_domains(csp):
            if check_all_constraints(csp):
                if len(csp.unassigned_vars) == 0:
                    return (csp.assignments, count)
                else:
                    temp = list()
                    var = csp.pop_next_unassigned_var()
                    for val in csp.get_domain(var):
                        new_csp = csp.copy()
                        new_csp.set_assignment(var, val)
                        temp.append(new_csp)
                    temp.extend(agenda)
                    agenda = temp
    return (None, count)


# QUESTION 1: How many extensions does it take to solve the Pokemon problem
#    with DFS?

# Hint: Use get_pokemon_problem() to get a new copy of the Pokemon problem
#    each time you want to solve it with a different search method.

ANSWER_1 = 20


#### Part 3: Forward Checking ##################################################

def eliminate_from_neighbors(csp, var) :
    """
    Eliminates incompatible values from var's neighbors' domains, modifying
    the original csp.  Returns an alphabetically sorted list of the neighboring
    variables whose domains were reduced, with each variable appearing at most
    once.  If no domains were reduced, returns empty list.
    If a domain is reduced to size 0, quits immediately and returns None.
    """
    dom = dict()
    csp2 = csp.copy()
    for nb in csp.get_neighbors(var):
        c = csp.constraints_between(nb, var)
        if len(c) > 1:
            csp.set_domain(nb,list())
            return None
        else:
            for val1 in csp.get_domain(nb):
                count = 0
                for val2 in csp.get_domain(var):
                    if not c[0].check(val1,val2):
                        count += 1
                if count == len(csp.get_domain(var)):
                    csp2.eliminate(nb,val1)
                    csp.set_domain(nb,csp2.get_domain(nb))
                    if len(csp.get_domain(nb)) == 0:
                        return None
                    dom.setdefault(nb)
    return sorted(dom.keys())

# Because names give us power over things (you're free to use this alias)
forward_check = eliminate_from_neighbors

def solve_constraint_forward_checking(problem) :
    """
    Solves the problem using depth-first search with forward checking.
    Same return type as solve_constraint_dfs.
    """
    if has_empty_domains(problem):
        return None, 1
    count = 0
    agenda = [problem]
    while len(agenda) > 0:
        p = agenda.pop(0)
        count += 1
        if not has_empty_domains(p) and check_all_constraints(p):
            uns = p.pop_next_unassigned_var()
            if uns is None:
                return (p.assignments,count)
            cop = list()
            for val in p.get_domain(uns):
                csp = p.copy().set_assignment(uns,val)
                forward_check(csp,uns)
                cop.append(csp)
            cop.extend(agenda)
            agenda = cop
    return (None,count)


# QUESTION 2: How many extensions does it take to solve the Pokemon problem
#    with DFS and forward checking?

ANSWER_2 = 9


#### Part 4: Domain Reduction ##################################################

def domain_reduction(csp, queue=None) :
    """
    Uses constraints to reduce domains, propagating the domain reduction
    to all neighbors whose domains are reduced during the process.
    If queue is None, initializes propagation queue by adding all variables in
    their default order. 
    Returns a list of all variables that were dequeued, in the order they
    were removed from the queue.  Variables may appear in the list multiple times.
    If a domain is reduced to size 0, quits immediately and returns None.
    This function modifies the original csp.
    """
    popped = list()
    if queue is None:
        queue = csp.get_all_variables()
    while queue:
        var = queue.pop(0)
        popped.append(var)
        elim = eliminate_from_neighbors(csp,var)
        if elim:
            for neighbor in elim:
                if neighbor not in queue:
                    queue.append(neighbor)
        if elim is None:
            return None
    return popped


# QUESTION 3: How many extensions does it take to solve the Pokemon problem
#    with DFS (no forward checking) if you do domain reduction before solving it?

ANSWER_3 = 6


def solve_constraint_propagate_reduced_domains(problem) :
    """
    Solves the problem using depth-first search with forward checking and
    propagation through all reduced domains.  Same return type as
    solve_constraint_dfs.
    """
    if has_empty_domains(problem):
        return (None, 1)
    count = 0
    agenda = [problem]
    while len(agenda) > 0:
        p = agenda.pop(0)
        count += 1
        if not has_empty_domains(p) and check_all_constraints(p):
            uns = p.pop_next_unassigned_var()
            if uns is None:
                return (p.assignments,count)
            cop = list()
            for val in p.get_domain(uns):
                csp = p.copy().set_assignment(uns,val)
                domain_reduction(csp,[uns])
                cop.append(csp)
            cop.extend(agenda)
            agenda = cop
    return (None,count)


# QUESTION 4: How many extensions does it take to solve the Pokemon problem
#    with forward checking and propagation through reduced domains?

ANSWER_4 = 7


#### Part 5A: Generic Domain Reduction #########################################

def propagate(enqueue_condition_fn, csp, queue=None) :
    """
    Uses constraints to reduce domains, modifying the original csp.
    Uses enqueue_condition_fn to determine whether to enqueue a variable whose
    domain has been reduced. Same return type as domain_reduction.
    """
    if queue is None:
        queue = csp.get_all_variables()[:]
    popped = list()
    while queue:
        var = queue.pop(0)
        popped.append(var)
        for v in csp.variables:
            for constr in csp.constraints_between(var, v):
                v_domain = csp.get_domain(v)[:]
                for v_val in v_domain:
                    num_var_values = len(csp.get_domain(var))
                    count = 0
                    for val in csp.get_domain(var):
                        if not constr.check(val, v_val):
                            count += 1
                    if count is num_var_values:
                        csp.eliminate(v, v_val)
                        if len(csp.get_domain(v)) is 0:
                            return None
                        if not v in queue:
                            if enqueue_condition_fn(csp, v):
                                queue.append(v)
    return popped


def condition_domain_reduction(csp, var) :
    """Returns True if var should be enqueued under the all-reduced-domains
    condition, otherwise False"""
    return True

def condition_singleton(csp, var) :
    """Returns True if var should be enqueued under the singleton-domains
    condition, otherwise False"""
    return len(csp.get_domain(var)) == 1

def condition_forward_checking(csp, var) :
    """Returns True if var should be enqueued under the forward-checking
    condition, otherwise False"""
    return False


#### Part 5B: Generic Constraint Solver ########################################

def solve_constraint_generic(problem, enqueue_condition=None) :
    """
    Solves the problem, calling propagate with the specified enqueue
    condition (a function). If enqueue_condition is None, uses DFS only.
    Same return type as solve_constraint_dfs.
    """
    if has_empty_domains(problem):
        return (None, 1)
    count = 0
    agenda = [problem]
    while len(agenda) > 0:
        p = agenda.pop(0)
        count += 1
        if not has_empty_domains(p) and check_all_constraints(p):
            uns = p.pop_next_unassigned_var()
            if uns is None:
                return (p.assignments,count)
            cop = list()
            for val in p.get_domain(uns):
                csp = p.copy().set_assignment(uns,val)
                if enqueue_condition != None:
                    propagate(enqueue_condition, csp,[uns])
                cop.append(csp)
            cop.extend(agenda)
            agenda = cop
    return (None,count)

# QUESTION 5: How many extensions does it take to solve the Pokemon problem
#    with forward checking and propagation through singleton domains? (Don't
#    use domain reduction before solving it.)

ANSWER_5 = 8


#### Part 6: Defining Custom Constraints #######################################

def constraint_adjacent(m, n) :
    """Returns True if m and n are adjacent, otherwise False.
    Assume m and n are ints."""
    return n in [m-1, m+1]

def constraint_not_adjacent(m, n) :
    """Returns True if m and n are NOT adjacent, otherwise False.
    Assume m and n are ints."""
    return not constraint_adjacent(m, n)

def all_different(variables) :
    """Returns a list of constraints, with one difference constraint between
    each pair of variables."""
    cons = list()
    for i in range(len(variables)-1):
        for j in range(len(variables)-i-1):
            cons.append(Constraint(variables[i],variables[i+j+1],constraint_different))
    return cons


#### SURVEY ####################################################################

NAME = "Rayden Y Chia"
COLLABORATORS = "nobody"
HOW_MANY_HOURS_THIS_LAB_TOOK = "16"
WHAT_I_FOUND_INTERESTING = "nothing much"
WHAT_I_FOUND_BORING = "redoing same algorithm in different styles"
SUGGESTIONS = ""
