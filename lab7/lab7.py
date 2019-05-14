# MIT 6.034 Lab 7: Support Vector Machines
# Written by 6.034 staff
import math
from svm_data import *
from functools import reduce
INF = float('inf')

#### Part 1: Vector Math #######################################################

def dot_product(u, v):
    """Computes the dot product of two vectors u and v, each represented 
    as a tuple or list of coordinates. Assume the two vectors are the
    same length."""
    return sum([a*b for a,b in zip(list(u),list(v))])

def norm(v):
    """Computes the norm (length) of a vector v, represented 
    as a tuple or list of coords."""
    return math.sqrt(dot_product(v,v))


#### Part 2: Using the SVM Boundary Equations ##################################

def positiveness(svm, point):
    """Computes the expression (w dot x + b) for the given Point x."""
    return dot_product(svm.w, point.coords) + svm.b

def classify(svm, point):
    """Uses the given SVM to classify a Point. Assume that the point's true
    classification is unknown.
    Returns +1 or -1, or 0 if point is on boundary."""
    p = positiveness(svm, point)
    return 1 if p > 0 else -1 if p < 0 else 0

def margin_width(svm):
    """Calculate margin width based on the current boundary."""
    return 2 / norm(svm.w)

def check_gutter_constraint(svm):
    """Returns the set of training points that violate one or both conditions:
        * gutter constraint (positiveness == classification, for support vectors)
        * training points must not be between the gutters
    Assumes that the SVM has support vectors assigned."""
    violators = set()
    diff = set()
    for v in svm.support_vectors:
        if v.classification != positiveness(svm, v):
            violators.add(v)
        diff.add(v)
    for p in svm.training_points:
        if p not in diff and positiveness(svm, p) < 1 and positiveness(svm, p) > -1:
                violators.add(p)
    return violators


#### Part 3: Supportiveness ####################################################

def check_alpha_signs(svm):
    """Returns the set of training points that violate either condition:
        * all non-support-vector training points have alpha = 0
        * all support vectors have alpha > 0
    Assumes that the SVM has support vectors assigned, and that all training
    points have alpha values assigned."""
    points = set()
    [points.add(p) for p in svm.training_points if (p in svm.support_vectors and p.alpha <= 0) or (p not in svm.support_vectors and p.alpha != 0)]
    return points

def check_alpha_equations(svm):
    """Returns True if both Lagrange-multiplier equations are satisfied,
    otherwise False. Assumes that the SVM has support vectors assigned, and
    that all training points have alpha values assigned."""
    s = 0
    diff = set()
    for v in svm.support_vectors:
        s += v.classification*v.alpha
        diff.add(v)
    for p in svm.training_points:
        if p not in diff:
            s += p.classification * p.alpha
    vsum = [0]*len(p)
    for p in svm.training_points:
        vsum = vector_add(scalar_mult(p.classification*p.alpha,p),vsum)
    
    return s == 0 and vsum == svm.w


#### Part 4: Evaluating Accuracy ###############################################

def misclassified_training_points(svm):
    """Returns the set of training points that are classified incorrectly
    using the current decision boundary."""
    m = set()
    [m.add(p) for p in svm.training_points if classify(svm, p) != p.classification]
    return m


#### Part 5: Training an SVM ###################################################

def update_svm_from_alphas(svm):
    """Given an SVM with training data and alpha values, use alpha values to
    update the SVM's support vectors, w, and b. Return the updated SVM."""
    cas = check_alpha_signs(svm)
    [svm.support_vectors.remove(p) for p in cas if p in svm.support_vectors]
    w = [0,0]
    bm = INF 
    bp = -INF
    for p in svm.training_points:
        if p.alpha != 0:
            if p not in svm.support_vectors:
                svm.support_vectors.append(p)
            w = vector_add(w, scalar_mult(p.classification * p.alpha, p.coords))
    for p in svm.support_vectors:
        if p.classification == -1:
            bm = min(bm, p.classification - dot_product(w, p.coords))
        else:
            bp = max(bp, p.classification - dot_product(w, p.coords))
    return svm.set_boundary(w, (bm+bp)/2)


#### Part 6: Multiple Choice ###################################################

ANSWER_1 = 11
ANSWER_2 = 6
ANSWER_3 = 3
ANSWER_4 = 2

ANSWER_5 = ['A', 'D']
ANSWER_6 = ['A', 'B', 'D']
ANSWER_7 = ['A', 'B', 'D']
ANSWER_8 = []
ANSWER_9 = ['A', 'B', 'D']
ANSWER_10 = ['A', 'B', 'D']

ANSWER_11 = False
ANSWER_12 = True
ANSWER_13 = False
ANSWER_14 = False
ANSWER_15 = False
ANSWER_16 = True

ANSWER_17 = [1,3,6,8]
ANSWER_18 = [1,2,4,5,6,7,8]
ANSWER_19 = [1,2,4,5,6,7,8]

ANSWER_20 = 6


#### SURVEY ####################################################################

NAME = 'Rayden Y Chia'
COLLABORATORS = 'no one'
HOW_MANY_HOURS_THIS_LAB_TOOK = '5'
WHAT_I_FOUND_INTERESTING = 'svm usage'
WHAT_I_FOUND_BORING = 'not much'
SUGGESTIONS = 'nothing'
