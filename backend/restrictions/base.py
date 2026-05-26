from abc import ABC, abstractmethod


from typing import Any


class Restriction(ABC):
    """Abstract base class for timetable restrictions.

    Concrete restrictions should implement apply(model, assignments, *args, **kwargs)
    which adds constraints to the provided CP-SAT model.
    """

    @abstractmethod
    def apply(self, model, assignments, *args, **kwargs):
        raise NotImplementedError()

    def apply_with_assumptions(self, model, assignments, *args, **kwargs) -> list[tuple[Any, dict]]:
        """Apply constraints and return assumption vars for entity-level diagnosis.

        Returns a list of (BoolVar, entity_info_dict) tuples.
        Entity info dict should contain at minimum:
          - "restriction": class name
          - "entity_type": e.g. "teacher"
          - "entity_id": unique identifier
          - "entity_name": display name

        Default implementation calls apply() and returns [].
        Override to support entity-level diagnosis via
        SufficientAssumptionsForInfeasibility().
        """
        self.apply(model, assignments, *args, **kwargs)
        return []

    @property
    def name(self):
        return self.__class__.__name__
