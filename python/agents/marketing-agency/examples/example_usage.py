# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Example usage of the Marketing Agency ADK agent.

This script demonstrates how to interact with the marketing_agency agent
via the ADK API server endpoint.

Prerequisites:
    1. Set up environment variables (copy .env.example to .env and fill in):
       - GOOGLE_CLOUD_PROJECT
       - GOOGLE_CLOUD_LOCATION
       - GOOGLE_GENAI_USE_VERTEXAI

    2. Start the ADK API server from the marketing-agency directory:
       $ adk api_server marketing_agency

    3. Run this script:
       $ python examples/example_usage.py

    Optionally, set the ADK_API_URL environment variable to override the
    default server address (default: http://127.0.0.1:8000).
"""

import json
import os
import sys

import requests

# Base URL can be overridden via ADK_API_URL environment variable
BASE_URL = os.environ.get("ADK_API_URL", "http://127.0.0.1:8000")

# Endpoint created by running `adk api_server marketing_agency`
RUN_ENDPOINT = f"{BASE_URL}/run_sse"
HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "text/event-stream",
}

# Create a session for the user
SESSION_ENDPOINT = (
    f"{BASE_URL}/apps/marketing_agency/users/user_001/sessions/session_001"
)
try:
    response = requests.post(SESSION_ENDPOINT, timeout=10)
    response.raise_for_status()
    print("Session created:", response.json())
except requests.exceptions.ConnectionError:
    print(
        f"Error: Could not connect to the ADK API server at {BASE_URL}.\n"
        "Please start the server with: adk api_server marketing_agency"
    )
    sys.exit(1)
except requests.exceptions.RequestException as e:
    print(f"Error creating session: {e}")
    sys.exit(1)

# Example product launch scenario: organic cake business
user_inputs = [
    "I want to launch an organic cake business. Help me establish an online presence.",
    "I like 'organicbakedelight.com'. Please create a website for it.",
    "Now create a marketing strategy for Organic Bake Delight targeting health-conscious customers.",
    "Design a logo and brand assets for Organic Bake Delight with warm, earthy tones.",
]

for user_input in user_inputs:
    data = {
        "session_id": "session_001",
        "app_name": "marketing_agency",
        "user_id": "user_001",
        "new_message": {
            "role": "user",
            "parts": [
                {
                    "text": user_input,
                }
            ],
        },
    }

    print(f'\n[user]: "{user_input}"')

    with requests.post(
        RUN_ENDPOINT,
        data=json.dumps(data),
        headers=HEADERS,
        stream=True,
        timeout=120,
    ) as r:
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"API request failed: {e}")
            continue
        for chunk in r.iter_lines():
            if not chunk:
                continue
            json_string = chunk.decode("utf-8").removeprefix("data: ").strip()
            event = json.loads(json_string)

            if "content" not in event:
                print(event)
                continue

            author = event["author"]
            parts = event["content"]["parts"]

            function_calls = [
                p["functionCall"] for p in parts if "functionCall" in p
            ]
            function_responses = [
                p["functionResponse"] for p in parts if "functionResponse" in p
            ]

            if parts and "text" in parts[0]:
                text_response = parts[0]["text"]
                print(f"\n[{author}]: {text_response}")

            if function_calls:
                for function_call in function_calls:
                    name = function_call["name"]
                    args = function_call["args"]
                    print(
                        f"\n[{author}] calling tool: {name!r}\n"
                        f"args: {json.dumps(args, indent=2)}\n"
                    )

            elif function_responses:
                for function_response in function_responses:
                    function_name = function_response["name"]
                    payload = json.dumps(
                        function_response["response"], indent=2
                    )
                    print(
                        f"\n[{author}] response from: {function_name!r}\n"
                        f"response: {payload}\n"
                    )

                    # Application-level routing based on sub-agent responses
                    match function_name:
                        case "domain_create_agent":
                            print(
                                "[app]: Render domain name suggestions to user"
                            )
                        case "website_create_agent":
                            print("[app]: Save generated HTML/CSS/JS files")
                        case "marketing_create_agent":
                            print("[app]: Display marketing strategy report")
                        case "logo_create_agent":
                            print(
                                "[app]: Render generated logo and brand assets"
                            )
