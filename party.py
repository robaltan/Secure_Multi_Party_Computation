"""
Implementation of the Multi-Party Case: Honest-but-Curious Adversaries by 
using Shamir's Secret Sharing.
Authors: Ricky Yuan, Altan Tutar
"""

# Import the debug library for printing log outputs
from log import debug
# Import the necessary functionalities for circuit implementation
from circuit import GATES, N_PARTIES, N_GATES, DEGREE, PRIME, INP, ADD, MUL, SUB, function
# Import random library for randomizing inputs
from random import randint

# Debug string prefix that is for debugging output
global_bgw_debug_string_prefix = f"<bgw_protocol>"

def get_poly_coefficients():
    """
    Randomly generate coefficients for a polynomial function of degree `DEGREE` 
    designated globally by the circuit script
    @return A list of coefficients, as requested.
    """
    # Create an empty array
    poly_coefficients = []
    for _ in range(DEGREE):
        # Append random integers onto polycoefficients with the max integer being the prime designated globally by the circuit script
        poly_coefficients.append(randint(0, PRIME)) 

    # Return randomly generated polynomial coefficients
    return poly_coefficients

def get_share_for_party(val, receiver_n, coeff):
    """
    Find the share for a given party with its party number and the polynomial function
    
    @param val: secret value.
    @receiver_n: the id for the receiving party.
    @coeff: coefficients describing the generated polynomial function.
    @return an array consists of the shares to be distributed to the each party.
    """
    share = val # P_n = S
    for i, c in enumerate(coeff):
        deg = i + 1 # Corresponding degree in the polynomial
        share += c * receiver_n ** deg # P_n += a_i * x ^ t

    return share

def generate_shares(val):
    """
    Given a private value, generate shares for each party involved where 
    the number of parties 'N_PARTIES' is designated globally by circuit script

    @param val: secret beheld by the current party.
    @return An array of size `n_parties` shares, with i-th element in this array being the share for the i-th party.
    """
    # Get the randomly-generated polynomial function for the client
    poly_coefficients = get_poly_coefficients()
    shares = {}
    for i in range(1, N_PARTIES + 1):
        # For each degree, get the corresponding share
        shares[i] = get_share_for_party(val, i, poly_coefficients)
    
    return shares
    
def bgw_protocol(party_n, private_value, network):
    """
    Runs BGW protocol for a given party. Generates shares to the each other party.
    Obtains all circuit outputs. Finds the 

    @param party_n: the party id of the current party.
    @param private_value: the secret value held by this party.
    @param network: network object in charge of sendeing and receiving messages.
    @return Function result.
    """
    # Debug output from this party
    this_party_debug_string = global_bgw_debug_string_prefix + f"[{party_n}] "
    debug(this_party_debug_string + f"init: {private_value}")

    # Generate shares for each party
    own_shares = generate_shares(private_value)
    debug(this_party_debug_string + f"STBS: {str(own_shares)}")

    # Progress through the circuit and obtain the output on the final wire
    output_wire_value = process_circuit(party_n, network, own_shares)

    # Send this party's circuit output to every other party
    for i in range(1, N_PARTIES + 1):
        network.send_share(output_wire_value, N_GATES + 1, i)

    # Obtain all circuit outputs
    circuit_outputs = get_all_circuit_outputs(network)
    debug(this_party_debug_string + "circuit_outputs: {}".format(str(circuit_outputs)))

    # Find P(0), found by using T+1 data points, where T is the degree of the polynomial
    # Output needs to be in module PRIME
    global_result = calculate_global_result(circuit_outputs) % PRIME

    debug(this_party_debug_string + "Global final circuit result: {}".format(global_result))
    return global_result

def send_own_shares_to_parties(gate_n, network, shares):
    """
    Sends shares to other parties in the protocol
    @param gate_n: where the party sends the shares to
    @network network: reference to the network object that can send and receive shares
    @shares: generated shares
    """
    # Send share for each of the input gates
    for i in range(1, N_PARTIES + 1):
        assert(GATES[i][0] == INP) # Make sure the gate entry is for the right party
        share_i = shares[i]
        network.send_share(share_i, gate_n, i)
        debug(global_bgw_debug_string_prefix + f"send_share: {i}, {share_i}", 2)

def get_all_circuit_outputs(network):
    """
    Receives all shares from every party on the output
    @param network: reference to the network object
    """
    circuit_outputs = {}
    # Obtain calculated value for everyone else
    for i in range(1, N_PARTIES + 1):
        # Receive shares from every party on the output
        circuit_outputs[i] = network.receive_share(i, N_GATES + 1)
    return circuit_outputs

def process_circuit(gate_n, network, own_shares):
    """
    Processeses the given circuit and returns the value on the given gate
    @param gate_n: the gate number where the party will send its share to
    @network: reference to the network object that can send and receive shares
    @own_shares: the set of shares that will be sent at the given gate_n
    """
    this_party_debug_string = global_bgw_debug_string_prefix + f"[{gate_n}] "

    # Send generated shares for the current party to all other parties
    send_own_shares_to_parties(gate_n, network, own_shares)

    wire_values = dict({})
    wire_predecessors = dict({})

    # Go through each gate and perform calculation / receive share
    for i in range(1, N_GATES + 1):
        gate_type, next_gate, next_in_order = GATES[i]
        if gate_type == INP:
            # If the gate is an input gate, wait for the share
            debug(this_party_debug_string + f"attempt to received_share: {i}", 2)
            output_value = network.receive_share(i, i)
            debug(this_party_debug_string + f"received_share: {i}", 2)
        elif gate_type == ADD:
            pred_1 = wire_values[wire_predecessors[i][0]]
            pred_2 = wire_values[wire_predecessors[i][1]]
            output_value = add_gate(pred_1, pred_2)
        elif gate_type == SUB:
            pred_1 = wire_values[wire_predecessors[i][0]]
            pred_2 = wire_values[wire_predecessors[i][1]]
            output_value = sub_gate(pred_1, pred_2)
        elif gate_type == MUL:
            pred_1 = wire_values[wire_predecessors[i][0]]
            pred_2 = wire_values[wire_predecessors[i][1]]
            output_value = mul_gate(pred_1, pred_2, i, network)
        else:
            raise Exception("Bad gate type")

        # Set the input values for the subsequent gate to this gate
        if next_gate not in wire_predecessors:
            wire_predecessors[next_gate] = [-1, -1]
        wire_predecessors[next_gate][next_in_order-1] = i # Storing predecessor gate ID
        wire_values[i] = output_value

    output_wire_id = wire_predecessors[N_GATES + 1][0]
    output_wire_value = wire_values[output_wire_id]
    debug(this_party_debug_string + "output_wire_value: " + str(output_wire_value))
    
    return output_wire_value

def calculate_global_result(circuit_outputs):
    """
    Returns the result of the circuit by interpolating the lagrange polynomial
    @param: circuit outputs: the set of received shares
    """
    deltas = {}
    for i in range(1, len(circuit_outputs) + 1):
        # For the first T datapoints, find delta_i
        delta_i = 1
        for j in range(1, len(circuit_outputs) + 1):
            if i != j:
                delta_i *= j / (j-i)
        deltas[i] = round(delta_i)

    debug(global_bgw_debug_string_prefix + f"delta: {str(deltas)}")
    global_result = 0
    for i in range(1, len(circuit_outputs) + 1):
        global_result += round(circuit_outputs[i] * deltas[i] % PRIME)
    
    return global_result

def add_gate(i_1, i_2):
    """
    Implements the add gate
    @param i_1: first number
    @param i_2: second number
    """
    return round((i_1 + i_2) % PRIME)

def sub_gate(i_1, i_2):
    return round((i_1 - i_2) % PRIME)

def mul_gate(i_1, i_2, gate_n, network):
    """
    Implements the multiplication gate
    @param i_1: first number
    @param i_2: second number 
    @gate_n: the number of the gate that has the multiplication gate
    @network: reference to the network object
    """
    d = i_1 * i_2
    debug(global_bgw_debug_string_prefix + f"{i_1, i_2, d}")
    own_shares = generate_shares(d)
    debug(global_bgw_debug_string_prefix + "own_shares: " + str(own_shares))
    # Send shares to other parties for multiplication
    send_own_shares_to_parties(gate_n, network, own_shares)
    # Receive shares from all parties for multiplication
    multiplication_gate_outputs = {} # keeps track of all shares from different parties
    for i in range(1, N_PARTIES + 1):
        multiplication_gate_outputs[i] = network.receive_share(i, gate_n)

    debug(global_bgw_debug_string_prefix + "multiplication_gate_outputs: " + str(multiplication_gate_outputs))
    mult_result = calculate_global_result(multiplication_gate_outputs)
    debug(global_bgw_debug_string_prefix + "mult_result: {}".format(mult_result))
    # Return the final result that was obtained by Lagrange polynomial interpolation
    return round(mult_result % PRIME)