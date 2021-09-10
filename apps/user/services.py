import requests
import numpy as np
import copy
import os


class MapsAPIUse:
    """MapsAPIUse class is used for working with Google Directions API."""
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    direction_api_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'

    @staticmethod
    def get_value_matrix_between_addresses(addresses, mode):
        """Method execute request to Directions API and return value matrix between given addresses.

        :param addresses: list of addresses for calculating value matrix between them
        :type addresses: list
        :param mode: argument value for API request for which describe method of movement
        :type mode: str
        :return: matrix of durations which describe time to from one address to another`s
        :rtype: numpy.ndarray
        """
        params = {
            'origins': addresses,
            'destinations': addresses,
            'mode': mode,
            'departure_time': 'now',
            'language': 'uk',
            'key': MapsAPIUse.api_key
        }
        response = requests.get(url=MapsAPIUse.direction_api_url, params=params).json()

        rows = response['rows']
        duration_matrix = list()

        for i in range(len(rows)):
            row = rows[i]
            durations = list()

            for j in range(len(row['elements'])):
                element = row['elements'][j]
                durations.append(element['duration_in_traffic']['value'] if i != j else np.Infinity)

            duration_matrix.append(durations)

        result = {'duration_matrix': np.array(duration_matrix)}

        return result


class Node:
    """Node class is used for holding data of tree node.

    :param value_matrix: matrix of durations which describe time to from one address to another`s
    :type value_matrix: numpy.ndarray
    :param constraint_matrix: matrix which contain state of using paths between addresses (0 - the path forbidden,
    1 - the path is used, 2 - the path has not been used yet)
    :param parent_node: parent node to current node in tree, defaults to None if current node is root node of tree
    :type parent_node: Node
    """
    def __init__(self, value_matrix, constraint_matrix, parent_node=None):
        self.value_matrix = copy.copy(value_matrix)
        self.constraint_matrix = copy.copy(constraint_matrix)
        self.size = len(value_matrix)
        self.parent = parent_node
        self.left_child: Node = None
        self.right_child: Node = None
        self.lower_bound = 0
        self.next_path_to_split = dict()
        self.tour = copy.copy(parent_node.tour) if parent_node else list()

    def reduction_operation(self, axis):
        """Returns sum of min values from rows or from columns.

        If axis = 1 selects minimum values from every row of node value matrix and return
        sum of this values. If axis = 0 selects minimum values from every column of node
        value matrix. Method selects minimum values only from paths that have not been used
        yet.

        :param axis: indicates where to select minimum values, 1 - from rows, 2 - from columns
        :type axis: int

        :return: sum of minimum values
        :type: int
        """
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
        """Calculates lower bound of tour for node.

        Method uses reduction_operation method from this class to calculate sum of minimum
        values from rows and columns of value matrix and sums this values and saves this
        value to node lower bound attribute. If node has a parent, then sums minimum values
        from rows and columns with value of parent node lower bound.

        :return: None
        """
        sum_of_min_values_from_rows = self.reduction_operation(1)
        sum_of_min_values_from_columns = self.reduction_operation(0)

        if self.parent:
            self.lower_bound = self.parent.lower_bound + sum_of_min_values_from_rows + sum_of_min_values_from_columns
        else:
            self.lower_bound = sum_of_min_values_from_rows + sum_of_min_values_from_columns

    def find_next_path(self, previous_vertex, current_vertex):
        """Checks if there is an available path from the current vertex to another vertices.

        :param previous_vertex: the number of the vertex which has been visited before the current vertex
        :type previous_vertex: int
        :param current_vertex: the number of the current vertex from which the next path is searched
        :type current_vertex: int

        :return: dictionary with one key if there is no available path from the current vertex and with
        two keys if there is an available path from the current vertex is the second key saves number of next
        vertex
        :rtype: dict
        """
        for next_vertex in range(self.size):
            if (self.constraint_matrix[current_vertex][next_vertex] == 1) and (next_vertex != previous_vertex):
                return {'has_next': True, 'next_vertex': next_vertex}
        return {'has_next': False}

    def check_sub_tours(self):
        """Checks if there are sub tours to the tour of the current node.

        Method checks every possible path to find the paths which will be able to create sub tours for the
        tour of the current node. Method search every element in constraint matrix with value 2 and
        changes this value to 1 after changing of one element the method tries to find next available path
        from end vertex of the changed path if the method finds the path and the end vertex of this
        path is equal to the start vertex of the changed path and the number of traversed paths is not
        higher then a number of all vertices the method will exclude this path from possible paths.

        :return: None
        """
        for i in range(self.size):
            for j in range(self.size):
                if self.constraint_matrix[i][j] == 2:
                    previous_vertex = i
                    from_vertex = j
                    traversed_paths = 1
                    next_path = self.find_next_path(previous_vertex, from_vertex)
                    while next_path['has_next']:
                        traversed_paths += 1
                        previous_vertex = from_vertex
                        from_vertex = next_path['next_vertex']
                        if from_vertex == i and traversed_paths < self.size:
                            self.constraint_matrix[i][j] = 0
                            self.value_matrix[i][j] = np.Infinity
                            break
                        next_path = self.find_next_path(previous_vertex, from_vertex)
                        if traversed_paths == self.size:
                            break

    def select_next_path_to_split(self):
        """Selects the next path for creating child nodes of the current node.

        After executing reduction operations for rows and columns the method searches
        the possible path of which value in value matrix is the highest.

        :return: None
        """
        self.next_path_to_split['value'] = -1

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
                    if minimum_value_from_row_and_column > self.next_path_to_split['value']:
                        self.next_path_to_split['from'] = i
                        self.next_path_to_split['to'] = j
                        self.next_path_to_split['value'] = minimum_value_from_row_and_column

        del self.next_path_to_split['value']

    def add_path_to_tour(self, path):
        """Adds new path to node tour attribute.

        Method obtains the path argument which contains the start vertex and the end vertex
        of the path and add the path to node tour by changing the constraint matrix of the
        node. Method changes every element in a row to 0 and every element of a column to 0,
        but element at the intersection of row and column is changed to 1 row number is equal
        to the number of the start vertex of the path and column number is equal to the number
        of the end vertex of the path.

        :param path: Contain the start vertex and end vertex of the path is needed to
        add to the node tour
        :type path: dict

        :return: None
        """
        for i in range(self.size):
            self.constraint_matrix[path['from']][i] = 0
            self.constraint_matrix[i][path['to']] = 0
        self.constraint_matrix[path['from']][path['to']] = 1
        self.constraint_matrix[path['to']][path['from']] = 0

        self.value_matrix[path['to']][path['from']] = np.Infinity
        self.tour.append(path)

    def exclude_path_from_tour(self, path):
        """Excludes path from available paths.

        The method obtains a path argument containing the start and end vertices of the
        path and excludes the path from the available paths by changing the constraint
        matrix of the node. Element of the constraint matrix at the intersection of row
        and column is changed to 0 row number is equal to the number of the start vertex
        of the path and column number is equal to the number of the end vertex of the path.

        :param path: Contain the start vertex and end vertex of the path is needed to
        exclude from available path
        :type: dict

        :return: None
        """
        self.constraint_matrix[path['from']][path['to']] = 0
        self.value_matrix[path['from']][path['to']] = np.Infinity

    def min(self, axis):
        """Returns list of minimum values from every row or columns of value matrix depending
        on axis argument.

        :param axis: value which indicates where to choose minimum values, if axis is
        equal to 1 minimum values choose from every row of value matrix, if axis is equal
        to 0 minimum values choose from every column of value matrix
        :type axis: int

        :return: the list of minimum values from rows or columns depends on axis argument
        :rtype: list
        """
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
        """Checks if the current node`s tour is a full tour.

        Method checks the constraint matrix and if maximum value of every row of
        matrix is equal to 1 and number of value 1 in this row is equal to 1 it
        means that the tour of current node is full.

        :return: the result of checking whether the node tour is complete, if the
        tour is complete then the value is True, if the tour is not complete value
        then the value is True
        :rtype: bool
        """
        for matrix_row in self.constraint_matrix:
            if np.max(matrix_row) in (0, 2) or list(matrix_row).count(1) > 1:
                return False
        return True


class Solver:
    """Class is used to combine methods for resolving Branch and Bound algorithm.

    :param value_matrix: matrix of durations which describe time to from one address to another`s
    :type value_matrix: numpy.ndarray
    """
    def __init__(self, value_matrix):
        self.value_matrix = value_matrix
        self.size = len(value_matrix)
        self.root_node: Node = None

    def create_constraints_matrix(self):
        """Creates a constraint matrix.

        Method simplify creating of constraint matrix. Every element of created
        matrix is equal to 2 except of elements which are at the intersection of
        row and column with same number.

        :return: created constraint matrix
        :rtype: numpy.ndarray
        """
        constraints_matrix = list()

        for i in range(self.size):
            matrix_row = [2] * self.size
            matrix_row[i] = 0
            constraints_matrix.append(matrix_row)

        return np.array(constraints_matrix)

    def branch_and_bound_method(self):
        """Executes a sequence of steps for resolving the algorithm.

        At the start, method creates a root node of the tree after that starts a cycle
        until it finds the final result

        :return: the end result of solving the algorithm according to given value matrix
        :rtype: dict
        """
        self.root_node = Node(self.value_matrix, self.create_constraints_matrix())
        self.root_node.calculate_lower_bound_of_tour()
        self.root_node.select_next_path_to_split()

        left_child = Solver.create_child_node(self.root_node, add_path=True)
        self.root_node.left_child = left_child
        right_child = Solver.create_child_node(self.root_node)
        self.root_node.right_child = right_child

        while True:
            parent = left_child if left_child.lower_bound <= right_child.lower_bound else right_child
            parent = self.check_lower_bound_of_another_leaves(self.root_node, parent)

            if parent.is_tour():
                break
            parent.select_next_path_to_split()
            left_child = Solver.create_child_node(parent, add_path=True)
            parent.left_child = left_child
            right_child = Solver.create_child_node(parent)
            parent.right_child = right_child

        final_result = {'tour': parent.tour, 'tour_duration': parent.lower_bound}

        return final_result

    @staticmethod
    def create_child_node(parent_node: Node, add_path=False):
        """Creates new a new instance of Node class.

        :param parent_node: instance of Node class which is a parent node for new class instance
        :type parent_node: Node
        :param add_path: indicates whether need to add new path to created class instance
        :type add_path: bool

        :return:
        :rtype: Node
        """
        new_node = Node(parent_node.value_matrix, parent_node.constraint_matrix, parent_node)

        if add_path:
            new_node.add_path_to_tour(parent_node.next_path_to_split)
        else:
            new_node.exclude_path_from_tour(parent_node.next_path_to_split)

        new_node.check_sub_tours()
        new_node.calculate_lower_bound_of_tour()

        return new_node

    @staticmethod
    def check_lower_bound_of_another_leaves(parent_node: Node, current_node: Node):
        """Checks whether there is a leaf of this tree with less value of the lower bound
         attribute then current leaf.

         If the parent node passed in the argument has child nodes and these child nodes
         have a lower bound attribute value less than the current node, the method calls
         itself by passing its child node as the parent node. This recursion continues
         until the method finds the leaves of the tree. If the value of the lower limit
         of the tree leaf is less than the current one, the current leaf will change to
         the found one. At the end of this method, the continuation of the solution is
         continued from the returned leaf of the tree.

        :param parent_node: the node of the built tree for which checks are performed
        :type: Node
        :param current_node: the node on which the previous iteration of the algorithm was performed
        :type: Node

        :return: tree leaf with the lowest value of lower bound attribute
        :rtype: Node
        """
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
