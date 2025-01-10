import json
import datetime
import decimal
from flask import Flask, jsonify, request, make_response, Response

class HTTP:
  
    status = {
        '200': 'Ok',
        '201': 'Created',
        '400': 'Bad Request',
        '401': 'Unauthorized',
        '403': 'Forbidden',
        '404': 'Not Found',
        '405': 'Method Not Allowed',
        '406': 'Not Acceptable',
        '409': 'Conflict',
        '500': 'Internal Server Error',
    }
  
    # Request
    request = request

    # Response
    def response(self, data = None, code = 200, message = None, error = None):
        """Generates a standardized response for success or error."""
        message_to_use = message if message else self.status.get(str(code), 'Default message')
        headers = []

        # If there is an error, structure the response accordingly
        if error:
            para = {
                'status': code,
                'result': {},
                'error': str(error),
                'message': message_to_use,
            }
        elif data:
            # If there is data, structure the response as a success
            para = {
                'status': code,
                'result': data,
                'message': message_to_use,
            }

            if 'headers' in data:
                headers = data['headers']

        else:
            # If no data and no error, just send the status
            para = {
                'status': code,
                'message': message_to_use,
            }

        def default(o):
            """Helper method to serialize non-serializable objects like datetime."""
            if isinstance(o, datetime.datetime):
                return o.__str__()

        return Response(
            json.dumps(para, default=default, sort_keys=True, indent=4, cls=DecimalEncoder),
            status=para['status'],
            headers=headers,
            mimetype='application/json'
        )


# Decimal Encoder for JSON Serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        """Convert Decimal objects to float or int."""
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)