import traceback
from typing import List, Any, Dict, Optional
from abc import ABC, abstractmethod

import os
from dotenv import load_dotenv
load_dotenv()

class StepExecutionError(Exception):
    """Custom exception for step execution failures with traceback."""

    def __init__(self, step_number: int, original_error: Exception, traceback_str: str):
        self.step_number = step_number
        self.original_error = original_error
        self.traceback_str = traceback_str
        super().__init__(
            f"Error at step {step_number}: {str(original_error)}\n\nTraceback:\n{traceback_str}"
        )

class Step(ABC):
    def __init__(self, input_keys: Optional[list[str]] = None, **kwargs):
        self.config: Dict[str, Any] = kwargs
        self.input_keys = input_keys or []

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate that all required keys are present in the input data"""
        if not isinstance(input_data, dict):
            raise TypeError(f"Input data must be a dictionary, got {type(input_data)}")

        missing_keys = [key for key in self.input_keys if key not in input_data]
        if missing_keys:
            raise KeyError(f"Missing required keys in input data: {missing_keys}")

    @abstractmethod
    def run(self, input_data: Dict[str, Any], **runtime_args) -> Dict[str, Any]:
        """Execute the step's logic on the input data."""
        pass
    
class Runner:
    def __init__(self):
        self._steps: List[Step] = []
        self._current_step: int = 0

    def add(self, step: Step) -> None:
        if not isinstance(step, Step):
            raise TypeError("Step must be an instance of Step class")
        self._steps.append(step)

    def run(self, initial_input: Any = None, **runtime_args) -> Any:
        if not self._steps:
            raise ValueError("No steps defined in the runner")

        current_input = initial_input
        self._current_step = 0

        try:
            for step in self._steps:
                self._current_step += 1
                current_input = step.run(current_input, **runtime_args)
                
        except Exception as e:
            raise StepExecutionError(
                step_number=self._current_step,
                original_error=e,
                traceback_str="".join(traceback.format_exc()),
            ) from e

        return current_input

    @property
    def step_count(self) -> int:
        """Return the total number of steps."""
        return len(self._steps)

    @property
    def current_step(self) -> int:
        """Return the current step number (1-based indexing)."""
        return self._current_step
