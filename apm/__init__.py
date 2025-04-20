from typing import Callable, TypeVar, ParamSpec


P = ParamSpec("P")
R = TypeVar("R")


class FunctionRegistry:
    def __init__(self):
        self.events: dict[str, Callable[..., object]] = {}

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        self.events[func.__name__] = func
        return func

    def __getattr__(self, name: str) -> Callable[..., object] | None:
        if name in self.events:
            return self.events[name]


__all__ = ["FunctionRegistry"]
