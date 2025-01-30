from flask import jsonify, request
from models.broker_credentials_model import BrokerCredentials
from utils.commonUtils import format_query_result, format_single_query_result
from utils.callApi import call_host_lookup_api, call_user_session_api, call_user_market_api


def refresh_broker_token(cursor, user_data):
    try:
        result = BrokerCredentials.get_broker_credentials_by_user(cursor, user_data.id)
        if result:
            column_names = ["id", "brokerServer", "MarketApiKey", "MarketSecretKey","InteractiveApiKey", "InteractiveSecretKey", "MarketUrl", "InteractiveUrl", "userId", "interactiveUserId", "marketUserId"]
            formatted_result = format_query_result(result, column_names)
            if formatted_result and formatted_result[0]:
                data = formatted_result[0]
                # user_market_response = call_user_market_api(cursor, data, user_data.id)
                # if user_market_response.get('type') == 'error' or user_market_response.get('isError'):
                #     message = (user_market_response.get('result', {}).get('message') or 
                #           user_market_response.get('description') or 
                #           user_market_response.get('error') or 
                #           "An error occurred")
                #     return jsonify({"message": message, "error": user_market_response}), 400

                host_lookup_response = call_host_lookup_api(data)

                user_session_response = call_user_session_api(cursor, data, host_lookup_response, user_data.id)
                if user_session_response.get('type') == 'error' or user_session_response.get('isError'):
                    message = (user_session_response.get('result', {}).get('message') or 
                          user_session_response.get('description') or 
                          user_session_response.get('error') or 
                          "An error occurred")
                    return jsonify({"message": message, "error": user_session_response}), 400
                
                return jsonify({"message": "Broker token refreshed successfully", "host_lookup": host_lookup_response, "Interactive_session" : user_session_response}), 200
            else:
                return jsonify({"message": "Broker credentials not found"}), 404
        else:
            return jsonify({"message": "Broker credentials not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error creating token", "error": str(e)}), 500