from mesa import Model
from mesa.time import RandomActivation


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


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent."""

    def __init__(self, unique_id, model, name, preferences):
        super().__init__(unique_id, model, name)
        self.preferences = None
        self.logger = self._init_logger(name)

    @staticmethod
    def _init_logger(name):
        logger = logging.getLogger(name)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s >> %(message)s"
        )
        console.setFormatter(formatter)
        logger.addHandler(console)
        return logger

    def step(self):
        super().step()
        messages = self.get_new_messages()
        if len(messages) == 0:
            # propose item
            item = self.preferences.most_preferred()
            target = self.get_random_target()
            proposal = Message(
                self.get_name(), target.get_name(), MessagePerformative.PROPOSE, [item]
            )
            self.logger.info(
                f"No messages received. Proposing {item.get_name()} to {target.get_name()}"
            )
            self.send_message(proposal)
        else:
            for message in messages:
                if message.get_performative() == MessagePerformative.ACCEPT:
                    self.logger.info(
                        "Item accepted: " + message.get_content()[0].get_name()
                    )
                elif message.get_performative() == MessagePerformative.PROPOSE:
                    item = message.get_content()[0]
                    # accept proposal
                    target = self.get_random_target()
                    accept = Message(
                        self.get_name(),
                        target.get_name(),
                        MessagePerformative.ACCEPT,
                        [message.get_content()[0]],
                    )
                    self.logger.info(
                        f"Accepting proposal {item.get_name()} from {message.get_exp()}"
                    )
                    self.send_message(accept)
                else:
                    self.logger.warning(
                        "Unknown message received: " + message.get_performative()
                    )

    def get_random_target(self):
        return self.random.choice(
            [
                agent
                for agent in self.model.schedule.agents
                if agent.get_name() != self.get_name()
            ]
        )

    def get_preference(self):
        return self.preferences

    def generate_preferences(self, list_items):

        list_criteria = [
            CriterionName.PRODUCTION_COST,
            CriterionName.ENVIRONMENT_IMPACT,
            CriterionName.CONSUMPTION,
            CriterionName.DURABILITY,
            CriterionName.NOISE,
        ]

        values_list = [
            Value.VERY_GOOD,
            Value.GOOD,
            Value.AVERAGE,
            Value.BAD,
            Value.VERY_BAD,
        ]

        # Select random subsets of criteria
        criteria_subset = rd.sample(list_criteria, rd.randint(1, len(list_criteria)))

        agent_pref = Preferences()
        agent_pref.set_criterion_name_list(criteria_subset)

        for item in list_items:
            # Add a random value for each criterion
            for criterion_name in criteria_subset:
                agent_pref.add_criterion_value(
                    CriterionValue(item, criterion_name, rd.choice(values_list))
                )

        self.preferences = agent_pref


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model."""

    def __init__(self):
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)

        # To be completed
        list_items = [
            Item("Diesel Engine", "A super cool diesel engine"),
            Item("Electric Engine", "A very quiet engine"),
        ]

        for i, agent_name in enumerate(["Bob", "Alice"]):
            a = ArgumentAgent(i, self, agent_name, Preferences())
            a.generate_preferences(list_items)
            self.schedule.add(a)

        self.running = True
        self.step_count = 0

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()
        self.step_count += 1
        if self.step_count == 2:
            self.running = False

    def get_message_history(self):
        history = self.__messages_service.get_message_history()
        return pd.DataFrame(history)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.root.handlers = []
    argument_model = ArgumentModel()
    argument_model.run_model()
