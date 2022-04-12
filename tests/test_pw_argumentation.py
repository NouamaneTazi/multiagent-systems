import logging
import unittest
import colorama

from communication.message.MessagePerformative import MessagePerformative
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Preferences import Preferences
from communication.preferences.Value import Value
from pw_argumentation import ArgumentModel

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
        A2 to A1: accept (item) # because top 10%
        A1 to A2: commit (item)
        A2 to A1: commit (item)
        """
        agents_prefs = []  # list of agents agents_prefs

        # Agent1
        list_items = [Item(f"item{i}", "") for i in range(1, 11)]
        list_criteria = [
            CriterionName.PRODUCTION_COST,
        ]
        criteria_values = [
            CriterionValue(list_items[0], list_criteria[0], values_list[0]),
        ]
        for i in range(1, 10):
            criteria_values.append(CriterionValue(list_items[i], list_criteria[0], values_list[4]))

        agents_prefs.append(Preferences(list_criteria, criteria_values))

        # Agent2
        agents_prefs.append(Preferences(list_criteria, criteria_values))

        argument_model = ArgumentModel(agents_prefs)
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

        argument_model = ArgumentModel(agents_prefs)
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

        argument_model = ArgumentModel(agents_prefs)
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
            [
                "A1",
                "A2",
                MessagePerformative.ARGUE,
                "item1",
                "pro",
                CriterionName.PRODUCTION_COST,
                Value.VERY_GOOD,
                None,
            ],
        )

        self.assertEqual(
            list(history.iloc[3]),
            [
                "A2",
                "A1",
                MessagePerformative.ARGUE,
                "item1",
                "con",
                CriterionName.DURABILITY,
                Value.VERY_BAD,
                CriterionName.PRODUCTION_COST,
            ],
        )

    def test_scenario_4(self):
        """test scenario
        A1 to A2: propose(item1)
        A2 to A1: ask_why(item1)
        A1 to A2: argue(item1, production=good)
        A2 to A1: argue(item2, production=very_good)
        """
        agents_prefs = []  # list of agents agents_prefs

        item1 = Item("item1", "")
        item2 = Item("item2", "")

        # Agent1
        list_criteria = [
            CriterionName.PRODUCTION_COST,
        ]
        criteria_values = [
            CriterionValue(item1, CriterionName.PRODUCTION_COST, Value.GOOD),
            CriterionValue(item2, CriterionName.PRODUCTION_COST, Value.VERY_BAD),
        ]

        agents_prefs.append(Preferences(list_criteria, criteria_values))

        # Agent2
        criteria_values = [
            CriterionValue(item1, CriterionName.PRODUCTION_COST, Value.GOOD),
            CriterionValue(item2, CriterionName.PRODUCTION_COST, Value.VERY_GOOD),
        ]
        agents_prefs.append(Preferences(list_criteria, criteria_values))

        argument_model = ArgumentModel(agents_prefs)
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
            ["A1", "A2", MessagePerformative.ARGUE, "item1", "pro", CriterionName.PRODUCTION_COST, Value.GOOD, None],
        )

        self.assertEqual(
            list(history.iloc[3]),
            [
                "A2",
                "A1",
                MessagePerformative.ARGUE,
                "item2",
                "pro",
                CriterionName.PRODUCTION_COST,
                Value.VERY_GOOD,
                None,
            ],
        )


if __name__ == "__main__":
    colorama.init()  # INFO: used to print colored text on Windows
    logging.basicConfig(level=logging.DEBUG)
    logging.root.handlers = []
    unittest.main()
