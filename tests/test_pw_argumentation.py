import unittest
from typing import Dict, List, Tuple

from mesa import Model
from mesa.time import RandomActivation, BaseScheduler

from pw_argumentation import ArgumentAgent
from communication.agent.CommunicatingAgent import CommunicatingAgent

from communication.message.MessageService import MessageService
from communication.message.MessagePerformative import MessagePerformative
from communication.message.Message import Message

from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value
from communication.preferences.Preferences import Preferences

from communication.arguments.Argument import Argument

import random as rd
import pandas as pd
import logging
import colorama
from collections import defaultdict


class ArgumentModelTester(Model):
    """ArgumentModel which inherit from Model."""

    def __init__(self, agents_prefs):
        self.schedule = BaseScheduler(self)  # RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)

        available_colors = [
            colorama.Fore.YELLOW,
            colorama.Fore.BLUE,
            colorama.Fore.MAGENTA,
            colorama.Fore.CYAN,
            colorama.Fore.WHITE,
            colorama.Fore.RED,
            colorama.Fore.GREEN,
        ]

        for i, preferences in enumerate(agents_prefs):
            a = ArgumentAgent(i, self, f"A{i+1}", preferences, available_colors[i])
            self.schedule.add(a)

        self.running = True
        self.step_count = 0

    def step(self):
        self.__messages_service.dispatch_messages()  # only needed if instant delivery is False
        self.schedule.step()
        self.step_count += 1
        if self.step_count == 4:
            self.running = False

    def get_message_history(self):
        history = self.__messages_service.get_message_history()
        return pd.DataFrame(history)


values_list = [
    Value.VERY_GOOD,
    Value.GOOD,
    Value.AVERAGE,
    Value.BAD,
    Value.VERY_BAD,
]


class TestArgumentation(unittest.TestCase):
    def test_scenario_1(self):
        """test scenario
        A1 to A2: propose(item)
        A2 to A1: accept (item)
        A1 to A2: commit (item)
        A2 to A1: commit (item)
        """
        agents_prefs = []  # list of agents agents_prefs

        # Agent1
        list_items = [
            Item("item1", ""),
            Item("item2", ""),
        ]
        list_criteria = [
            CriterionName.PRODUCTION_COST,
        ]
        criteria_values = [
            CriterionValue(list_items[0], list_criteria[0], values_list[0]),
            CriterionValue(list_items[1], list_criteria[0], values_list[4]),
        ]

        agents_prefs.append(Preferences(list_criteria, criteria_values))

        # Agent2
        agents_prefs.append(Preferences(list_criteria, criteria_values))

        argument_model = ArgumentModelTester(agents_prefs)
        argument_model.step()
        argument_model.step()
        history = argument_model.get_message_history()
        self.assertEqual(history.iloc[0].performative, MessagePerformative.PROPOSE)
        self.assertEqual(history.iloc[1].performative, MessagePerformative.ACCEPT)
        self.assertEqual(history.iloc[2].performative, MessagePerformative.COMMIT)
        self.assertEqual(history.iloc[3].performative, MessagePerformative.COMMIT)

    def test_scenario_2(self):
        """test scenario
        A1 to A2: propose(item)
        A2 to A1: ask_why(item)
        A1 to A2: argue(item, production = very_good)
        A2 to A1: argue(not item, production = very_bad)
        """
        agents_prefs = []  # list of agents agents_prefs

        list_items = [
            Item("item1", ""),
            Item("item2", ""),
        ]

        # Agent1
        list_criteria = [
            CriterionName.PRODUCTION_COST,
        ]
        criteria_values = [
            CriterionValue(list_items[0], list_criteria[0], values_list[0]),
            CriterionValue(list_items[1], list_criteria[0], values_list[4]),
        ]

        agents_prefs.append(Preferences(list_criteria, criteria_values))

        # Agent2
        criteria_values = [
            CriterionValue(list_items[0], list_criteria[0], values_list[4]),
            CriterionValue(list_items[1], list_criteria[0], values_list[2]),
        ]
        agents_prefs.append(Preferences(list_criteria, criteria_values))

        argument_model = ArgumentModelTester(agents_prefs)
        argument_model.step()
        argument_model.step()
        history = argument_model.get_message_history()
        self.assertEqual(history.iloc[0].performative, MessagePerformative.PROPOSE)
        self.assertEqual(history.iloc[1].performative, MessagePerformative.ASK_WHY)

        self.assertEqual(history.iloc[2].performative, MessagePerformative.ARGUE)
        self.assertEqual(history.iloc[2].decision, "pro")

        self.assertEqual(history.iloc[3].performative, MessagePerformative.ARGUE)
        self.assertEqual(history.iloc[3].decision, "con")

    def test_scenario_3(self):
        """test scenario
        A1 to A2: propose(item1)
        A2 to A1: ask_why(item1)
        A1 to A2: argue(item1, production=very_good)
        A2 to A1: argue(not item1, durability=very_bad and durability>production)
        """
        agents_prefs = []  # list of agents agents_prefs

        item1 = Item("item1", "")
        item2 = Item("item2", "")

        # Agent1
        list_criteria = [
            CriterionName.PRODUCTION_COST,
            CriterionName.DURABILITY,
        ]
        criteria_values = [
            CriterionValue(item1, CriterionName.PRODUCTION_COST, values_list[0]),
            CriterionValue(item1, CriterionName.DURABILITY, values_list[4]),
            CriterionValue(item2, CriterionName.PRODUCTION_COST, values_list[4]),
            CriterionValue(item2, CriterionName.DURABILITY, values_list[4]),
        ]

        agents_prefs.append(Preferences(list_criteria, criteria_values))

        # Agent2
        list_criteria = [
            CriterionName.DURABILITY,
            CriterionName.PRODUCTION_COST,
        ]
        criteria_values = [
            CriterionValue(item1, CriterionName.PRODUCTION_COST, values_list[0]),
            CriterionValue(item1, CriterionName.DURABILITY, values_list[4]),
            CriterionValue(item2, CriterionName.PRODUCTION_COST, values_list[4]),
            CriterionValue(item2, CriterionName.DURABILITY, values_list[0]),
        ]
        agents_prefs.append(Preferences(list_criteria, criteria_values))

        argument_model = ArgumentModelTester(agents_prefs)
        argument_model.step()
        argument_model.step()
        history = argument_model.get_message_history()

        self.assertEqual(
            list(history.iloc[0])[:4],
            ["A1", "A2", MessagePerformative.PROPOSE, "item1"],
        )
        self.assertEqual(
            list(history.iloc[1])[:4],
            ["A2", "A1", MessagePerformative.ASK_WHY, "item1"],
        )

        self.assertEqual(
            list(history.iloc[2]),
            ["A1", "A2", MessagePerformative.ARGUE, "item1", "pro", CriterionName.PRODUCTION_COST, Value.VERY_GOOD, None]
        )

        self.assertEqual(
            list(history.iloc[3]),
            ["A2", "A1", MessagePerformative.ARGUE, "item1", "con", CriterionName.DURABILITY, Value.VERY_BAD, CriterionName.PRODUCTION_COST]
        )


if __name__ == "__main__":
    colorama.init()  # INFO: used to print colored text on Windows
    logging.basicConfig(level=logging.DEBUG)
    logging.root.handlers = []
    unittest.main()
