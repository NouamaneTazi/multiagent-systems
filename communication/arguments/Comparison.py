#!/usr/bin/env python3


class Comparison:
    """Comparison class.
    This class implements a comparison object used in argument object.

    attr:
        best_criterion_name:
        worst_criterion_name:
    """

    def __init__(self, best_criterion_name, worst_criterion_name):
        """Creates a new comparison."""
        self.__best_criterion_name = best_criterion_name
        self.__worst_criterion_name = worst_criterion_name

    def __str__(self):
        """Returns a string representation of the comparison."""
        return f"{self.__best_criterion_name}>{self.__worst_criterion_name}"

    def get_worst_criterion_name(self):
        return self.__worst_criterion_name

    def get_best_criterion_name(self):
        return self.__best_criterion_name
