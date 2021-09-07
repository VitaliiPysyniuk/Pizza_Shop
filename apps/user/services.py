import requests
import numpy as np
import copy


class MapsAPIUse:
    api_key = 'AIzaSyATtXEM2gWMdhxjky2KMF7ebfJ58WmevQE'
    direction_api_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'

    @staticmethod
    def get_distance_and_duration_between_addresses(start_address, end_addresses):
        params = {
            'origins': start_address,
            'destinations': end_addresses,
            'mode': 'driving',
            'departure_time': 'now',
            'language': 'uk',
            'key': MapsAPIUse.api_key
        }
        response = requests.get(url=MapsAPIUse.direction_api_url, params=params).json()

        rows = response['rows']
        distance_matrix = list()
        duration_matrix = list()

        for i in range(len(rows)):
            row = rows[i]
            distances = list()
            durations = list()

            for j in range(len(row['elements'])):
                element = row['elements'][j]
                distances.append(element['distance']['value'] if element['distance']['value'] != 0 else np.Infinity)
                durations.append(element['duration_in_traffic']['value'] if i != j else np.Infinity)

            distance_matrix.append(distances)
            duration_matrix.append(durations)

        result = {'distance_matrix': np.array(distance_matrix), 'duration_matrix': np.array(duration_matrix)}

        return result


class Node:
    def __init__(self, value_matrix, constraint_matrix, parent=None):
        self.value_matrix = copy.copy(value_matrix)
        self.constraint_matrix = copy.copy(constraint_matrix)
        self.size = len(value_matrix)
        self.parent = parent
        self.left_child: Node = None
        self.right_child: Node = None
        self.lower_bound = 0
        self.next_way_to_split = dict()
        self.tour = copy.copy(parent.tour) if parent else list()

    def reduction_operation(self, axis):
        minimum_values = self.min(axis=axis)

        for i in range(self.size):
            if np.max(self.constraint_matrix, axis=axis)[i] == 1:
                continue

            for j in range(self.size):
                if np.max(self.constraint_matrix, axis=1 if axis == 0 else 0)[j] == 1:
                    continue
                if axis == 1 and self.constraint_matrix[i][j] == 2:
                    self.value_matrix[i][j] = self.value_matrix[i][j] - minimum_values[i]
                elif axis == 0 and self.constraint_matrix[j][i] == 2:
                    self.value_matrix[j][i] = self.value_matrix[j][i] - minimum_values[i]

        return sum(minimum_values)

    def calculate_lower_bound_of_tour(self):
        sum_of_min_values_from_rows = self.reduction_operation(1)
        sum_of_min_values_from_columns = self.reduction_operation(0)

        if self.parent:
            self.lower_bound = self.parent.lower_bound + sum_of_min_values_from_rows + sum_of_min_values_from_columns
        else:
            self.lower_bound = sum_of_min_values_from_rows + sum_of_min_values_from_columns

    def find_next_way(self, previous_vertex, from_vertex):
        for to_vertex in range(self.size):
            if (self.constraint_matrix[from_vertex][to_vertex] == 1) and (to_vertex != previous_vertex):
                return {'has_next': True, 'next_vertex': to_vertex}
        return {'has_next': False}

    def check_subtours(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.constraint_matrix[i][j] == 2:
                    previous_vertex = i
                    from_vertex = j
                    traversed_ways = 1
                    next_way = self.find_next_way(previous_vertex, from_vertex)
                    while next_way['has_next']:
                        traversed_ways += 1
                        previous_vertex = from_vertex
                        from_vertex = next_way['next_vertex']
                        if from_vertex == i and traversed_ways < self.size:
                            self.constraint_matrix[i][j] = 0
                            self.value_matrix[i][j] = np.Infinity
                            break
                        next_way = self.find_next_way(previous_vertex, from_vertex)
                        if traversed_ways == self.size:
                            break

    def select_next_way_to_split(self):
        self.next_way_to_split['value'] = -1

        for i in range(self.size):
            if np.max(self.constraint_matrix, axis=1)[i] == 1:
                continue
            for j in range(self.size):
                if np.max(self.constraint_matrix, axis=0)[j] == 1:
                    continue
                if self.value_matrix[i][j] == 0:
                    self.value_matrix[i][j] = np.Infinity
                    minimum_value_from_row_and_column = self.min(axis=1)[i] + self.min(axis=0)[j]
                    self.value_matrix[i][j] = 0
                    if minimum_value_from_row_and_column > self.next_way_to_split['value']:
                        self.next_way_to_split['from'] = i
                        self.next_way_to_split['to'] = j
                        self.next_way_to_split['value'] = minimum_value_from_row_and_column

        del self.next_way_to_split['value']

    def add_way_to_tour(self, way):
        for i in range(self.size):
            self.constraint_matrix[way['from']][i] = 0
            self.constraint_matrix[i][way['to']] = 0
        self.constraint_matrix[way['from']][way['to']] = 1
        self.constraint_matrix[way['to']][way['from']] = 0

        self.value_matrix[way['to']][way['from']] = np.Infinity
        self.tour.append(way)

    def exclude_way_from_tour(self, way):
        self.constraint_matrix[way['from']][way['to']] = 0
        self.value_matrix[way['from']][way['to']] = np.Infinity

    def min(self, axis):
        minimum_values = list()

        for i in range(self.size):
            minimum_values.append(np.Infinity)

            for j in range(self.size):
                if axis == 1:
                    if self.constraint_matrix[i][j] == 2 and self.value_matrix[i][j] < minimum_values[-1]:
                        minimum_values[-1] = self.value_matrix[i][j]
                else:
                    if self.constraint_matrix[j][i] == 2 and self.value_matrix[j][i] < minimum_values[-1]:
                        minimum_values[-1] = self.value_matrix[j][i]

            minimum_values[-1] = 0 if minimum_values[-1] == np.Infinity else minimum_values[-1]

        return minimum_values

    def is_tour(self):
        for matrix_row in self.constraint_matrix:
            if np.max(matrix_row) in (0, 2):
                return False
        return True


class Solver:
    def __init__(self, value_matrix):
        self.value_matrix = value_matrix
        self.size = len(value_matrix)
        self.high_bound = self.calculate_high_bound()
        self.root_node: Node = None

    def calculate_high_bound(self):
        high_bound = 0
        visited_vertices = list()
        from_vertex = 0

        while len(visited_vertices) != self.size:
            possible_ways = list(self.value_matrix[from_vertex])
            del possible_ways[from_vertex]

            while possible_ways:
                minimum_way = min(possible_ways)
                to_vertex = list(self.value_matrix[from_vertex]).index(minimum_way)

                if to_vertex == 0 and (len(visited_vertices) == self.size - 1):
                    visited_vertices.append(to_vertex)
                    high_bound += minimum_way
                    break
                elif to_vertex != 0 and (to_vertex not in visited_vertices):
                    visited_vertices.append(to_vertex)
                    high_bound += minimum_way
                    from_vertex = to_vertex
                    break

                possible_ways.remove(minimum_way)

        return high_bound

    def create_constraints_matrix(self):
        constraints_matrix = list()

        for i in range(self.size):
            matrix_row = [2] * self.size
            matrix_row[i] = 0
            constraints_matrix.append(matrix_row)

        return np.array(constraints_matrix)

    def branch_and_bound_method(self):
        self.root_node = Node(self.value_matrix, self.create_constraints_matrix())
        self.root_node.calculate_lower_bound_of_tour()
        self.root_node.select_next_way_to_split()

        left_child = Solver.create_child_node(self.root_node, add_way=True)
        self.root_node.left_child = left_child
        right_child = Solver.create_child_node(self.root_node)
        self.root_node.right_child = right_child

        while True:
            parent = left_child if left_child.lower_bound <= right_child.lower_bound else right_child
            parent = self.check_lower_bound_of_another_leaves(self.root_node, parent)

            if parent.is_tour():
                break
            parent.select_next_way_to_split()
            left_child = Solver.create_child_node(parent, add_way=True)
            parent.left_child = left_child
            right_child = Solver.create_child_node(parent)
            parent.right_child = right_child

        final_result = {'tour': parent.tour, 'tour_duration': parent.lower_bound}

        return final_result

    @staticmethod
    def create_child_node(parent_node: Node, add_way=False):
        new_node = Node(parent_node.value_matrix, parent_node.constraint_matrix, parent_node)

        if add_way:
            new_node.add_way_to_tour(parent_node.next_way_to_split)
        else:
            new_node.exclude_way_from_tour(parent_node.next_way_to_split)

        new_node.check_subtours()
        new_node.calculate_lower_bound_of_tour()

        return new_node

    @staticmethod
    def check_lower_bound_of_another_leaves(parent_node: Node, current_node: Node):
        node_from_left_branch: Node = None
        node_from_right_branch: Node = None

        if not parent_node.left_child and not parent_node.right_child and parent_node.lower_bound < current_node.lower_bound:
            return parent_node

        if parent_node.left_child and (parent_node.left_child.lower_bound <= current_node.lower_bound):
            node_from_left_branch = Solver.check_lower_bound_of_another_leaves(parent_node.left_child, current_node)
        if parent_node.right_child and (parent_node.right_child.lower_bound <= current_node.lower_bound):
            node_from_right_branch = Solver.check_lower_bound_of_another_leaves(parent_node.right_child,
                                                                                current_node)

        if node_from_left_branch and node_from_right_branch:
            if node_from_left_branch.lower_bound <= node_from_right_branch.lower_bound:
                if node_from_left_branch != current_node:
                    return node_from_left_branch
            elif node_from_left_branch.lower_bound > node_from_right_branch.lower_bound:
                if node_from_right_branch != current_node:
                    return node_from_right_branch

        elif node_from_left_branch:
            if node_from_left_branch != current_node and node_from_left_branch.lower_bound < current_node.lower_bound:
                return node_from_left_branch

        elif node_from_right_branch:
            if node_from_right_branch != current_node and node_from_right_branch.lower_bound < current_node.lower_bound:
                return node_from_right_branch

        return current_node
