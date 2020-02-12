# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Measurement calibration circuits. To apply the measurement mitigation
use the fitters to produce a filter.
"""

from qiskit import QuantumRegister, ClassicalRegister, \
    QuantumCircuit, QiskitError
from ...verification.tomography import count_keys


def complete_meas_cal(qubit_list=None, qr=None, cr=None, circlabel=''):
    """
    Return a list of measurement calibration circuits for the full
    Hilbert space.

    Each of the 2**n circuits creates a basis state

    Args:
        qubit_list(list[integer]): A list of qubits to perform the measurement correction on.
           If `None`, and qr is given then assumed to be performed over the entire
           qr. The calibration states will be labelled according to this ordering.

        qr(QuantumRegister): Quantum registers. If `None`, one is created.

        cr: (ClassicalRegister). Classical registers. If `None`, one is created.

        circlabel(string): A string to add to the front of circuit names for
            unique identification.

    Returns:
        A list of QuantumCircuit objects containing the calibration circuits.

        A list of calibration state labels.

    Additional Information:
        The returned circuits are named circlabel+cal_XXX
        where XXX is the basis state,
        e.g., cal_1001.

        Pass the results of these circuits to the CompleteMeasurementFitter
        constructor.

    Raises:
        QiskitError: if both qubit_list and qr are None.
    
    """

    if qubit_list is None and qr is None:
        raise QiskitError("Must give one of a qubit_list or a qr")

    # Create the registers if not already done
    if qr is None:
        qr = QuantumRegister(max(qubit_list)+1)

    if qubit_list is None:
        qubit_list = range(len(qr))

    nqubits = len(qubit_list)

    # labels for 2**n qubit states
    state_labels = count_keys(nqubits)

    cal_circuits, _ = tensored_meas_cal([qubit_list],
                                        qr, cr, circlabel)

    return cal_circuits, state_labels


def tensored_meas_cal(mit_pattern=None, qr=None, cr=None, circlabel=''):
    """
    Return a list of calibration circuits

    Args:
        mit_pattern (list of lists of integers): Qubits to perform the
            measurement correction on, divided to groups according to tensors.
            If `None` and qr is given then assumed to be performed over the entire
            qr as one group.

        qr (QuantumRegister): A quantum register. If `None`, one is created.

        cr (ClassicalRegister): A classical register. If `None`, one is created.

        circlabel(string): A string to add to the front of circuit names for
            unique identification.

    Returns:
        A list of two QuantumCircuit objects containing the calibration.
        
        circuits
        
        mit_pattern

    Additional Information:
        The returned circuits are named circlabel+cal_XXX
        where XXX is the basis state,
        e.g., cal_000 and cal_111.

        Pass the results of these circuits to the TensoredMeasurementFitter
        constructor.

    Raises:
        QiskitError: if both mit_pattern and qr are None.
        QiskitError: if a qubit appears more than once in mit_pattern.
        
    """

    if mit_pattern is None and qr is None:
        raise QiskitError("Must give one of mit_pattern or qr")

    qubits_in_pattern = []
    if mit_pattern is not None:
        for qubit_list in mit_pattern:
            for qubit in qubit_list:
                if qubit in qubits_in_pattern:
                    raise QiskitError("mit_pattern cannot contain \
                    multiple instances of the same qubit")
                qubits_in_pattern.append(qubit)

        # Create the registers if not already done
        if qr is None:
            qr = QuantumRegister(max(qubits_in_pattern)+1)
    else:
        qubits_in_pattern = range(len(qr))
        mit_pattern = [qubits_in_pattern]

    nqubits = len(qubits_in_pattern)

    # create classical bit registers
    if cr is None:
        cr = ClassicalRegister(nqubits)

    qubits_list_sizes = [len(qubit_list) for qubit_list in mit_pattern]
    nqubits = sum(qubits_list_sizes)
    size_of_largest_group = max(qubits_list_sizes)
    largest_labels = count_keys(size_of_largest_group)

    state_labels = []
    for largest_state in largest_labels:
        basis_state = ''
        for list_size in qubits_list_sizes:
            basis_state = largest_state[:list_size] + basis_state
        state_labels.append(basis_state)

    cal_circuits = []
    for basis_state in state_labels:
        qc_circuit = QuantumCircuit(qr, cr,
                                    name='%scal_%s' % (circlabel, basis_state))

        end_index = nqubits
        for qubit_list, list_size in zip(mit_pattern, qubits_list_sizes):

            start_index = end_index - list_size
            substate = basis_state[start_index:end_index]

            for qind in range(list_size):
                if substate[list_size-qind-1] == '1':
                    qc_circuit.x(qr[qubit_list[qind]])

            end_index = start_index

        qc_circuit.barrier(qr)

        # add measurements
        end_index = nqubits
        for qubit_list, list_size in zip(mit_pattern, qubits_list_sizes):

            for qind in range(list_size):
                qc_circuit.measure(qr[qubit_list[qind]],
                                   cr[nqubits-(end_index-qind)])

            end_index -= list_size

        cal_circuits.append(qc_circuit)

    return cal_circuits, mit_pattern
