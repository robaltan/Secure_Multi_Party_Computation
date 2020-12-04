# secure multi-party computation, semi-honest case, distributed, v1
# naranker dulay, dept of computing, imperial college, october 2020
# modified by: Altan Tutar, Han Yuan

import math


# Circuit below to evalute
CIRCUIT = 3

# Gate types
INP, ADD, MUL, SUB = (0,1,2,3)

# Define MPC Function as an addition/multiplication circuit. INPut gates 
# precede ADD/MUL gates. ADD/MUL gates are defined in evaluation order. 
# By convention the final wire is considerd the circuit's output wire.

if CIRCUIT == 1: 	# example in Smart
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME  = 35742549198872617291353508656626642567
  # degree of polynominal - T in slides
  DEGREE = 15

  PRIVATE_VALUES = {1:580000486500, 2:656194536014, 3:354446189471, 4:220376453071, 5:235546455948, 6:410351199687}

  def function(x):	# function being evaluated by parties
    return (x[1]*x[2] + x[3]*x[4] + x[5]*x[6]) % PRIME

  GATES = {
    1:  (INP, 7,1),
    2:  (INP, 7,2),
    3:  (INP, 8,1),
    4:  (INP, 8,2),
    5:  (INP, 9,1),
    6:  (INP, 9,2),
    7:  (MUL, 10,1),
    8:  (MUL, 10,2),
    9:  (MUL, 11,1),
    10: (ADD, 11,2),
    11: (ADD, 12,1),  	# (12,1) is circuit output wire
  }

elif CIRCUIT == 2:	# factorial tree for 2^n parties
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME = 101
  # PRIME = 1_000_000_007
  # PRIME = 35742549198872617291353508656626642567  # Large Bell prime

  # degree of polynominal - T in slides
  DEGREE = 1

  INPUTS = 2 ** 5
  PRIVATE_VALUES = {k: k for k in range(1, INPUTS+1)}

  def function(x):	# function being evaluated by parties
    product = 1
    for value in x.values(): product = (product * value) % PRIME
    return product

  GATES = {}

  def tree(next_gate, n_gates):
    global GATES
    if n_gates >= 1:
      kind = INP if next_gate == 1 else MUL
      output_gate = next_gate + n_gates
      last_gate = output_gate - 1
      for g in range(next_gate, output_gate, 2):
        GATES[g]   = (kind, output_gate, 1)
        if g < last_gate:
          GATES[g+1] = (kind, output_gate, 2)
        output_gate += 1
      tree(next_gate + n_gates, n_gates // 2)

  tree(1, INPUTS)

# ___________________________________________________________________________
elif CIRCUIT == 3:	# add your circuit(s) here
  # prime number
  PRIME = 101

  # values to be used
  PRIVATE_VALUES = {1:580000486500, 2:656194536014, 3:354446189471, 4:220376453071, 5:235546455948, 6:410351199687}
  
  # degree of the polynomial
  DEGREE = int(len(PRIVATE_VALUES) / 2 - 1)

  def function(x): # function being evaluated by parties
    return ((x[4] - x[1]) + (x[5] - x[2]) + (x[6] - x[3])) % PRIME

  GATES = {
    1:  (INP, 7,2),
    2:  (INP, 8,2),
    3:  (INP, 9,2),
    4:  (INP, 7,1),
    5:  (INP, 8,1),
    6:  (INP, 9,1),
    7:  (SUB, 10, 1),
    8:  (SUB, 10, 2),
    9:  (SUB, 11, 2),
    10: (ADD, 11, 1),
    11: (ADD, 12, 1)
  }
# ___________________________________________________________________________
elif CIRCUIT == 4: # DEBUG: simple ADD circuit for debug
  PRIME = 101
  DEGREE = 1

  PRIVATE_VALUES = {1: 10000, 2: 238582345, 3: 13}

  def function(x):
    return (x[1] + x[2] + x[3]) % PRIME

  GATES = {
    1: (INP, 4, 1),
    2: (INP, 4, 2),
    3: (INP, 5, 2),
    4: (ADD, 5, 1),
    5: (ADD, 6, 1)
  }

# ___________________________________________________________________________
elif CIRCUIT == 5: # DEBUG: simple MUL circuit for debug
  PRIME = 101
  DEGREE = 1

  PRIVATE_VALUES = {1: 357235, 2: 3352, 3: 13}

  def function(x):
    return x[1] * x[2] * x[3] % PRIME

  GATES = {
    1: (INP, 4, 1),
    2: (INP, 4, 2),
    3: (INP, 5, 2),
    4: (MUL, 5, 1),
    5: (MUL, 6, 1)
  }

# ___________________________________________________________________________
elif CIRCUIT == 6:
  PRIME = 100_003
  x = 2
  y = 100
  DEGREE = int(y / 2 - 1)
  def function(x):
    prod = 0
    for val in x.values():
      prod += val

    return prod % PRIME

  PRIVATE_VALUES = {i: x for i in range(1, y + 1)}
  GATES = {}
  for i, v in PRIVATE_VALUES.items():
    GATES[i] = (INP, y + i - 1, 2)

  GATES[1] = (INP, y + 1, 1)
  for i in range(y + 1, y * 2):
    GATES[i] = (ADD, i + 1, 1)

# ___________________________________________________________________________
elif CIRCUIT == 7:
  # prime number
  PRIME = 1_000_003

  # values to be used
  x = 7
  y = 10
  if x == 0:
    PRIVATE_VALUES = {1: 1, 2: 1}
  elif x == 1:
    PRIVATE_VALUES = {1: y, 2: 1} # just check for validation, it must be y**0 = 1
  else:
    PRIVATE_VALUES = {k: y for k in range(1, x**2+1)}
  
  # degree of the polynomial
  DEGREE = int(x / 2 - 1)

  def function(x): # function being evaluated by parties
    # calculate y**(x**(2))
    product = 1
    for k in x.values():
      product = (product * k)  % PRIME

    return product
  

  def build_gates(x):
    GATES = {}
    number_of_inputs = x ** 2 

    # firstly, build the input gates
    for i in range(1, number_of_inputs + 1):
      if i == 1:
        GATES[i] = (INP, number_of_inputs + 1, 1)
      elif i == 2:
        GATES[i] = (INP, number_of_inputs + 1, 2)
      else:
        GATES[i] = (INP, i + number_of_inputs - 1, 2)
    # now, build the input gates
    for i in range(number_of_inputs + 1, number_of_inputs * 2):
      GATES[i] = (MUL, i + 1, 1)
    
    return GATES

  GATES = build_gates(x)

# ___________________________________________________________________________
elif CIRCUIT == 8: # DEBUG: simple ADD circuit for debug
  PRIME = 101
  DEGREE = 1

  PRIVATE_VALUES = {1: 39, 2: 17, 3: 13}

  def function(x):
    return (x[1] - x[2] - x[3]) % PRIME

  GATES = {
    1: (INP, 4, 1),
    2: (INP, 4, 2),
    3: (INP, 5, 2),
    4: (SUB, 5, 1),
    5: (SUB, 6, 1)
  }

# ___________________________________________________________________________
# elif CIRCUIT == 9:
#   PRIME = 100_003
#   x = 20
#   y = 20
#   DEGREE = int(y / 2 - 1)
#   def function(x):
#     prod = 1
#     for val in x.values():
#       prod *= val

#     return prod % PRIME

#   PRIVATE_VALUES = {i: x for i in range(1, y + 1)}
#   GATES = {}
#   for i, v in PRIVATE_VALUES.items():
#     GATES[i] = (INP, y + i - 1, 2)

#   GATES[1] = (INP, y + 1, 1)
#   for i in range(y + 1, y * 2):
#     GATES[i] = (MUL, i + 1, 1)

#   # print(GATES)


# true function result - used to check result from MPC circuit
FUNCTION_RESULT = function(PRIVATE_VALUES)
N_GATES     = len(GATES)
N_PARTIES   = len(PRIVATE_VALUES)
# print(PRIVATE_VALUES)
ALL_PARTIES = range(1, N_PARTIES+1)
ALL_DEGREES = range(1, DEGREE+1)

assert PRIME > N_PARTIES, "Prime > N failed :-("
assert 2*DEGREE < N_PARTIES, "2T < N failed :-("

# Various Primes 
# PRIME = 11
# PRIME = 101
# PRIME = 1_009
# PRIME = 10_007
# PRIME = 100_003
# PRIME = 1_000_003 
# PRIME = 1_000_000_007
# PRIME = 35742549198872617291353508656626642567  # Large Bell prime


