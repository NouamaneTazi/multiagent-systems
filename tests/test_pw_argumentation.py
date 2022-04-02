import unittest
from typing import Dict, List, Tuple

from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value
from communication.preferences.Preferences import Preferences


class TestArgumentation(unittest.TestCase):
    def setUp(self):
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
            CriterionValue(
                diesel_engine, CriterionName.PRODUCTION_COST, Value.VERY_GOOD
            )
        )
        agent_pref.add_criterion_value(
            CriterionValue(diesel_engine, CriterionName.CONSUMPTION, Value.GOOD)
        )
        agent_pref.add_criterion_value(
            CriterionValue(diesel_engine, CriterionName.DURABILITY, Value.VERY_GOOD)
        )
        agent_pref.add_criterion_value(
            CriterionValue(
                diesel_engine, CriterionName.ENVIRONMENT_IMPACT, Value.VERY_BAD
            )
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

        self.agent_pref = agent_pref
        self.items = {
            "diesel_engine": diesel_engine,
            "electric_engine": electric_engine,
        }

    def test_perf_get_value(self):
        """test get_value performance method"""
        diesel_engine = self.items["diesel_engine"]
        self.assertEqual(
            diesel_engine.get_value(self.agent_pref, CriterionName.PRODUCTION_COST),
            Value.VERY_GOOD,
        )


if __name__ == "__main__":
    unittest.main()
