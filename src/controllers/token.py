from flask import jsonify, request
from models.broker_credentials_model import BrokerCredentials
from models.token import Token
from utils.commonUtils import format_query_result, format_single_query_result
from utils.get_broker import get_token

def refresh_broker_token(cursor, user_data):
    try:
        result = BrokerCredentials.get_broker_credentials_by_user(cursor, user_data.id)
        if result:
            formatted_token = None
            column_names = ["id", "brokerServer", "MarketApiKey", "MarketSecretKey","InteractiveApiKey", "InteractiveSecretKey", "MarketUrl", "InteractiveUrl", "userId", "interactiveUserId", "marketUserId", "client_code"]
            formatted_result = format_query_result(result, column_names)
            if formatted_result and formatted_result[0]:
                data = formatted_result[0]
                brokerType = data.get('brokerServer')
                if brokerType == 'Upstox':
                    return jsonify({"brokercredentials": data, "brokerType": brokerType}), 200
                def check_error(response):
                        if response.get('isError'):
                            return jsonify(response), 400
                        return None

                token_response = get_token(cursor, data, user_data.id)
                if (error := check_error(token_response)):
                    return error
                        
                client_code = token_response.get('user_session').get('result', {}).get('clientCodes')
                if client_code and client_code[0]:
                    data['client_code'] = client_code[0]
                    broker_updated_data = {
                        "client_code": client_code[0],
                        "userId": user_data.id
                    }
                    BrokerCredentials.create_broker_credentials(cursor, broker_updated_data)
                    data['client_code'] = client_code[0]

                token = Token.get_token_by_user(cursor, user_data.id)
                if token:
                    column_names = ["id", "interactive_token", "userId", "market_token", "interactive_url"]
                    formatted_token = format_single_query_result(token, column_names)
                    
                return jsonify({"message": "Broker token refreshed successfully", "brokercredentials": data,  "token": formatted_token}), 200
            else:
                return jsonify({"message": "Broker credentials not found"}), 404
        else:
            return jsonify({"message": "Broker credentials not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error creating token", "error": str(e)}), 500
    
def create_upstox_token(cursor, data):
    try:
        if data:
            data['brokerServer'] = 'Upstox'
            BrokerCredentials.create_broker_credentials(cursor, data)
            Token.upsert_token(cursor, data.get('userId'), data.get('access_token'), None, data.get('InteractiveUrl'))
            
            formatted_broker = None
            formatted_token = None
            result = BrokerCredentials.get_broker_credentials_by_user(cursor, data.get('userId'))
            if result:
                column_names = ["id", "brokerServer", "MarketApiKey", "MarketSecretKey","InteractiveApiKey", "InteractiveSecretKey", "MarketUrl", "InteractiveUrl", "userId", "interactiveUserId", "marketUserId", "client_code"]
                formatted_result = format_query_result(result, column_names)
                if formatted_result and formatted_result[0]:
                    formatted_broker = formatted_result[0]
            
            token = Token.get_token_by_user(cursor, data.get('userId'))
            if token:
                column_names = ["id", "interactive_token", "userId", "market_token", "interactive_url"]
                formatted_token = format_single_query_result(token, column_names)
            
            return jsonify({"message": "Broker token created successfully", "brokercredentials": formatted_broker,  "token": formatted_token}), 200
        else:
            return jsonify({"message": "Please provide broker credentials"}), 404
    except Exception as e:
        return jsonify({"message": "Error creating token", "error": str(e)}), 500