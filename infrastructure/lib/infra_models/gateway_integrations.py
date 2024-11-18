"""Dataclass for GatewayIntegrations."""

from dataclasses import dataclass

from aws_cdk.aws_apigateway import AwsIntegration


@dataclass
class GatewayIntegration:
    """Gateway Integration Model."""

    http_method: str
    target: AwsIntegration
    method_responses: list[dict[str, str]]
