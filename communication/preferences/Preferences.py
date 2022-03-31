#!/usr/bin/env python3

from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value


class Preferences:
    """Preferences class.
    This class implements the preferences of an agent.

    attr:
        criterion_name_list: the list of criterion name (ordered by importance)
        criterion_value_list: the list of criterion value
        item_list: the list of items
    """

    def __init__(self):
        """Creates a new Preferences object."""
        self.__criterion_name_list = []
        self.__criterion_value_list = []
        self.__item_list = []

    def __str__(self):
        """Returns a string representation of the preferences."""
        return (
            f"\n* Items: {self.__item_list}\n* Criteria: {self.__criterion_name_list}"
        )

    def get_criterion_name_list(self):
        """Returns the list of criterion name."""
        return self.__criterion_name_list

    def get_criterion_value_list(self):
        """Returns the list of criterion value."""
        return self.__criterion_value_list

    def get_item_list(self):
        """Returns the list of items."""
        return self.__item_list

    def set_criterion_name_list(self, criterion_name_list):
        """Sets the list of criterion name (ordered by importance)."""
        self.__criterion_name_list = criterion_name_list

    def add_criterion_value(self, criterion_value):
        """Adds a criterion value in the list."""
        item = criterion_value.get_item()
        if item not in self.__item_list:
            self.__item_list.append(item)
        self.__criterion_value_list.append(criterion_value)

    def get_value(self, item, criterion_name):
        """Gets the value for a given item and a given criterion name."""
        for value in self.__criterion_value_list:
            if (
                value.get_item() == item
                and value.get_criterion_name() == criterion_name
            ):
                return value.get_value()
        return None

    def is_preferred_criterion(self, criterion_name_1, criterion_name_2):
        """Returns if a criterion 1 is preferred to the criterion 2."""
        for criterion_name in self.__criterion_name_list:
            if criterion_name == criterion_name_1:
                return True
            if criterion_name == criterion_name_2:
                return False

    def is_preferred_item(self, item_1, item_2):
        """Returns if the item 1 is preferred to the item 2."""
        return item_1.get_score(self) > item_2.get_score(self)

    def most_preferred(self, item_list=None):
        """Returns the most preferred item from a list. If no list is given, the list of items known by agent is used."""
        if not item_list or len(item_list) == 0:
            if len(self.__item_list) == 0:
                return None
            else:
                item_list = self.__item_list
        best_item = item_list[0]
        for item in item_list:
            if self.is_preferred_item(
                item, best_item
            ):  # TODO: check if we need to shuffle the list before
                best_item = item
        return best_item

    def is_item_among_top_10_percent(self, item, list_items):
        """
        Return whether a given item is among the top 10 percent of the preferred items.

        :return: a boolean, True means that the item is among the favourite ones
        """
        return self.is_item_among_top_x_percent(item, 10, list_items)

    def is_item_among_top_x_percent(self, item, x, list_items=None):
        """
        Return whether a given item is among the top x percent of the preferred items.

        :return: a boolean, True means that the item is among the favourite ones
        """
        if list_items is None:
            list_items = self.__item_list
        assert (
            len(list_items) > 0 and item in list_items
        ), f"{item} is not in {list_items}"
        scores = [item.get_score(self) for item in list_items]
        scores.sort(reverse=True)
        top_x_percent = scores[: int(len(scores) * x / 100)]
        return item.get_score(self) in top_x_percent

    def remove_item(self, item):
        """Removes an item from the list of items and the related criteria."""
        self.__item_list.remove(item)
        for criterion_value in self.__criterion_value_list:
            if criterion_value.get_item() == item:
                self.__criterion_value_list.remove(criterion_value)


if __name__ == "__main__":
    """Testing the Preferences class."""
    agent_pref = Preferences()
    agent_pref.set_criterion_name_list(
        [
            CriterionName.PRODUCTION_COST,
            CriterionName.ENVIRONMENT_IMPACT,
            CriterionName.CONSUMPTION,
            CriterionName.DURABILITY,
            CriterionName.NOISE,
        ]
    )

    diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.PRODUCTION_COST, Value.VERY_GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.CONSUMPTION, Value.GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.DURABILITY, Value.VERY_GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.ENVIRONMENT_IMPACT, Value.VERY_BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(diesel_engine, CriterionName.NOISE, Value.VERY_BAD)
    )

    electric_engine = Item("Electric Engine", "A very quiet engine")
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.PRODUCTION_COST, Value.BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.CONSUMPTION, Value.VERY_BAD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.DURABILITY, Value.GOOD)
    )
    agent_pref.add_criterion_value(
        CriterionValue(
            electric_engine, CriterionName.ENVIRONMENT_IMPACT, Value.VERY_GOOD
        )
    )
    agent_pref.add_criterion_value(
        CriterionValue(electric_engine, CriterionName.NOISE, Value.VERY_GOOD)
    )

    """test list of preferences"""
    print(diesel_engine)
    print(electric_engine)
    print(diesel_engine.get_value(agent_pref, CriterionName.PRODUCTION_COST))
    print(
        agent_pref.is_preferred_criterion(
            CriterionName.CONSUMPTION, CriterionName.NOISE
        )
    )
    print(
        "Electric Engine > Diesel Engine : {}".format(
            agent_pref.is_preferred_item(electric_engine, diesel_engine)
        )
    )
    print(
        "Diesel Engine > Electric Engine : {}".format(
            agent_pref.is_preferred_item(diesel_engine, electric_engine)
        )
    )
    print(
        "Electric Engine (for agent 1) = {}".format(
            electric_engine.get_score(agent_pref)
        )
    )
    print(
        "Diesel Engine (for agent 1) = {}".format(diesel_engine.get_score(agent_pref))
    )
    print(
        "Most preferred item is : {}".format(
            agent_pref.most_preferred([diesel_engine, electric_engine]).get_name()
        )
    )
