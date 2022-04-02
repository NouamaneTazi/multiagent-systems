import unittest
from typing import Dict, List, Tuple

from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value
from communication.preferences.Preferences import Preferences


class TestPreferences(unittest.TestCase):
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

    def test_is_preferred_criterion(self):
        """test is_preferred_criterion method"""
        agent_pref = self.agent_pref

        self.assertTrue(
            agent_pref.is_preferred_criterion(
                CriterionName.CONSUMPTION, CriterionName.NOISE
            )
        )
        self.assertFalse(
            agent_pref.is_preferred_criterion(
                CriterionName.CONSUMPTION, CriterionName.PRODUCTION_COST
            )
        )

    def test_is_preferred_item(self):
        """test is_preferred_item method"""
        diesel_engine = self.items["diesel_engine"]
        electric_engine = self.items["electric_engine"]
        agent_pref = self.agent_pref

        self.assertTrue(agent_pref.is_preferred_item(diesel_engine, electric_engine))
        self.assertFalse(agent_pref.is_preferred_item(electric_engine, diesel_engine))

    def test_get_score(self):
        """test get_score method"""
        diesel_engine = self.items["diesel_engine"]
        electric_engine = self.items["electric_engine"]
        agent_pref = self.agent_pref

        self.assertEqual(electric_engine.get_score(agent_pref), 362.5)
        self.assertEqual(diesel_engine.get_score(agent_pref), 525.0)

    def test_most_preferred(self):
        """test most_preferred method"""
        agent_pref = self.agent_pref
        diesel_engine = self.items["diesel_engine"]
        electric_engine = self.items["electric_engine"]

        self.assertEqual(
            agent_pref.most_preferred([diesel_engine, electric_engine]), diesel_engine
        )

    def test_is_item_among_top_10_percent(self):
        """test is_item_among_top_10_percent method"""
        agent_pref = self.agent_pref
        diesel_engine = self.items["diesel_engine"]
        electric_engine = self.items["electric_engine"]

        self.assertFalse(agent_pref.is_item_among_top_10_percent(diesel_engine))
        self.assertFalse(agent_pref.is_item_among_top_10_percent(electric_engine))

    def test_is_item_among_top_50_percent(self):
        """test is_item_among_top_50_percent method"""
        agent_pref = self.agent_pref
        diesel_engine = self.items["diesel_engine"]
        electric_engine = self.items["electric_engine"]

        self.assertTrue(agent_pref.is_item_among_top_x_percent(diesel_engine, 50))
        self.assertFalse(agent_pref.is_item_among_top_x_percent(electric_engine, 50))


if __name__ == "__main__":
    unittest.main()
