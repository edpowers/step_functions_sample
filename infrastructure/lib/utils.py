"""Utils for creating cdk stack."""

from dataclasses import dataclass
from typing import Any

from aws_cdk import (
    Duration,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_stepfunctions as sfn,
)
from constructs import Construct


@dataclass
class RestApiConfigs:
    """Configuration model for RestAPI."""

    rest_api_name: str
    description: str
    id_str: str  # ID for creating the construct.


@dataclass
class StateMachineConfigs:
    """Configuration for AWS State Machine (Step Function)."""

    id_str: str
    definition_body: Any  # Replace with task definition properties.
    timeout_duration: Duration


@dataclass
class LambdaFunctionConfigs:
    """Lambda function configs for creating lamdba function."""

    id_str: str
    runtime: _lambda.Runtime
    function_name: str
    handler: str
    code: str
    timeout: Duration
    memory_size: int


class Utils:
    """Staticmethods for defining cdk infrastructure."""

    @staticmethod
    def create_lambda_function(
        scope: Construct, lambda_function_configs: LambdaFunctionConfigs
    ) -> _lambda.Function:
        """Create a lambda function given configs."""
        return _lambda.Function(
            scope=scope,
            id=lambda_function_configs.id_str,
            function_name=lambda_function_configs.function_name,
            handler=lambda_function_configs.handler,
            runtime=lambda_function_configs.runtime,
            code=lambda_function_configs.code,
            timeout=lambda_function_configs.timeout,
            memory_size=lambda_function_configs.memory_size,
        )

    @staticmethod
    def create_rest_api(
        scope: Construct, rest_api_configs: RestApiConfigs
    ) -> apigw.RestApi:
        """Create a rest api based on the configuration properties."""
        return apigw.RestApi(
            scope=scope,
            id=rest_api_configs.id_str,
            rest_api_name=rest_api_configs.rest_api_name,
            description=rest_api_configs.description,
        )

    @staticmethod
    def create_state_machine(
        scope: Construct, state_machine_configs: StateMachineConfigs
    ) -> sfn.StateMachine:
        return sfn.StateMachine(
            scope=scope,
            id=state_machine_configs.id_str,
            definition_body=state_machine_configs.definition_body,
            timeout=state_machine_configs.timeout_duration,
        )
