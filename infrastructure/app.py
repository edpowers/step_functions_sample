"""Stack synthesis."""

import aws_cdk as cdk

from lib.step_functions_basics import StepFunctionsStack

app = cdk.App()

stagings = {"dev": ["us-east-1"]}

for env_name in stagings:
    for region in stagings[env_name]:
        StepFunctionsStack(
            app,
            region=region,
            construct_id=f"StepFunctionsBasicsStack-{env_name}-{region}",
        )

app.synth()
