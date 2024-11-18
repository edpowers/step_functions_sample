"""Utils for Task Definitions."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aws_lambda_powertools import Logger

logger = Logger(child=True)


@dataclass
class WorkflowModel:
    """Workflow model for storing workflows."""

    templates: dict[str, Any]
    workflows: dict[str, Any]
    errors: dict[str, Any]


class UtilsDefinitions:
    """Util functions for task definitions."""

    @staticmethod
    def substitute_params(
        template: dict[str, Any], params: dict[str, str]
    ) -> dict[str, Any]:
        """Replace parameters in template with actual values."""
        template_str = json.dumps(template)
        for key, value in params.items():
            # Raise ValueError if not a string. This is meant for single value
            # replacement, and trying to substitute a dict into the json doesn't make sense
            # if we're going to load the json thereafter anyway.
            if not isinstance(value, str):
                raise ValueError(f"{type(value)=} is not a string.")

            template_str = template_str.replace(f"${{{key}}}", value)

        return json.loads(template_str)

    @staticmethod
    def load_json_from_dir(directory: Path) -> dict[str, Any]:
        """Load json from directory."""
        return {
            f.stem: UtilsDefinitions.load_definition(str(f))
            for f in directory.glob("*.json")
        }

    @staticmethod
    def load_definition(file_path: str) -> dict[str, Any]:
        """Load a single ASL definition file."""
        with open(file_path) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as je:
                logger.error(f"{je=} - Assuming file is empty.")
                return {}

    @staticmethod
    def load_all_workflows() -> WorkflowModel:
        """Load all workflow definitions."""
        base_path = Path(__file__).parent.parent / "definitions"

        return WorkflowModel(
            templates=UtilsDefinitions.load_json_from_dir(base_path / "templates"),
            workflows=UtilsDefinitions.load_json_from_dir(base_path / "workflows"),
            errors=UtilsDefinitions.load_json_from_dir(base_path / "errors"),
        )
