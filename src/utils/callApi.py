import requests
from models.token import Token

def call_host_lookup_api(data):
    try:
        url = data['InteractiveUrl']
        headers = {
            'Content-Type': 'application/json',
        }
        body = {
            'AccessPassword': '2021HostLookUpAccess',
            'version': 'interactive_1.0.1',
        }
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 404:
            return {"uniqueKey": '', "connectionString": data['InteractiveUrl'], "MarketUrl" : data['MarketUrl']}
        response_json = response.json()
        uniqueKey = response_json.get('result', {}).get('uniqueKey') or ''
        connectionString = response_json.get('result', {}).get('connectionString') or data['InteractiveUrl']
        
        return {"uniqueKey": uniqueKey, "connectionString": connectionString, "MarketUrl" : data['MarketUrl']}
    except requests.exceptions.RequestException as e:
        return {"uniqueKey": '', "connectionString": data['InteractiveUrl'], "MarketUrl" : data['MarketUrl']}

def call_user_session_api(cursor, data, host_lookup_response, userId):
    try:
        uniqueKey = host_lookup_response['uniqueKey']
        connectionString = host_lookup_response['connectionString'] 
        if not connectionString:
            return {"isError": True, 'error': 'Invalid response from Host Lookup API.'}

        url = connectionString + '/user/session'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'appKey': data['InteractiveApiKey'],
            'secretKey': data['InteractiveSecretKey'],
            'source': 'WebAPI',
        }
        
        if uniqueKey:
            payload['uniqueKey'] = uniqueKey
            
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 404:
            return {"isError": True, 'error': "Interactive Data Resource not found (404)"}
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
        url = data['MarketUrl'] + '/auth/login'
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'appKey': data['MarketApiKey'],
            'secretKey': data['MarketSecretKey'],
            'source': 'WebAPI',
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 404:
            return {"isError": True, 'error': "Market Data Resource not found (404)"}
        
        if response.content:
            resultData = response.json()
            if resultData.get('type') == 'success':
                if resultData.get('result', {}).get('userID') != data['marketUserId']:
                    return {"isError": True, 'error': "User Id does not match"}
                token = resultData.get('result').get('token')
                if token:
                    Token.upsert_token(cursor, userId, None, token, None)
            return resultData
        else:
            return {"isError": True, 'error': "Empty response from server"}
    except requests.exceptions.RequestException as e:
        return {"isError": True, 'error': str(e)}
    
def call_multitrade_login(cursor, data, userId):
    try:
        connectionString = data['InteractiveUrl'] 
        if not connectionString:
            return {"isError": True, 'error': 'Invalid response from Host Lookup API.'}

        url = connectionString + '/connect/login'
        headers = {
          "Content-Type": "application/x-www-form-urlencoded",
          "Api-Version": "3"
        }
        
        payload = {
          "api_key": data['InteractiveApiKey'],
          "api_secrets": data['InteractiveSecretKey']
        }
            
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 404:
            return {"isError": True, 'error': "Interactive Data Resource not found (404)"}
        resultData = response.json()
        if resultData.get('status') == 'successful':
            token = resultData.get('data').get('request_token')
            if token:
                secretToken = data['InteractiveApiKey'] + ':' + token
                Token.upsert_token(cursor, userId, secretToken, None, connectionString)
        return resultData
    except requests.exceptions.RequestException as e:
        print(str(e))
        return {"isError": True, 'error': str(e)}