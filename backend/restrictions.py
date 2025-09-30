from abc import ABC, abstractmethod


class Restriction(ABC):
    """Abstract base class for timetable restrictions.

    Concrete restrictions should implement apply(model, assignments, *args, **kwargs)
    which adds constraints to the provided CP-SAT model.
    """

    @abstractmethod
    def apply(self, model, assignments, *args, **kwargs):
        raise NotImplementedError()
