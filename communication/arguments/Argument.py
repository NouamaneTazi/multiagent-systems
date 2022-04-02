#!/usr/bin/env python3

from communication.arguments.Comparison import Comparison
from communication.arguments.CoupleValue import CoupleValue


class Argument:
    """Argument class.
    This class implements an argument used in the negotiation.

    attr:
        decision: A boolean value (for positive or negative arguments)
        item: The item name
        comparison_list: list of (criterion, criterion) comparisons
        couple_values_list: list of  (criterion, value) couples
    """

    def __init__(self, boolean_decision, item):
        """Creates a new Argument."""
        self.__decision = boolean_decision
        self.__item = item
        self.__comparison_list = []
        self.__couple_values_list = []

    def __str__(self):
        """Returns a string representation of the argument."""
        return f"{'not' if not self.__decision else ''} {self.__item}, {' and '.join(map(str, self.__comparison_list + self.__couple_values_list))}"

    def add_premise_comparison(self, criterion_name_1, criterion_name_2):
        """Adds a premise comparison in the comparison list."""
        self.__comparison_list.append(Comparison(criterion_name_1, criterion_name_2))

    def add_premise_couple_values(self, criterion_name, value):
        """Add a premise couple values in the couple values list."""
        self.__couple_values_list.append(CoupleValue(criterion_name, value))

    def get_conclusion(self):
        """Returns the conclusion of the argument."""
        return (self.__item, self.__decision)

    def get_premises(self):
        """Returns the premises of the argument."""
        return self.__comparison_list + self.__couple_values_list

    def get_supporting_criterion(self):
        """Returns the supporting criterion of the argument."""
        assert (
            len(self.__comparison_list) > 0 or len(self.__couple_values_list) > 0
        ), "The argument has no supporting criterion"
        for comparison in self.__comparison_list:
            return comparison.get_best_criterion_name()
        for couple_value in self.__couple_values_list:
            return couple_value.get_criterion_name()

    def get_couple_value(self):
        """Returns the supporting couple value of the argument.
        TODO: assumes a single couple value per argument"""
        assert len(self.__couple_values_list) > 0, "The argument has no couple value"
        couple_value = self.__couple_values_list[0]
        return couple_value.get_criterion_name(), couple_value.get_value()

    def get_comparison(self):
        """Returns the supporting comparison of the argument.
        TODO: assumes a single comparison per argument"""
        if len(self.__comparison_list) == 0:
            return None, None
        comparison = self.__comparison_list[0]
        return (
            comparison.get_best_criterion_name(),
            comparison.get_worst_criterion_name(),
        )
