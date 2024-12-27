import requests

BASE_URL = 'https://api.nusasms.com/nusasms_api/1.0'
# For testing
# BASE_URL = 'https://dev.nusasms.com/nusasms_api/1.0'

HEADERS = {
    "Accept": "application/json",
    "APIKey": "437167929AF629E3F0B2F5B30AA48C18"
}
PAYLOADS = {
    'destination': '6281282209956',
    # Optional
    'message': "hai.\\nGrinning face emoticon: \\\\U0001F600",
    'include_unsubscribe': True
}

r = requests.post(
    f'{BASE_URL}/whatsapp/message',
    headers=HEADERS,
    json=PAYLOADS,
    # Skip SSL Verification
    # verify=False
)

print(r.json())