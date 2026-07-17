"""
integrations.py — OpenAI and Plaid service wrappers

This file will isolate all external API communication.

OpenAI responsibilities:
- generate a weekly spending goal
- generate a monthly savings goal
- generate a supportive daily finance tip
- request structured output
- validate the response
- return safe fallback goals when mock mode is enabled or the request fails

Plaid responsibilities:
- create a sandbox Link token
- exchange a public token
- retrieve recent transactions
- convert Plaid data into the application's transaction format
- avoid exposing or logging access tokens

The demo should support environment flags such as:
- USE_MOCK_OPENAI
- USE_MOCK_PLAID


"""
