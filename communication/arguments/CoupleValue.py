#!/usr/bin/env python3


class CoupleValue:
    """CoupleValue class.
    This class implements a couple value used in argument object.

    attr:
        criterion_name:
        value:
    """

    def __init__(self, criterion_name, value):
        """Creates a new couple value."""
        self.__criterion_name = criterion_name
        self.__value = value

    def __str__(self):
        """Returns a string representation of the couple value."""
        return f"{self.__criterion_name.name}={self.__value.name}"

    def __eq__(self, o):
        """Return True if CoupleValues are equal."""
        if isinstance(o, CoupleValue):
            return (
                self.__criterion_name == o.__criterion_name
                and self.__value == o.__value
            )
        else:
            return False

    def get_criterion_name(self):
        return self.__criterion_name

    def get_value(self):
        return self.__value
