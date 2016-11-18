import itertools


class Node:

    def __init__(self, id, latitude, longitude):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return "Node({0}, {1}, {2})".format(self.id, self.latitude,
                                            self.longitude)

    def __repr__(self):
        return str(self)


class Solution:

    def __init__(self, tour, value):
        self.tour = tour
        self.value = value


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ...
    Source:
    https://docs.python.org/3.5/library/itertools.html#itertools-recipes
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def reverse_subtour(tour, start, end):
    """Returns a new list with the subtour reversed"""
    return tour[:start] + list(reversed(tour[start:end + 1])) + tour[end + 1:]


def solve(tour):
    """Solves the Traveling Salesman Problem (TSP) with a heuristic.

    Args:
        tour: List of nodes (Node) representing a tour. Even if a tour
            starts and ends at the same node, the last node in the
            list must be the last destination visited before returning
            to the starting point.

    Returns:
        A tour with a distance less or equal to the distance of the
        initial tour.

    """

    # This function implements a local search heuristic with a 2-opt
    # neighborhood to solve an Euclidean TSP.

    best_solution = Solution(list(tour), tour_squared_distance(tour))

    improved = True
    while improved:
        improved = False
        best_candidate = Solution(best_solution.tour, best_solution.value)

        for candidate_tour in two_opt_neighbors(best_solution.tour):
            candidate = Solution(candidate_tour,
                                 tour_squared_distance(candidate_tour))

            # We use the squared distance since the square root
            # function is monotone increasing, so comparing squared
            # distance is equivalent to comparing distances.
            if candidate.value < best_candidate.value:
                best_candidate = candidate

        if best_candidate.value < best_solution.value:
            improved = True
            best_solution = best_candidate

    return best_solution.tour


def squared_distance(a, b):
    """Squared euclidean distance"""

    return (a.latitude - b.latitude) ** 2 + \
        (a.longitude - b.longitude) ** 2


def tour_squared_distance(tour):
    # "+ tour[0]" => add the distance for returning to the starting
    # point
    distance = 0
    for a, b in pairwise(tour + [tour[0]]):
        distance += squared_distance(a, b)
    return distance


def two_opt_neighbors(tour):
    """Generates 2-opt neighbors for a tour.

    https://en.wikipedia.org/wiki/2-opt
    """
    for start in range(1, len(tour) - 1):
        for end in range(start + 1, len(tour)):
            yield reverse_subtour(tour, start, end)
