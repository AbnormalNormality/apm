from typing import Any, Callable, TypeVar, ParamSpec
from os import system
from sys import platform
from copy import deepcopy


P = ParamSpec("P")
R = TypeVar("R")

FUNCTION = Callable[..., object]


class FunctionRegistry:
    def __init__(self, *valid_keys: str):
        self._events: dict[str, FUNCTION] = {}

        self._validKeys = valid_keys

    def __call__(self, arg: str | FUNCTION) -> FUNCTION | Callable[[FUNCTION], FUNCTION]:
        if isinstance(arg, str):
            def decorator(func: FUNCTION) -> FUNCTION:
                return self._register(arg, func)
            return decorator

        else:
            return self._register(arg.__name__, arg)

    def __getattr__(self, name: str) -> FUNCTION:
        if name in self.__dict__.keys() or name in self.__dir__():
            return self.__dict__[name]

        elif name in self._events:
            return self._events[name]

        else:
            return EmptyFunction()

    def _register(self, name: str, func: FUNCTION) -> FUNCTION:
        if name in self.__dict__.keys() or name in self.__dir__():
            raise ValueError(
                f"The name {name} is used by the class {type(self).__name__}")

        elif self._validKeys and name not in self._validKeys:
            raise ValueError(f"{name} is not a valid key")

        self._events[name] = func
        return func


def clear_console():
    if platform.startswith("linux") or platform == "darwin":
        system("clear")

    elif platform.startswith("win"):
        system("cls")


class DefaultClass:
    def __repr__(self) -> str:
        return f"{type(self).__name__}({", ".join([f"{k}: {repr(v)}" for k, v in self.__dict__.items() if not k.startswith("_")])})"

    def copy(self):
        return deepcopy(self)


class EmptyFunction:
    def __call__(self, *args: Any, **kwds: Any):
        return None

    def __bool__(self) -> bool:
        return False


__all__ = ["FunctionRegistry", "clear_console",
           "DefaultClass", "EmptyFunction"]


if __name__ == '__main__':
    clear_console()

    class Mailbox:
        def __init__(self):
            self.event = FunctionRegistry("on_mail", "on_spam")

    mailbox = Mailbox()

    @mailbox.event
    def on_mail(message: str):
        print(message)

    on_mail_event = mailbox.event.on_mail
    if on_mail_event:
        on_mail_event("Hello, World!")

    @mailbox.event("on_spam")
    def spam_handler():
        print("Spam")

    mailbox.event.on_spam()
