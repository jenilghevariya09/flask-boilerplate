import requests
from utils.callApi import call_host_lookup_api, call_user_session_api, call_user_market_api, call_multitrade_login

def check_error(response):
    if response.get('type') == 'error' or response.get('isError'):
        message = (response.get('result', {}).get('message') or 
                  response.get('description') or 
                  response.get('error') or 
                  "An error occurred")
        return {"isError": True, 'error': response, 'message': message}
    return None

def check_error_multitrade(response):
    if response.get('status') == 'unsuccessful' or response.get('isError'):
        message = (response.get('data', {}).get('error') or 
                  response.get('data', {}).get('error_text') or 
                  response.get('error') or 
                  "An error occurred")
        return {"isError": True, 'error': response, 'message': message}
    return None

def get_token(cursor, data, user_id):
    try:
        broker = data.get('brokerServer')
        
        handlers = BROKER_HANDLERS.get(broker, {})
        
        data.setdefault('MarketUrl', handlers['marketUrl'])
        data.setdefault('InteractiveUrl', handlers['interactiveUrl'])
        
        market_data = {}
        user_session = {}
        host_lookup_response = {}
        
        if data['MarketUrl'] and "market" in handlers:
            market_data = handlers["market"](cursor, data, user_id)
            if (error := handlers["check_error"](market_data)):
                return error

        if data['InteractiveUrl'] and "interactive" in handlers:
            if handlers.get("is_host_lookup"):
                host_lookup_response = call_host_lookup_api(data)
            
            if handlers.get("is_host_lookup"):
                user_session = handlers['interactive'](cursor, data, host_lookup_response, user_id)
            else:
                user_session = handlers['interactive'](cursor, data, user_id)
                
            if (error := handlers["check_error"](user_session)):
                return error
        
        return {"market_data": market_data, "user_session": user_session}
    except requests.exceptions.RequestException as e:
        return {"isError": True, 'error': str(e), 'message': "An error occurred"}

BROKER_HANDLERS = {
    "XTS-Symphony": {
        'marketUrl': 'https://developers.symphonyfintech.in/apimarketdata',
        'interactiveUrl': 'https://developers.symphonyfintech.in/interactive',
        "market": call_user_market_api,
        "interactive": call_user_session_api,
        "is_host_lookup": True,
        "check_error": check_error
    },
    "XTS-Jainam": {
        'marketUrl': 'http://ctrade.jainam.in:3001/apimarketdata',
        'interactiveUrl': 'http://ctrade.jainam.in:4001/hostlookup',
        "market": call_user_market_api,
        "interactive": call_user_session_api,
        "is_host_lookup": True,
        "check_error": check_error
    },
    "XTS-JMFinance": {
        'marketUrl': 'https://smartapi.jmfonline.in/apimarketdata',
        'interactiveUrl': 'https://smartapi.jmfonline.in/interactive',
        "market": call_user_market_api,
        "interactive": call_user_session_api,
        "is_host_lookup": True,
        "check_error": check_error
    },
    "XTS-Multitrade": {
        'marketUrl': 'https://wss1.mtsp.co.in:15207',
        'interactiveUrl': 'https://wss1.mtsp.co.in:15207',
        "interactive": call_multitrade_login,
        "is_host_lookup": False,
        "check_error": check_error_multitrade
    },
    "XTS-Other": {
        'marketUrl': '',
        'interactiveUrl': '',
        "market": call_user_market_api,
        "interactive": call_user_session_api,
        "is_host_lookup": True,
        "check_error": check_error
    },
}