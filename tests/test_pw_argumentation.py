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


class TestArgumentModel(Model):
    """ArgumentModel which inherit from Model."""

    def __init__(self):
        self.schedule = BaseScheduler(self)  # RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)

        list_items = [
            Item("Diesel Engine", "A super cool diesel engine"),
            Item("Electric Engine", "A very quiet engine"),
        ]
        available_colors = [
            colorama.Fore.YELLOW,
            colorama.Fore.BLUE,
            colorama.Fore.MAGENTA,
            colorama.Fore.CYAN,
            colorama.Fore.WHITE,
            colorama.Fore.RED,
            colorama.Fore.GREEN,
        ]

        for i, agent_name in enumerate(["Bob", "Alice"]):
            a = ArgumentAgent(i, self, agent_name, Preferences(), available_colors[i])
            a.generate_preferences(list_items)
            self.schedule.add(a)

        self.running = True
        self.step_count = 0

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()
        self.step_count += 1
        if self.step_count == 4:
            self.running = False

    def get_message_history(self):
        history = self.__messages_service.get_message_history()
        return pd.DataFrame(history)


class TestArgumentation(unittest.TestCase):
    def setUp(self):
        colorama.init()  # INFO: used to print colored text on Windows
        logging.basicConfig(level=logging.DEBUG)
        logging.root.handlers = []

    def test_perf_get_value(self):
        """test get_value performance method"""
        argument_model = TestArgumentModel()
        argument_model.run_model()


if __name__ == "__main__":
    unittest.main()
