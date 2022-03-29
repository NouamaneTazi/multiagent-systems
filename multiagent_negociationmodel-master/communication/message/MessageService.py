#!/usr/bin/env python3
from communication.message.MessagePerformative import MessagePerformative

class MessageService:
    """MessageService class.
    Class implementing the message service used to dispatch messages between communicating agents.

    Not intended to be created more than once: it's a singleton.

    attr:
        scheduler: the scheduler of the sma (Scheduler)
        messages_to_proceed: the list of message to proceed mailbox of the agent (list)
    """

    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method.
        """
        return MessageService.__instance

    def __init__(self, scheduler, instant_delivery=True):
        """ Create a new MessageService object.
        """
        if MessageService.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            MessageService.__instance = self
            self.__scheduler = scheduler
            self.__instant_delivery = instant_delivery
            self.__messages_to_proceed = []
            self.__message_history = []

    def get_message_history(self):
        """ Returns the message history
        """
        return self.__message_history 


    def add_message_to_history(self, message):
        """ Adds a message to the message history after parsing it
        """
        sender = message.get_exp()
        receiver = message.get_dest()
        perform = message.get_performative()
        content = message.get_content()
        item = content[0]

        if perform == MessagePerformative.ARGUE:
            argument = content[1]
            couple_value = argument.get_couple_values_list()[0]
            main_criterion = couple_value.get_criterion_name()
            value = couple_value.get_value()
            comparisons = argument.get_comparision_list()
                       
            if comparisons:
                comparison = comparisons[0]
                secondary_criterion = comparison.get_worst_criterion_name()

            else:
                secondary_criterion=None
            history = {
                'sender':sender,
                'receiver':receiver,
                'type_message':perform,
                'item':item,
                'value':value,
                'main_criterion':main_criterion,
                'secondary_criterion':secondary_criterion
                }
        
        else:
            history = {
                'sender':sender,
                'receiver':receiver,
                'type_message':perform,
                'item':item,
                'value':None,
                'main_criterion':None,
                'secondary_criterion':None
                }

        self.__message_history.append(history)

    def set_instant_delivery(self, instant_delivery):
        """ Set the instant delivery parameter.
        """
        self.__instant_delivery = instant_delivery

    def send_message(self, message):
        """ Dispatch message if instant delivery active, otherwise add the message to proceed list.
        """
        self.add_message_to_history(message)

        if self.__instant_delivery:
            self.dispatch_message(message)
        else:
            self.__messages_to_proceed.append(message)

    def dispatch_message(self, message):
        """ Dispatch the message to the right agent.
        """
        self.find_agent_from_name(message.get_dest()).receive_message(message)

    def dispatch_messages(self):
        """ Proceed each message received by the message service.
        """
        if len(self.__messages_to_proceed) > 0:
            for message in self.__messages_to_proceed:
                self.dispatch_message(message)

        self.__messages_to_proceed.clear()

    def find_agent_from_name(self, agent_name):
        """ Return the agent according to the agent name given.
        """
        for agent in self.__scheduler.agents:
            if agent.get_name() == agent_name:
                return agent
