from unittest import TestCase
import numpy as np

from ..services import Solver, Node, MapsAPIUse


class TestNode(TestCase):
    def setUp(self):
        self.duration_matrix = np.array([
            [np.Infinity, 40, 8, 80, 48],
            [24, np.Infinity, 27, 68, 66],
            [9, 37, np.Infinity, 82, 49],
            [64, 76, 62, np.Infinity, 48],
            [43, 64, 41, 42, np.Infinity]
        ])
        self.constraint_matrix = np.array([
            [0, 2, 2, 2, 2],
            [2, 0, 2, 2, 2],
            [2, 2, 0, 2, 2],
            [2, 2, 2, 0, 2],
            [2, 2, 2, 2, 0]
        ])
        self.size = len(self.duration_matrix)
        self.node = Node(self.duration_matrix, self.constraint_matrix)

    def test_min_method(self):
        minimum_value_from_rows = self.node.min(axis=1)
        minimum_value_from_columns = self.node.min(axis=0)

        self.assertIsInstance(minimum_value_from_rows, list)
        self.assertIsInstance(minimum_value_from_columns, list)
        self.assertEqual(minimum_value_from_rows, [8, 24, 9, 48, 41])
        self.assertEqual(minimum_value_from_columns, [9, 37, 8, 42, 48])

        self.node.constraint_matrix[0][2] = 0
        self.node.constraint_matrix[2][0] = 0
        self.node.constraint_matrix[4][2] = 0

        self.node.value_matrix[1][0] = 99
        self.node.value_matrix[3][4] = 99

        minimum_value_from_rows = self.node.min(axis=1)
        minimum_value_from_columns = self.node.min(axis=0)

        self.assertEqual(minimum_value_from_rows, [40, 27, 37, 62, 42])
        self.assertEqual(minimum_value_from_columns, [43, 37, 27, 42, 48])

    def test_reduction_operation_method(self):
        sum_of_minimum_value_from_rows = self.node.reduction_operation(axis=1)
        sum_of_minimum_value_from_columns = self.node.reduction_operation(axis=0)

        self.assertNotIsInstance(sum_of_minimum_value_from_rows, list)
        self.assertNotIsInstance(sum_of_minimum_value_from_columns, list)
        self.assertEqual(sum_of_minimum_value_from_rows, 130)
        self.assertEqual(sum_of_minimum_value_from_columns, 24)

        sum_of_minimum_value_from_rows = self.node.reduction_operation(axis=1)
        sum_of_minimum_value_from_columns = self.node.reduction_operation(axis=0)

        self.assertEqual(sum_of_minimum_value_from_rows, 0)
        self.assertEqual(sum_of_minimum_value_from_columns, 0)

    def test_calculate_lower_bound_of_tour_method(self):
        self.node.calculate_lower_bound_of_tour()

        self.assertEqual(self.node.lower_bound, 154)

        self.node.value_matrix[0][2] = 99
        self.node.calculate_lower_bound_of_tour()

        self.assertEqual(self.node.lower_bound, 9)

    def test_find_next_path_method(self):
        self.node.constraint_matrix[0][2] = 1
        self.node.constraint_matrix[2][0] = 1

        result = self.node.find_next_path(0, 2)
        self.assertEqual(result, {'has_next': False})

        self.node.constraint_matrix[0][2] = 0
        self.node.constraint_matrix[4][2] = 1

        result = self.node.find_next_path(2, 4)
        self.assertEqual(result, {'has_next': False})

        result = self.node.find_next_path(1, 4)
        self.assertEqual(result, {'has_next': True, 'next_vertex': 2})

    def test_check_sub_tours_method(self):
        self.node.constraint_matrix = np.array([
            [0, 2, 2, 0, 0],
            [0, 0, 0, 1, 0],
            [2, 2, 0, 2, 2],
            [0, 0, 0, 0, 1],
            [2, 2, 2, 0, 0]
        ])

        self.node.check_sub_tours()

        self.assertEqual(self.node.constraint_matrix[4][1], 0)

        self.node.constraint_matrix[2][1] = 1
        self.node.check_sub_tours()

        self.assertEqual(self.node.constraint_matrix[4][2], 0)

    def test_add_path_to_tour_method(self):
        self.node.add_path_to_tour({'from': 2, 'to': 4})
        self.node.add_path_to_tour({'from': 4, 'to': 0})

        self.assertEqual(self.node.constraint_matrix[2][4], 1)
        self.assertEqual(self.node.constraint_matrix[4][2], 0)
        self.assertEqual(sum(self.node.constraint_matrix[2]), 1)
        self.assertEqual(self.node.constraint_matrix[4][0], 1)
        self.assertEqual(self.node.constraint_matrix[0][4], 0)
        self.assertEqual(sum(self.node.constraint_matrix[4]), 1)

    def test_exclude_path_from_tour(self):
        self.node.exclude_path_from_tour({'from': 2, 'to': 4})
        self.node.exclude_path_from_tour({'from': 3, 'to': 1})

        self.assertEqual(self.node.constraint_matrix[2][4], 0)
        self.assertEqual(self.node.constraint_matrix[3][1], 0)

    def test_select_next_path_to_split(self):
        self.node.calculate_lower_bound_of_tour()
        self.node.select_next_path_to_split()

        self.assertEqual(self.node.next_path_to_split, {'from': 3, 'to': 4})

        for i in range(self.size):
            self.node.constraint_matrix[3][i] = 0
            self.node.constraint_matrix[i][4] = 0
        self.node.constraint_matrix[4][3] = 0
        self.node.next_path_to_split = {'value': -1}

        self.node.calculate_lower_bound_of_tour()
        self.node.select_next_path_to_split()

        self.assertEqual(self.node.next_path_to_split, {'from': 1, 'to': 3})

    def test_is_tour_method(self):
        self.node.constraint_matrix = np.array([
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0]
        ])

        self.assertEqual(self.node.is_tour(), True)

        self.node.constraint_matrix[0][4] = 1
        self.assertEqual(self.node.is_tour(), False)

        self.node.constraint_matrix[0][4] = 0
        self.node.constraint_matrix[2][1] = 0
        self.assertEqual(self.node.is_tour(), False)


class TestMapsAPIUseClass(TestCase):
    def test_get_value_matrix_between_addresses_method(self):
        addresses = ['Оперний театр, Львів', 'Forum, Львів', 'Цирк, Львів']
        params = {
            'addresses': '|'.join(addresses),
            'mode': 'driving'
        }

        result = MapsAPIUse.get_value_matrix_between_addresses(**params)

        self.assertIsInstance(result['duration_matrix'], np.ndarray)
        self.assertEqual(len(result['duration_matrix']), len(addresses))
        for i in range(len(addresses)):
            self.assertEqual(result['duration_matrix'][i][i], np.Infinity)


class TestSolverClass(TestCase):
    def setUp(self):
        self.duration_matrix = np.array([
            [np.Infinity, 40, 8, 80, 48],
            [24, np.Infinity, 27, 68, 66],
            [9, 37, np.Infinity, 82, 49],
            [64, 76, 62, np.Infinity, 48],
            [43, 64, 41, 42, np.Infinity]
        ])

        self.solver = Solver(self.duration_matrix)

    def test_create_constraints_matrix_method(self):
        created_matrix = self.solver.create_constraints_matrix()

        self.assertIsInstance(created_matrix, np.ndarray)
        self.assertEqual(len(created_matrix), self.solver.size)
        for i in range(self.solver.size):
            self.assertEqual(created_matrix[i][i], 0)

    def test_create_child_node_method(self):
        root_node = Node(self.solver.value_matrix, self.solver.create_constraints_matrix())
        root_node.reduction_operation(1)
        root_node.reduction_operation(0)
        root_node.select_next_path_to_split()

        left_child_node = self.solver.create_child_node(root_node, add_path=True)
        right_child_node = self.solver.create_child_node(root_node)

        self.assertIsInstance(left_child_node, Node)
        self.assertEqual(left_child_node.parent, root_node)
        self.assertEqual(len(left_child_node.tour), 1)
        self.assertIn(root_node.next_path_to_split, left_child_node.tour)
        self.assertIsInstance(right_child_node, Node)
        self.assertEqual(right_child_node.parent, root_node)
        self.assertEqual(len(right_child_node.tour), 0)
        self.assertNotIn(root_node.next_path_to_split, right_child_node.tour)

    def test_branch_and_bound_method(self):
        final_result = self.solver.branch_and_bound_method()
        correct_result = [{'from': 4, 'to': 3}, {'from': 3, 'to': 1}, {'from': 0, 'to': 2}, {'from': 1, 'to': 0},
                          {'from': 2, 'to': 4}]

        self.assertIsInstance(final_result, dict)
        self.assertEqual(final_result['tour_duration'], 199)
        self.assertEqual(final_result['tour'], correct_result)




