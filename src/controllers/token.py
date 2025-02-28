from flask import jsonify, request
from models.broker_credentials_model import BrokerCredentials
from models.token import Token
from utils.commonUtils import format_query_result, format_single_query_result
from utils.get_broker import get_token

def refresh_broker_token(cursor, user):
    try:
        result = BrokerCredentials.get_broker_credentials_by_user(cursor, user.get('id'))
        if result and result[0]:
            data = result[0]
            brokerType = data.get('brokerServer')
            if brokerType == 'Upstox':
                return jsonify({"brokercredentials": data, "brokerType": brokerType}), 200
            def check_error(response):
                    if response.get('isError'):
                        return jsonify(response), 400
                    return None

            token_response = get_token(cursor, data, user.get('id'))
            if (error := check_error(token_response)):
                return error
                    
            client_code = token_response.get('user_session').get('result', {}).get('clientCodes')
            if client_code and client_code[0]:
                data['client_code'] = client_code[0]
                broker_updated_data = {
                    "client_code": client_code[0],
                    "userId": user.get('id')
                }
                BrokerCredentials.create_broker_credentials(cursor, broker_updated_data)
                data['client_code'] = client_code[0]

            token = Token.get_token_by_user(cursor, user.get('id'))
                
            return jsonify({"message": "Broker token refreshed successfully", "brokercredentials": data,  "token": token}), 200
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
            result = BrokerCredentials.get_broker_credentials_by_user(cursor, data.get('userId'))
            if result and result[0]:
                formatted_broker = result[0]
            
            token = Token.get_token_by_user(cursor, data.get('userId'))
            
            return jsonify({"message": "Broker token created successfully", "brokercredentials": formatted_broker,  "token": token}), 200
        else:
            return jsonify({"message": "Please provide broker credentials"}), 404
    except Exception as e:
        return jsonify({"message": "Error creating token", "error": str(e)}), 500