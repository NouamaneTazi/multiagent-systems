#!/usr/bin/env python3

from communication.arguments.Comparison import Comparison
from communication.arguments.CoupleValue import CoupleValue


class Argument:
    """Argument class.
    This class implements an argument used in the negotiation.

    attr:
        decision:
        item:
        comparison_list:
        couple_values_list:
    """

    def __init__(self, boolean_decision, item):
        """Creates a new Argument.
        """
        self.__decision = boolean_decision
        self.__item = item.get_name()
        self.__comparison_list = []
        self.__couple_values_list = []

    def get_decision(self):
        return self.__decision

    def get_item(self):
        return self.__item

    def get_comparision_list(self):
        return self.__comparison_list
    
    def get_couple_values_list(self):
        return self.__couple_values_list

    def add_premiss_comparison(self, criterion_name_1, criterion_name_2):
        """Adds a premiss comparison in the comparison list.
        """
        self.__comparison_list.append(Comparison(criterion_name_1, criterion_name_2))

    def add_premiss_couple_values(self, criterion_name, value):
        """Add a premiss couple values in the couple values list.
        """
        self.__couple_values_list.append(CoupleValue(criterion_name, value))

    def describe_self(self):
        return self.__item, self.__decision, self.__comparison_list, self.__couple_values_list

    def log_arg(self):
        if len(self.__comparison_list)>0:
            print(self.__item, self.__couple_values_list[0].get_value(), self.__comparison_list[0].get_best_criterion_name(), self.__comparison_list[0].get_worst_criterion_name())
        
        else:
            print(self.__item, self.__couple_values_list[0].get_value(), self.__couple_values_list[0].get_criterion_name())

