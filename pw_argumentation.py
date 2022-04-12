from mesa import Model
from mesa.time import RandomActivation, BaseScheduler


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
import numpy as np
import copy
import logging
import colorama
from collections import defaultdict

global_arguments_dict = defaultdict(list)


class ArgumentAgent(CommunicatingAgent):
    """ArgumentAgent which inherit from CommunicatingAgent."""

    def __init__(self, unique_id, model, name, preferences, log_color):
        super().__init__(unique_id, model, name)
        self.preferences = preferences
        self.logger = self._init_logger(name, log_color)
        self.done_negotiating = False
        self.no_args_items = []  # items for which we have no arguments. We never propose those items again

    @staticmethod
    def _init_logger(name, log_color):
        logger = logging.getLogger(name)
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)

        formatter = logging.Formatter(f"{log_color}%(asctime)s - %(levelname)s - %(name)s >> %(message)s")
        console.setFormatter(formatter)
        logger.addHandler(console)
        return logger

    def step(self):
        super().step()  # TODO: check if this is needed
        messages = self.get_new_messages()
        if len(messages) == 0:
            # propose item
            item = self.preferences.most_preferred(exclude_list=self.no_args_items)
            if item:
                target = self.get_random_target()
                proposal = Message(
                    self.get_name(),
                    target.get_name(),
                    MessagePerformative.PROPOSE,
                    [item],
                )
                self.logger.info(f"No messages received. Proposing {item.get_name()} to {target.get_name()}")
                self.send_message(proposal)
            else:
                self.logger.info("No messages received. No items to propose.")
                self.done_negotiating = True
        else:
            for message in messages:
                if message.get_performative() == MessagePerformative.ACCEPT:
                    self.handle_accept(message)
                elif message.get_performative() == MessagePerformative.REJECT:
                    self.handle_reject(message)
                elif message.get_performative() == MessagePerformative.PROPOSE:
                    self.handle_propose(message)
                elif message.get_performative() == MessagePerformative.COMMIT:
                    self.handle_commit(message)
                elif message.get_performative() == MessagePerformative.ARGUE:
                    self.handle_argue(message)
                elif message.get_performative() == MessagePerformative.ASK_WHY:
                    self.handle_ask_why(message)
                else:
                    self.logger.warning(f"Unknown message received: {message.get_performative()}")

    def handle_argue(self, message):
        # item = message.get_content()[0]
        target_name = message.get_exp()
        argument = message.get_content()[1]
        item = (
            argument.get_item()
        )  # TODO: check this: basically we completely forget about the old item when we argue for a better alternative
        counter_argument = self.get_counter_argument(argument)
        if counter_argument:
            message = Message(
                self.get_name(),
                target_name,
                MessagePerformative.ARGUE,
                [item, counter_argument],  # TODO: Warning: item and counter_argument.item are not the same
            )
            self.logger.info(f"Received argument from {target_name}. Sending counter argument: {counter_argument}")
            global_arguments_dict[argument.get_item()].append(counter_argument)
            self.send_message(message)

        elif argument.get_conclusion()[1]:  # accept proposal
            message = Message(
                self.get_name(),
                target_name,
                MessagePerformative.ACCEPT,
                [item],
            )
            self.logger.info(f"Accepting proposal {item.get_name()} from {target_name} because no counter argument")
            self.send_message(message)

        else:  # reject item
            self.preferences.remove_item(item)
            self.logger.debug(f"Removed {item.get_name()} from preferences. New preferences: {self.preferences}")
            message = Message(
                self.get_name(),
                target_name,
                MessagePerformative.REJECT,
                [item],
            )
            self.logger.info(f"Rejecting my proposal {item.get_name()} because no counter argument")
            self.send_message(message)

    def handle_ask_why(self, message):
        item = message.get_content()[0]
        target_name = message.get_exp()
        argument = self.support_proposal(item)  # TODO: case where no supporting args
        if argument:
            message = Message(
                self.get_name(),
                target_name,
                MessagePerformative.ARGUE,
                [item, argument],
            )
            self.logger.info(f"Received ASK_WHY message from {target_name}. Giving argument:{argument}")
            global_arguments_dict[item].append(argument)
            self.send_message(message)
        else:
            # propose another item
            other_items = self.preferences.get_item_list().copy()
            other_items.remove(item)
            item = self.preferences.most_preferred(exclude_list=self.no_args_items)
            if item:
                proposal = Message(self.get_name(), target_name, MessagePerformative.PROPOSE, [item])
                self.logger.info(f"No args for previous item. Proposing new item: {item.get_name()} to {target_name}")
                self.send_message(proposal)
            else:
                self.logger.info(" No args for previous item. No more items to propose.")
                self.done_negotiating = True

    def handle_commit(self, message):
        item = message.get_content()[0]
        target_name = message.get_exp()
        message = Message(
            self.get_name(),
            None,
            MessagePerformative.COMMIT,
            [item],
        )
        self.logger.info(f"Received COMMIT message from {target_name}. Committing {item.get_name()}")
        self.send_message(message)
        self.preferences.remove_item(item)
        self.logger.debug(f"Removed {item.get_name()} from preferences. New preferences: {self.preferences}")
        self.done_negotiating = True

    def handle_accept(self, message):
        item = message.get_content()[0]
        target_name = message.get_exp()
        message = Message(
            self.get_name(),
            target_name,
            MessagePerformative.COMMIT,
            [item],
        )
        self.logger.info(f"Received ACCEPT message from {target_name}. Committing {item.get_name()}")
        self.send_message(message)
        self.preferences.remove_item(item)
        self.logger.debug(f"Removed {item.get_name()} from preferences. New preferences: {self.preferences}")
        self.done_negotiating = True

    def handle_reject(self, message):
        item = message.get_content()[0]
        target_name = message.get_exp()
        self.preferences.remove_item(item)
        self.logger.debug(f"Removed {item.get_name()} from preferences. New preferences: {self.preferences}")

        # propose new item
        item = self.preferences.most_preferred(exclude_list=self.no_args_items)
        if item:
            proposal = Message(
                self.get_name(),
                target_name,
                MessagePerformative.PROPOSE,
                [item],
            )
            self.logger.info(
                f"Received REJECT message from {target_name}. Proposing {item.get_name()} to {target_name}"
            )
            self.send_message(proposal)
        else:
            self.logger.info(f"Received REJECT message from {target_name}. No items to propose.")
            self.done_negotiating = True

    def handle_propose(self, message):
        """Accepts proposal if item is among top 10 preferred items, otherwise asks why."""
        target_name = message.get_exp()
        item = message.get_content()[0]
        PERCENT = 10
        if self.preferences.is_item_among_top_x_percent(item, PERCENT):
            message = Message(
                self.get_name(),
                target_name,
                MessagePerformative.ACCEPT,
                [item],
            )
            self.logger.info(
                f"Accepting proposal {item.get_name()} from {target_name} because it is among top {PERCENT}%"
            )
        else:
            message = Message(
                self.get_name(),
                target_name,
                MessagePerformative.ASK_WHY,
                [item],
            )
            self.logger.info(f"Asking why {item.get_name()} from {target_name}")
        self.send_message(message)

    def get_random_target(self):
        return self.random.choice(
            [agent for agent in self.model.schedule.agents if agent.get_name() != self.get_name()]
        )

    def get_preference(self):
        return self.preferences

    def generate_random_preferences(self, list_items=None):
        if list_items is None or len(list_items) == 0:
            list_items = [
                Item("Engine 1"),
                Item("Engine 2"),
                Item("Engine 3"),
                Item("Engine 4"),
                Item("Engine 5"),
            ]

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
                agent_pref.add_criterion_value(CriterionValue(item, criterion_name, rd.choice(values_list)))

        self.preferences = agent_pref

    def import_preferences(self, preferences):
        self.preferences = preferences

    def List_supporting_proposal(self, item):
        """Generate a list of arguments which can be used to support an item
        :param item: Item - name of the item
        :return: list of all arguments PRO an item (sorted by order of importance based on agent's preferences)
        """
        arg_list = []

        # iterate through all criteria (ordered by importance)
        criterion_name_list = self.preferences.get_criterion_name_list()
        for i, crit_name in enumerate(criterion_name_list):
            value = self.preferences.get_value(item, crit_name)
            if value in [Value.VERY_GOOD, Value.GOOD]:
                # add arg of type ARGUE(E <= Environment Impact=Very Good)
                arg = Argument(True, item)
                arg.add_premise_couple_values(crit_name, value)
                arg_list.append(arg)

                # iterate through the less important criteria
                if i < len(criterion_name_list) - 1:
                    for worst_crit_name in criterion_name_list[i + 1 :]:
                        # add arg of type ARGUE(E <= Noise=Very Good, Noise > Cost)
                        arg = Argument(True, item)
                        arg.add_premise_couple_values(crit_name, value)
                        arg.add_premise_comparison(crit_name, worst_crit_name)
                        arg_list.append(arg)
        return arg_list

    def List_attacking_proposal(self, item):
        """Generate a list of arguments which can be used to attack an item
        :param item: Item - name of the item
        :return: list of all arguments CON an item (sorted by order of importance based on preferences)
        """
        arg_list = []

        # iterate through all criteria (ordered by importance)
        criterion_name_list = self.preferences.get_criterion_name_list()
        for i, crit_name in enumerate(criterion_name_list):
            value = self.preferences.get_value(item, crit_name)
            if value in [Value.VERY_BAD, Value.BAD]:
                # add arg of type ARGUE(not E <= Environment Impact=Very Bad)
                arg = Argument(False, item)
                arg.add_premise_couple_values(crit_name, value)
                arg_list.append(arg)

                # iterate through the less important criteria
                if i < len(criterion_name_list) - 1:
                    for worst_crit_name in criterion_name_list[i + 1 :]:
                        # add arg of type ARGUE(not E <= Noise=Very Bad, Noise > Cost)
                        arg = Argument(False, item)
                        arg.add_premise_couple_values(crit_name, value)
                        arg.add_premise_comparison(crit_name, worst_crit_name)
                        arg_list.append(arg)
        return arg_list

    def support_proposal(self, item):
        """Used when the agent receives " ASK_WHY " after having proposed an item
        :param item: str - name of the item which was proposed
        :return: string - the strongest supportive argument
        """
        arg_list = self.List_supporting_proposal(item)
        if len(arg_list) == 0:
            self.logger.debug(
                f"Agent {self.get_name()} received ASK_WHY message but has no arguments to support {item}"
            )
            self.no_args_items.append(item)
            return None
        return arg_list[0]

    def argument_parsing(self, argument):
        """Parses an argument and returns its premises and its conclusion"""
        item, decision = argument.get_conclusion()
        criterion, prev_worst_criterion = argument.get_comparison()
        criterion, x = argument.get_couple_value()
        return (item, decision, criterion, x, prev_worst_criterion)

    def get_counter_argument(self, argument):
        """Returns a counter argument such as:
        1. the agent has a better alternative on the same criterion or a more important criterion
        2. the agent thinks badly of this item on the same or a more important criterion
        """
        item, decision = argument.get_conclusion()
        criterion, prev_worst_criterion = argument.get_comparison()
        criterion, x = argument.get_couple_value()

        if criterion not in self.preferences.get_criterion_name_list():
            self.logger.debug(f"Received an argument with a criterion not in the agent's preferences: {criterion}")
            return None

        if decision is True:  # received PRO argument
            # iterate through better criteria (assume agents have same criteria)
            for better_criterion in self.preferences.get_preferred_criteria(criterion):
                if (
                    prev_worst_criterion != better_criterion
                ):  # TODO try to avoid loop by giving the same previously rejected criterion
                    # has bad evaluation on more important criterion
                    y = self.preferences.get_value(item, better_criterion)
                    if y in [
                        Value.VERY_BAD,
                        Value.BAD,
                    ]:  # TODO: could be replaced with y < x
                        arg = Argument(False, item)
                        arg.add_premise_couple_values(better_criterion, y)
                        arg.add_premise_comparison(better_criterion, criterion)
                        if arg not in global_arguments_dict[item]:
                            return arg  # argue(not oi, cj = y with y is worst than x, cj > ci)

            # check for better alternative on same criterion
            for alternative in self.preferences.get_item_list():
                y = self.preferences.get_value(alternative, criterion)
                if alternative != item and y and y.value > x.value:
                    arg = Argument(True, alternative)  # TODO: Argument(False, item) ??
                    arg.add_premise_couple_values(criterion, y)
                    if arg not in global_arguments_dict[item]:
                        return arg  # argue(oj , ci = y, y is better than x) TODO: handle counter argument of this case

            # check for bad evaluation on same criterion
            if self.preferences.get_value(item, criterion) in [
                Value.VERY_BAD,
                Value.BAD,
            ]:
                arg = Argument(False, item)
                arg.add_premise_couple_values(criterion, self.preferences.get_value(item, criterion))
                if arg not in global_arguments_dict[item]:
                    return arg  # argue(not oi, ci = y, y is worst than x)
        else:  # received CON argument
            # TODO: problem: not agreeing on evaluations/preferences can lead to loops

            # iterate through better criteria (assume agents have same criteria)
            for better_criterion in self.preferences.get_preferred_criteria(criterion):
                if (
                    prev_worst_criterion != better_criterion
                ):  # TODO try to avoid loop by giving the same previously rejected criterion
                    # has good evaluation on more important criterion
                    y = self.preferences.get_value(item, better_criterion)
                    if y in [
                        Value.VERY_GOOD,
                        Value.GOOD,
                    ]:
                        arg = Argument(True, item)
                        arg.add_premise_couple_values(better_criterion, y)
                        arg.add_premise_comparison(better_criterion, criterion)
                        if arg not in global_arguments_dict[item]:
                            return arg  # argue(oi, cj = y with y is better than x, cj > ci)

            # check for better alternative on same criterion
            # for alternative in self.preferences.get_item_list():
            #     y = self.preferences.get_value(alternative, criterion)
            #     if alternative != item and y and y.value > x.value:
            #         arg = Argument(True, item)
            #         arg.add_premise_couple_values(criterion, y)
            #         if arg not in global_arguments_dict[item]:
            #             return arg  # argue(oj , ci = y, y is better than x)

            # check for good evaluation on same criterion
            if self.preferences.get_value(item, criterion) in [
                Value.VERY_GOOD,
                Value.GOOD,
            ]:
                arg = Argument(True, item)
                arg.add_premise_couple_values(criterion, self.preferences.get_value(item, criterion))
                if arg not in global_arguments_dict[item]:
                    return arg  # argue(not oi, ci = y, y is better than x)


class ArgumentModel(Model):
    """ArgumentModel which inherit from Model."""

    def __init__(self, agents_prefs=None, agent_names=None):
        global global_arguments_dict
        self.schedule = BaseScheduler(self)  # RandomActivation(self)
        self.agents = []

        MessageService.clear_instance()  # clears old MessageService singleton
        self.__messages_service = MessageService(self.schedule)

        # clear global_arguments_dict
        global_arguments_dict = defaultdict(list)

        available_colors = [
            colorama.Fore.YELLOW,
            colorama.Fore.BLUE,
            colorama.Fore.MAGENTA,
            colorama.Fore.CYAN,
            colorama.Fore.WHITE,
            colorama.Fore.RED,
            colorama.Fore.GREEN,
        ]

        if agents_prefs is None or len(agents_prefs) == 0:
            for i, agent_name in enumerate(["Bob", "Alice"]):
                a = ArgumentAgent(i, self, agent_name, Preferences(), available_colors[i])
                a.generate_random_preferences()
                self.agents.append(a)
                self.schedule.add(a)
        else:
            # deepcopy agents_prefs
            agents_prefs = copy.deepcopy(agents_prefs)

            for i, preferences in enumerate(agents_prefs):
                if agent_names is None or len(agent_names) == 0:
                    agent_name = f"A{i+1}"
                else:
                    agent_name = agent_names[i]
                a = ArgumentAgent(i, self, agent_name, preferences, available_colors[i])
                self.agents.append(a)
                self.schedule.add(a)
        self.running = True
        self.step_count = 0

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()
        self.step_count += 1
        if all(agent.done_negotiating for agent in self.agents):
            self.running = False
        if self.step_count == 100:
            self.running = False

    def get_message_history(self):
        history = self.__messages_service.get_message_history()
        return pd.DataFrame(history)

    def get_final_result(self):
        history = self.__messages_service.get_message_history()
        results = {}
        for i in range(len(history) - 1, -1, -1):
            if history[i]["performative"] == MessagePerformative.ACCEPT:
                results["winning_agent"] = history[i]["receiver"]
                results["winning_item"] = history[i]["item"]
                if history[i - 1]["performative"] == MessagePerformative.ARGUE:
                    results["winning_argument"] = {
                        "item": history[i - 1]["item"],
                        "decision": history[i - 1]["decision"],
                        "main_criterion": history[i - 1]["main_criterion"],
                        "value": history[i - 1]["value"],
                        "secondary_criterion": history[i - 1]["secondary_criterion"],
                    }
                    return results, pd.DataFrame(history)
                results["winning_argument"] = {
                    "item": history[i - 1]["item"],
                    "decision": "top_10_percent",
                }
                return results, pd.DataFrame(history)
            elif history[i]["performative"] == MessagePerformative.REJECT:
                results["winning_agent"] = history[i]["receiver"]
                results["winning_item"] = None
                if history[i - 1]["performative"] == MessagePerformative.ARGUE:
                    results["winning_argument"] = {
                        "item": history[i - 1]["item"],
                        "decision": history[i - 1]["decision"],
                        "main_criterion": history[i - 1]["main_criterion"],
                        "value": history[i - 1]["value"],
                        "secondary_criterion": history[i - 1]["secondary_criterion"],
                    }
                    return results, pd.DataFrame(history)
        return None, pd.DataFrame(history)


def format_argument(arg):
    if arg["decision"] == "top_10_percent":
        return f"{arg['item']} is among top 10% most preferred items for agent"
    s = f"{'not ' if arg['decision']=='con' else ''}{arg['item']}, "
    if arg["secondary_criterion"] is not None:
        s += f"{arg['main_criterion'].name}=={arg['value'].name} and {arg['main_criterion'].name}>{arg['secondary_criterion'].name}"
    else:
        s += f"{arg['main_criterion'].name}=={arg['value'].name}"
    return s


def generate_pref_df(n_items=2, n_crit=len(CriterionName), n_values=len(Value), drop_prefs=False):
    # generate preferences
    df = pd.DataFrame(np.random.randint(0, n_values, size=(n_items, n_crit)))
    # shuffle agent criteria preference order
    df.columns = np.random.permutation(df.columns)
    # drop random number of preferences
    if drop_prefs:
        df = df.drop(columns=np.random.choice(df.columns, size=np.random.randint(0, len(df.columns)), replace=False))
    return df


def generate_preferences(n_items=2, n_crit=len(CriterionName), n_values=len(Value), drop_prefs=False):
    df = generate_pref_df(n_items=n_items, n_crit=n_crit, n_values=n_values, drop_prefs=drop_prefs)
    list_criteria = []
    criteria_values = []
    for i, row in df.iterrows():
        for j, val in row.iteritems():
            list_criteria.append(CriterionName(j))
            criteria_values.append(CriterionValue(Item(f"item{i+1}"), CriterionName(j), Value(val)))
            df.rename(columns={j: CriterionName(j).name}, inplace=True)
        df.rename(index={i: Item(f"item{i+1}")}, inplace=True)

    rd.shuffle(criteria_values)  # avoid order bias on items for arguments
    return Preferences(list_criteria, criteria_values), df


if __name__ == "__main__":
    colorama.init()  # INFO: used to print colored text on Windows
    logging.basicConfig(level=logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR
    logging.root.handlers = []

    # generate preferences
    print()
    prefs_1, df1 = generate_preferences()
    print("Agent 1 preferences:")
    print(df1)
    print("-" * 100)
    prefs_2, df2 = generate_preferences()
    print("Agent 2 preferences:")
    print(df2)
    print("-" * 100)

    argument_model = ArgumentModel([prefs_1, prefs_2])
    argument_model.run_model()

    results, history = argument_model.get_final_result()
    print("Results:")
    if results:
        print("\tWinning agent:", results["winning_agent"])
        print("\tWinning item:", results["winning_item"])
        print("\tWinning argument:", format_argument(results["winning_argument"]))
    else:
        print("No winner")

    print()
    print(history)
