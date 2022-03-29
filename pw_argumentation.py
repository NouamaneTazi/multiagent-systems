from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences.Preferences import Preferences
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value

import random as rd


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent."""

    def __init__(self, unique_id, model, name, preferences):
        super().__init__(unique_id, model, name)
        self.preferences = None

    def step(self):
        super().step()

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

        for i, agent_name in ["Bob", "Alice"]:
            a = ArgumentAgent(i, self, agent_name, Preferences())
            a.generate_preferences(list_items)
            self.schedule.add(a)

        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()


if __name__ == "__main__":
    argument_model = ArgumentModel()

    # To be completed
