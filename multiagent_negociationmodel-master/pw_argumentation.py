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

class ArgumentAgent(CommunicatingAgent):
    """ TestAgent which inherit from CommunicatingAgent.
    """
    def __init__(self, unique_id, model, name, list_items):
        super().__init__(unique_id, model, name)
        self.preferences = None
        self.list_items = list_items
        self.proposed_items = []
        self.accepted_items = []
        self.commited_items = []
        self.arguments_for_dict = {}

        self.is_discussing = False

    def step(self):
        super().step()
        messages = self.get_new_messages()
        answer = None
        
        if len(self.list_items)>0:

            if len(messages) > 0:
                self.is_discussing = True
                message = messages[0]
                answer = self.answer(message)
                if answer:
                    self.send_message(answer)

            elif not self.is_discussing:
                self.is_discussing = True
                target = self.random.choice(self.model.schedule.agents)
                while target.unique_id == self.unique_id:
                    target = self.random.choice(self.model.schedule.agents)

                proposal = self.propose_item(target.get_name())
                self.send_message(proposal)

    def propose_item(self, target_name):
        item = self.preferences.most_preferred(self.list_items)
        proposal = Message(self.get_name(), target_name,
                           MessagePerformative.PROPOSE, [item])
        self.proposed_items.append(item)
        return proposal
    

    def support_proposal(self, item):
        argument = self.arguments_for_dict[item.get_name()][0]
        self.arguments_for_dict[item.get_name()] = self.arguments_for_dict[item.get_name()][1:].copy()

        return argument


    def argument_parsing(self, argument):
        return argument.get_decision()

    def is_good_argument(self, argument_received, argument_to_send):

        couple_value_received = argument_received.get_couple_values_list()[0]
        main_criterium_name_received = couple_value_received.get_criterion_name()

        couple_value_to_send = argument_to_send.get_couple_values_list()[0]
        comparisons_list_to_send = argument_to_send.get_comparision_list()
        main_criterium_name_to_send = couple_value_to_send.get_criterion_name()

        sec_criterium_name_to_send = None

        if len(comparisons_list_to_send)>0:
            comparison_to_send = comparisons_list_to_send[0]
            sec_criterium_name_to_send = comparison_to_send.get_worst_criterion_name()

        if (main_criterium_name_to_send == main_criterium_name_received) or (sec_criterium_name_to_send == main_criterium_name_received):
            return True

        else:
            return False

    def contradict_test(self, item, argument_received):
        agree = True
        decision_received = argument_received.get_decision()

        if decision_received==True:
            for arg in self.arguments_against_dict[item.get_name()]:
                if self.is_good_argument(argument_received, arg):
                    agree = False
                    self.arguments_against_dict[item.get_name()].remove(arg)

                    return (agree, arg)

        elif decision_received==False:
            for arg in self.arguments_for_dict[item.get_name()]:
                if self.is_good_argument(argument_received, arg):
                    agree = False
                    self.arguments_for_dict[item.get_name()].remove(arg)

                    return (agree, arg)
                
        return (agree, argument_received)

    def contradict(self, item, argument_received):
        agree = True
        argument = None
        decision_received = argument_received.get_decision()
        couple_values_received = argument_received.get_couple_values_list()[0]
        comparison_list_received = argument_received.get_comparision_list()

        if decision_received==True:
            criterium_name_1 = couple_values_received.get_criterion_name()
            if item.get_value(self.preferences, criterium_name_1) in [Value.BAD, Value.VERY_BAD]:
                agree = False
                argument = Argument(False, item)
                argument.add_premiss_couple_values(criterium_name_1, item.get_value(self.preferences, criterium_name_1))
                return (agree, argument)
            
            else:
                remaining_criterion_names = self.preferences.get_criterion_name_list().copy()
                remaining_criterion_names.remove(criterium_name_1)
                for criterium_name_2 in remaining_criterion_names:
                    if self.preferences.is_preferred_criterion(criterium_name_2, criterium_name_1):
                        if item.get_value(self.preferences, criterium_name_2) in [Value.BAD, Value.VERY_BAD]:
                            agree = False
                            argument = Argument(False, item)
                            argument.add_premiss_couple_values(criterium_name_2, item.get_value(self.preferences, criterium_name_2))
                            argument.add_premiss_comparison(criterium_name_2, criterium_name_1)
                            return (agree, argument)

        elif decision_received==False:
            criterium_name_1 = couple_values_received.get_criterion_name()
            if item.get_value(self.preferences, criterium_name_1) in [Value.GOOD, Value.VERY_GOOD]:
                agree = False
                argument = Argument(True, item)
                argument.add_premiss_couple_values(criterium_name_1, item.get_value(self.preferences, criterium_name_1))
                return (agree, argument)
            
            else:
                remaining_criterion_names = self.preferences.get_criterion_name_list().copy()
                remaining_criterion_names.remove(criterium_name_1)
                for criterium_name_2 in remaining_criterion_names:
                    if self.preferences.is_preferred_criterion(criterium_name_2, criterium_name_1):
                        if item.get_value(self.preferences, criterium_name_2) in [Value.GOOD, Value.VERY_GOOD]:
                            agree = False
                            argument = Argument(True, item)
                            argument.add_premiss_couple_values(criterium_name_2, item.get_value(self.preferences, criterium_name_2))
                            argument.add_premiss_comparison(criterium_name_2, criterium_name_1)
                            return (agree, argument)
                    
        return (agree, argument)

    def answer(self, message):
        sender = message.get_exp()
        message_type = message.get_performative()
        item = message.get_content()[0]

        if message_type == MessagePerformative.PROPOSE:
            if self.preferences.is_item_among_top_10_percent(item, self.list_items):
                answer = Message(self.get_name(), sender, MessagePerformative.ACCEPT, [item])
                self.accepted_items.append(item)
            else:
                answer = Message(self.get_name(), sender, MessagePerformative.ASK_WHY, [item])
            
        elif message_type == MessagePerformative.ASK_WHY:
            argument = self.support_proposal(item)
            answer = Message(self.get_name(), sender, MessagePerformative.ARGUE, [item, argument])
            
        elif message_type == MessagePerformative.ARGUE:
            argument = message.get_content()[1]
            agree, argument = self.contradict_test(item, argument)

            if agree:
                if argument.get_decision():
                    self.accepted_items.append(item)
                    answer = Message(self.get_name(), sender, MessagePerformative.ACCEPT, [item])
                
                else:
                    self.is_discussing = False
                    self.list_items = [item_ for item_ in self.list_items if item_!= item]
                    answer = Message(self.get_name(), sender, MessagePerformative.REJECT, [item])

            else:
                answer = Message(self.get_name(), sender, MessagePerformative.ARGUE, [item, argument])

        elif message_type == MessagePerformative.ACCEPT:

            if item in self.proposed_items:
                answer = Message(self.get_name(), sender, MessagePerformative.COMMIT, [item])
                self.proposed_items.remove(item)
                self.commited_items.append(item)

        elif message_type == MessagePerformative.REJECT:
            self.is_discussing = False
            self.list_items = [item_ for item_ in self.list_items if item_!= item]
            answer = None

        elif message_type == MessagePerformative.COMMIT:
            if item in self.accepted_items:
                self.is_discussing = False
                answer = Message(self.get_name(), sender, MessagePerformative.COMMIT, [item])
                self.commited_items.append(item)
                self.accepted_items.remove(item)
                self.list_items = [item_ for item_ in self.list_items if item_!= item]

            elif item in self.commited_items:
                self.is_discussing = False
                self.commited_items.remove(item)
                self.list_items = [item_ for item_ in self.list_items if item_!= item]
                answer = None

        return answer


    def get_preference(self):
        return self.preferences


    def set_preference(self, preferences):
        self.preferences = preferences

    def generate_arguments(self):

        for item in self.list_items:
            self.arguments_for_dict[item.get_name()] = self.List_supporting_proposal(item)

        self.arguments_against_dict = {}
        for item in self.list_items:
            self.arguments_against_dict[item.get_name()] = self.List_attacking_proposal(item)


    def generate_preferences(self, items_list):

        values_list = [Value.VERY_GOOD, Value.GOOD, Value.AVERAGE, Value.BAD, Value.VERY_BAD]

        criterion_list = [CriterionName.PRODUCTION_COST, CriterionName.ENVIRONMENT_IMPACT,
                          CriterionName.CONSUMPTION, CriterionName.DURABILITY,
                          CriterionName.NOISE]
        rd.shuffle(criterion_list)

        agent_pref = Preferences()
        agent_pref.set_criterion_name_list(criterion_list)
        
        for item in items_list:
            for criterion in agent_pref.get_criterion_name_list():
                value = rd.choice(values_list)
                agent_pref.add_criterion_value(CriterionValue(item, criterion, value))
                #print(item.get_name(), criterion, value)

        self.preferences = agent_pref


    def List_supporting_proposal(self, item):
        """Generate a list of arguments which can be used to support an item
        :param item: Item - name of the item
        :return: list of all arguments PRO an item (sorted by order of importance based on agent's preferences)
        """
        arg_list = []

        for criterion_name_1 in self.preferences.get_criterion_name_list():
            remaining_criterion_names = self.preferences.get_criterion_name_list().copy()
            remaining_criterion_names.remove(criterion_name_1)
            value = self.preferences.get_value(item, criterion_name_1)

            if value == Value.VERY_GOOD:
                arg = Argument(True, item)
                arg.add_premiss_couple_values(criterion_name_1, value)
                arg_list.append(arg)
                for criterion_name_2 in remaining_criterion_names:
                    if self.preferences.is_preferred_criterion(criterion_name_1, criterion_name_2):
                        arg = Argument(True, item)
                        arg.add_premiss_couple_values(criterion_name_1, value)
                        arg.add_premiss_comparison(criterion_name_1, criterion_name_2)
                        arg_list.append(arg)


            elif value == Value.GOOD:
                arg = Argument(True, item)
                arg.add_premiss_couple_values(criterion_name_1, value)
                arg_list.append(arg)

                for criterion_name_2 in remaining_criterion_names:
                    if self.preferences.is_preferred_criterion(criterion_name_1, criterion_name_2):
                        arg = Argument(True, item)
                        arg.add_premiss_couple_values(criterion_name_1, value)
                        arg.add_premiss_comparison(criterion_name_1, criterion_name_2)
                        arg_list.append(arg)

        return arg_list
        

    def List_attacking_proposal(self, item):
        """Generate a list of arguments which can be used to attack an item
        :param item: Item - name of the item
        :return: list of all arguments CON an item (sorted by order of importance based on preferences)
        """
        arg_list = []
        for criterion_name_1 in self.preferences.get_criterion_name_list():
            remaining_criterion_names = self.preferences.get_criterion_name_list().copy()
            remaining_criterion_names.remove(criterion_name_1)
            value = self.preferences.get_value(item, criterion_name_1)

            if value == Value.VERY_BAD:
                arg = Argument(False, item)
                arg.add_premiss_couple_values(criterion_name_1, value)
                arg_list.append(arg)

                for criterion_name_2 in remaining_criterion_names:
                    if self.preferences.is_preferred_criterion(criterion_name_1, criterion_name_2):
                        arg = Argument(False, item)
                        arg.add_premiss_couple_values(criterion_name_1, value)
                        arg.add_premiss_comparison(criterion_name_1, criterion_name_2)
                        arg_list.append(arg)


            elif value == Value.BAD:
                arg = Argument(False, item)
                arg.add_premiss_couple_values(criterion_name_1, value)
                arg_list.append(arg)

                for criterion_name_2 in remaining_criterion_names:
                    if self.preferences.is_preferred_criterion(criterion_name_1, criterion_name_2):
                        arg = Argument(False, item)
                        arg.add_premiss_couple_values(criterion_name_1, value)
                        arg.add_premiss_comparison(criterion_name_1, criterion_name_2)
                        arg_list.append(arg)

        return arg_list

class ArgumentModel(Model):
    """ ArgumentModel which inherit from Model.
    """
    def __init__(self):
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)


        diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
        electric_engine = Item("Electric Engine", "A very quiet engine")
        hydrogene_engine = Item("Hydrogene Engine", "A furutistic engine")
        nuclear_engine = Item("Nuclear Engine", "A very powerful yet dangerous engine")

        list_items = [diesel_engine, electric_engine, hydrogene_engine, nuclear_engine]

        Agent1 = ArgumentAgent(1, self, "Bob", list_items)
        Agent1.generate_preferences(list_items)
        Agent1.generate_arguments()
        self.schedule.add(Agent1)
        Agent2 = ArgumentAgent(2, self, "Alice", list_items)
        Agent2.generate_preferences(list_items)
        Agent2.generate_arguments()
        self.schedule.add(Agent2)

        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        step_answer = self.schedule.step()
        #print(step_answer)
    
    def run_model(self, step_count=200):
        for i in range(step_count):
            self.step()

    def get_message_history(self):
        history = self.__messages_service.get_message_history()
        return pd.DataFrame(history)
if __name__ == "__main__":
    argument_model = ArgumentModel()
    argument_model.run_model()
    history = argument_model.get_message_history()
    print(history)


