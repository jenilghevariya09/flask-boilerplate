import requests
from models.token import Token

def call_host_lookup_api():
    try:
        url = 'http://ctrade.jainam.in:4001/hostlookup'
        headers = {
            'Content-Type': 'application/json',
        }
        body = {
            'AccessPassword': '2021HostLookUpAccess',
            'version': 'interactive_1.0.1',
        }
        response = requests.post(url, headers=headers, json=body)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"isError": True,'error': str(e)}

def call_user_session_api(cursor, data, host_lookup_response, userId):
    try:
        uniqueKey = host_lookup_response.get('result', {}).get('uniqueKey')
        connectionString = host_lookup_response.get('result', {}).get('connectionString')
        if not uniqueKey or not connectionString:
            return {"isError": True, 'error': 'Invalid response from Host Lookup API.'}

        url = connectionString + '/user/session'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'appKey': data['InteractiveApiKey'],
            'secretKey': data['InteractiveSecretKey'],
            'source': 'WebAPI',
            'uniqueKey': uniqueKey,
        }
        
        response = requests.post(url, headers=headers, json=payload)
        resultData = response.json()
        if resultData.get('type') == 'success':
            token = resultData.get('result').get('token')
            if token:
                Token.upsert_token(cursor, userId, token, None, connectionString)
        return resultData
    except requests.exceptions.RequestException as e:
        print(str(e))
        return {"isError": True, 'error': str(e)}
    
def call_user_market_api(cursor, data, userId):
    try:
        url = 'http://ctrade.jainam.in:3001/apimarketdata/auth/login'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'appKey': data['MarketApiKey'],
            'secretKey': data['MarketSecretKey'],
            'source': 'WebAPI',
        }

        response = requests.post(url, headers=headers, json=payload)
        resultData = response.json()
        if resultData.get('type') == 'success':
            token = resultData.get('result').get('token')
            if token:
                Token.upsert_token(cursor, userId, None, token, None)
        return resultData
    except requests.exceptions.RequestException as e:
        return {"isError": True, 'error': str(e)}