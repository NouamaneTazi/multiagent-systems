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
        self.__item = item.get_name()
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
