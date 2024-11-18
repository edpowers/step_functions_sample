"""Lambda event model."""

from enum import Enum

from pydantic import BaseModel, computed_field


class EnumResult(Enum):
    """Enum result model."""

    SUCCESS = True
    FAILURE = False


class ValidationModel(BaseModel):
    """Lambda1 Event Model."""

    input_received: dict

    # TODO - fill in details.
    success: bool = True

    @computed_field
    @property
    def status(self) -> EnumResult:
        """Simple result logic that can check a condition and return true/false."""
        if self.success:
            return EnumResult.SUCCESS
        else:
            return EnumResult.FAILURE

    def return_result(
        self,
    ) -> dict[
        str,
        EnumResult | bool | dict,
    ]:
        """Return the result based on the processing."""
        return {
            "status": self.status,
            "processed": True,
            "input_received": self.input_received,
        }
