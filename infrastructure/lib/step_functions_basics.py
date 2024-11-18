"""Step Functions Basics."""

import json

from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_apigateway as apigw,
    aws_iam,
    aws_lambda as _lambda,
    aws_stepfunctions as sfn,
)
from constructs import Construct

from definitions.utils_definitions import UtilsDefinitions
from lib.infra_models import GatewayIntegration
from lib.utils import (
    LambdaFunctionConfigs,
    RestApiConfigs,
    StateMachineConfigs,
    Utils,
)


class StepFunctionsStack(Stack):
    def __init__(self, scope: Construct, region: str, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        # Create Lambda function
        validation_lambda = Utils.create_lambda_function(
            scope=self,
            lambda_function_configs=LambdaFunctionConfigs(
                id_str=f"ValidationLambda-{region}",
                runtime=_lambda.Runtime.PYTHON_3_12,
                function_name="ValidationLambda",
                handler="index.handler",
                code=_lambda.Code.from_asset("../src/validation_lambda"),
                timeout=Duration.seconds(30),
                memory_size=1024,
            ),
        )

        error_handler_lambda = Utils.create_lambda_function(
            scope=self,
            lambda_function_configs=LambdaFunctionConfigs(
                id_str=f"ErrorHandlingLambda-{region}",
                runtime=_lambda.Runtime.PYTHON_3_12,
                function_name="ErrorHandlingLambda",
                handler="index.handler",
                code=_lambda.Code.from_asset("../src/error_lambda"),
                timeout=Duration.seconds(30),
                memory_size=1024,
            ),
        )

        # Apply erorr handlers to task.
        # sfn_tasks.LambdaInvoke(
        #     self,
        #     id="TaskWithErrorHandling",
        #     lambda_function=error_handler_lambda,
        #     invocation_type=sfn_tasks.LambdaInvocationType.REQUEST_RESPONSE,
        #     retry_on_service_exceptions=True,
        #     integration_pattern=sfn.IntegrationPattern.REQUEST_RESPONSE,
        # )

        # Output path of $.Payload means that after the lambda function executes, the state
        # machine will only keep the contents under the Payload field.
        # AWS Lambda automatically wraps the function's return value in a payload field.
        definitions = UtilsDefinitions.load_all_workflows()

        # Define substitution parameters
        workflow_params = {
            "ValidationLambdaArn": validation_lambda.function_arn,
            "ErrorHandlerArn": error_handler_lambda.function_arn,
            "EnrichmentSource": "",
            "EnrichmentVersion": "v1",
            # "StorageDestination": "my-storage-bucket",  - TODO - integrate with s3 storage.
            "WorkflowName": "DataProcessingWorkflow",
        }

        # Get the workflow definition and substitute parameters
        definitions.workflows["processing_workflow_test"] = (
            UtilsDefinitions.substitute_params(
                definitions.workflows["processing_workflow_test"], workflow_params
            )
        )

        # Create State Machine
        state_machine = Utils.create_state_machine(
            self,
            state_machine_configs=StateMachineConfigs(
                id_str="AwsStepFunction",
                timeout_duration=Duration.minutes(5),
                definition_body=sfn.DefinitionBody.from_string(
                    json.dumps(definitions.workflows["processing_workflow_test"])
                ),
            ),
        )

        # Create an IAM role for API Gateway
        api_role = aws_iam.Role(
            self,
            "ApiGatewayRole",
            assumed_by=aws_iam.ServicePrincipal("apigateway.amazonaws.com"),
        )

        # Grant StartExecution permissions
        state_machine.grant_start_execution(api_role)

        # Create API Gateway
        api = Utils.create_rest_api(
            scope=self,
            rest_api_configs=RestApiConfigs(
                rest_api_name="RestApi1",
                description="Rest API Gateway",
                id_str="RestApiGateway",
            ),
        )

        integrations: list[GatewayIntegration] = []

        # Create API Gateway integration
        integrations.append(
            GatewayIntegration(
                http_method="POST",
                target=apigw.AwsIntegration(
                    service="states",
                    action="StartExecution",
                    options=apigw.IntegrationOptions(
                        credentials_role=api_role,
                        integration_responses=[
                            {
                                "statusCode": "200",
                                "responseTemplates": {
                                    "application/json": "{'executionArn': $input.json('$.executionArn')}"
                                },
                            },
                            {
                                "statusCode": "400",
                                "selectionPattern": "4\\d{2}",
                                "responseTemplates": {
                                    "application/json": '{"error": "Bad request"}'
                                },
                            },
                            {
                                "statusCode": "500",
                                "selectionPattern": "5\\d{2}",
                                "responseTemplates": {
                                    "application/json": '{"error": "Internal server error"}'
                                },
                            },
                        ],
                        request_templates={
                            "application/json": (
                                "{"
                                f'"stateMachineArn": "{state_machine.state_machine_arn}",'
                                '"input": "$util.escapeJavaScript($input.body)"'
                                "}"
                            )
                        },
                        passthrough_behavior=apigw.PassthroughBehavior.NEVER,
                    ),
                ),
                method_responses=[
                    {"statusCode": "200"},
                    {"statusCode": "400"},
                    {"statusCode": "500"},
                ],
            )
        )

        for integration in integrations:
            # Add method to API Gateway
            api.root.add_method(
                integration.http_method,
                integration.target,
                method_responses=integration.method_responses,
            )

        CfnOutput(self, "ApiUrl", value=api.url, description="API Gateway URL")
