"""Test the API gateway for event validation."""

import requests

# The URL will look something like this:
api_url = "https://<api-id>.execute-api.<region>.amazonaws.com/prod/"

# The payload should match your state machine's expected input
payload = {"data": {"key": "value"}}

# Send the POST request
response = requests.post(api_url, json=payload)
print(response.json())  # Will return the execution ARN
