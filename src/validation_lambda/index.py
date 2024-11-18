"""Sample lambda code for step function execution."""

from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.common.model.validation_model import ValidationModel

logger = Logger(child=True)


def processing_function(event: dict[str, Any]) -> dict[str, Any]:
    """Run processing logic on the input event.

    Args:
        event: Input event dictionary from Step Functions

    Returns:
        Dict containing processed results
    """
    logger.info("Processing event", extra={"event": event})

    try:
        # Add your processing logic here
        validated_event = ValidationModel.model_validate(event)

        # This is a sample implementation
        result = validated_event.return_result()

        logger.info("Successfully processed event", extra={"result": result})
        return result

    except Exception:
        logger.exception("Error processing event")
        raise


@logger.inject_lambda_context
def handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """AWS Lambda handler for Step Function execution.

    Args:
        event: Input event from Step Functions
        context: Lambda context object

    Returns:
        Dict containing processing results
    """
    logger.info(
        "Lambda invocation started",
        extra={"request_id": context.aws_request_id, "event": event},
    )

    try:
        # Process the event
        result = processing_function(event)

        # Return the processed result
        return {"statusCode": 200, "body": result, "requestId": context.aws_request_id}

    except Exception as e:
        logger.exception("Lambda execution failed")
        return {
            "statusCode": 500,
            "body": {"error": str(e), "status": "FAILED"},
            "requestId": context.aws_request_id,
        }
