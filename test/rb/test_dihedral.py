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
Tests for CNOT-dihedral functions
"""

import unittest

# Import the dihedral_utils functions
from qiskit.ignis.verification.randomized_benchmarking \
    import CNOTDihedral, random_cnotdihedral


class TestCNOTDihedral(unittest.TestCase):
    """
        Test CNOT-dihedral functions
    """
    def setUp(self):
        """
            setUp and global parameters
        """
        self.number_of_tests = 20  # number of pseudo-random seeds
        self.max_qubit_num = 2  # maximal number of qubits to check
        self.table_size = [0, 16, 6144]

    def test_dihedral_random_decompose(self):
        """
        Test that random elements are CNOTDihedral
        and to_circuit and from_circuit methods
        (where num_qubits < 3)
        """
        for qubit_num in range(1, 5):
            for nseed in range(20):
                elem = random_cnotdihedral(qubit_num, seed=nseed)
                self.assertTrue(elem,
                                'Error: random element is '
                                'not CNOTDihedral')
                if qubit_num < 3:
                    test_circ = elem.to_circuit()
                    self.assertTrue(test_circ,
                                    'Error: cannot decompose a random '
                                    'CNOTDihedral element to a circuit')
                    new_elem = CNOTDihedral(qubit_num)
                    test_elem = new_elem.from_circuit(test_circ)
                    # Test of to_circuit and from_circuit methods
                    self.assertEqual(elem, test_elem,
                                     'Error: decomposed circuit is not equal '
                                     'to the original circuit')

    def test_compose_method(self):
        """Test compose method"""
        samples = 10
        nseed = 111
        for qubit_num in range(1, 3):
            for i in range(samples):
                elem1 = random_cnotdihedral(qubit_num, seed=nseed + i)
                elem2 = random_cnotdihedral(qubit_num, seed=nseed + samples + i)
                circ1 = elem1.to_circuit()
                circ2 = elem2.to_circuit()
                value = elem1.compose(elem2)
                target = CNOTDihedral(qubit_num)
                target = target.from_circuit(circ1.extend(circ2))
                self.assertEqual(target, value,
                                 'Error: composed circuit is not the same')

    def test_dot_method(self):
        """Test dot method"""
        samples = 10
        nseed = 222
        for qubit_num in range(1, 3):
            for i in range(samples):
                elem1 = random_cnotdihedral(qubit_num, seed=nseed + i)
                elem2 = random_cnotdihedral(qubit_num, seed=nseed + samples + i)
                circ1 = elem1.to_circuit()
                circ2 = elem2.to_circuit()
                value = elem1.dot(elem2)
                target = CNOTDihedral(qubit_num)
                target = target.from_circuit(circ2.extend(circ1))
                self.assertEqual(target, value,
                                 'Error: composed circuit is not the same')


if __name__ == '__main__':
    unittest.main()
