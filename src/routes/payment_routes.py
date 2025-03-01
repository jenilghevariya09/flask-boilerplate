from flask import Blueprint, request, jsonify
from utils.payment_service import check_payment
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_model import User
from models.payment_history_model import mysql,PaymentHistory
from models.coupon_model import Coupon
import razorpay
import hmac
import hashlib
import datetime
from decimal import Decimal

payment_routes = Blueprint('payment_routes', __name__)

client = razorpay.Client(auth=("rzp_test_CQEcgPQabeIzXW", "BVUCLkharw8hJjcLp3UrSY3F"))

def convert_decimal_to_float(data):
    for key, value in data.items():
        if isinstance(value, Decimal):
            data[key] = float(value)
    return data


@payment_routes.route('/checkout-details', methods=['POST'])
@jwt_required()
def checkout():
    try:
        cursor = mysql.connection.cursor()
        email = get_jwt_identity()
        user_data = User.get_user_by_email(cursor, email)
        data = request.get_json()
        paymentDetails = check_payment(cursor, data, user_data)
        mysql.connection.commit()
        cursor.close()
        if paymentDetails and paymentDetails['isError'] == False:
            return jsonify(paymentDetails), 200
        else:
            return jsonify(paymentDetails), 400
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the checkout data", "error": str(e)}), 500

@payment_routes.route('/checkout', methods=['POST'])
@jwt_required()
def payment_checkout():
    try:
        cursor = mysql.connection.cursor()
        email = get_jwt_identity()
        user_data = User.get_user_by_email(cursor, email)
        data = request.get_json()

        paymentDetails = check_payment(cursor, data, user_data)
        checkoutData = paymentDetails.get('data')

        if paymentDetails.get('isError') or not checkoutData:
            return jsonify(paymentDetails), 400
        
        checkoutData = convert_decimal_to_float(checkoutData)
        
        notes = {
                "userId": user_data.get('id'),
                "activationDate": checkoutData.get('activationDate').astimezone(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                "expiryDate": checkoutData.get('expiryDate').astimezone(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                "planId": checkoutData.get('planId'),
                "subTotalAmount": checkoutData.get('subTotalAmount'),
                "taxAmount": checkoutData.get('taxAmount'),
                "totalAmount": checkoutData.get('totalAmount'),
                "subscriptionPeriod": checkoutData.get('subscriptionPeriod'),
            }

        if checkoutData.get('couponCode'):
            notes.update({
                "couponCode": checkoutData.get('couponCode'),
                "discountAmount": checkoutData.get('discountAmount'),
                "afterDiscountAmount": checkoutData.get('afterDiscountAmount'),
            })

        paymentData = {
                "amount": int(abs(checkoutData.get('totalAmount', 0)) * 100),
                "currency": "INR",
                "payment_capture": 1,
                "notes": notes,
            }
        
        isRedirect = False
        payment = None
        if paymentData['amount'] == 0:
            
            if checkoutData.get('couponCode'):
                notes['offerType'] = checkoutData.get('offerType')
                notes['couponValue'] = checkoutData.get('couponValue')
                
            notes['paymentStatus'] = 'captured'
            payment = PaymentHistory.create_payment_history(cursor, notes)
            
            if user_data.get('status') == 'active' and user_data.get('activateDate'):
                activateDate = user_data.get('activateDate')
            else:
                activateDate = checkoutData.get('activationDate')

            updated_user = {
                "activateDate": activateDate,
                "expiryDate": checkoutData.get('expiryDate'),
                "planId": checkoutData.get('planId'),
                "status": "active",
            }
            
            User.update_profile(cursor, user_data.get('id'), updated_user)
        else:
            paymentData["notes"]["name"] = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}"
            paymentData["notes"]["contact"] = f"+91{user_data.get('phone_number', '')}"
            paymentData["notes"]["email"] = user_data.get('email', '')
            payment = client.order.create(data=paymentData)
            isRedirect = True
            
        mysql.connection.commit()
        cursor.close()
        return jsonify({"payment": payment, "isRedirect": isRedirect}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the payment checkout", "error": str(e)}), 500


@payment_routes.route('/razorpay-webhook', methods=['POST'])
def webhook():
    webhook_secret = "0Sl7EYMtUt056Vr68hQuiZO/etjekbItCCaaqPE2"
    request_data = request.get_data(as_text=True)
    signature = request.headers.get('X-Razorpay-Signature')

    # Verify the webhook signature
    generated_signature = hmac.new(webhook_secret.encode(), request_data.encode(), hashlib.sha256).hexdigest()
    if hmac.compare_digest(generated_signature, signature):
        cursor = mysql.connection.cursor()
        event = request.get_json()
        event_type = event['event']
        payment = event['payload']['payment']['entity']
        payment_note = payment.get('notes', {})


        if event_type == 'payment.captured':
            notes = {
                    "paymentStatus": 'captured',
                    "userId": payment_note.get('userId'),
                    "activationDate": payment_note.get('activationDate'),
                    "expiryDate": payment_note.get('expiryDate'),
                    "planId": payment_note.get('planId'),
                    "subTotalAmount": payment_note.get('subTotalAmount'),
                    "taxAmount": payment_note.get('taxAmount'),
                    "totalAmount": payment_note.get('totalAmount'),
                    "subscriptionPeriod": payment_note.get('subscriptionPeriod'),
                    "paymentMethod" : payment.get('method'),
                    "order_id" : payment.get('order_id'),
                    "paymentId" : payment.get('id'),
                }
            if payment_note.get('couponCode'):
                coupon = Coupon.get_coupon_by_code(cursor, payment_note.get('couponCode'))
                notes.update({
                    "couponCode": payment_note.get('couponCode'),
                    "discountAmount": payment_note.get('discountAmount'),
                    "afterDiscountAmount": payment_note.get('afterDiscountAmount'),
                    "offerType": coupon.get('offerType'),
                    "couponValue": coupon.get('couponValue'),
                })
                
            PaymentHistory.create_payment_history(cursor, notes)
            user_data = User.get_user_by_id(cursor, payment_note.get('userId'))
            if user_data.get('status') == 'active':
                activateDate = user_data.get('activateDate')
            else:
                activateDate = payment_note.get('activationDate')
            
            updated_user = {
                "activateDate": activateDate,
                "expiryDate": payment_note.get('expiryDate'),
                "planId": payment_note.get('planId'),
                "status": "active",
            }
            User.update_profile(cursor, payment_note.get('userId'), updated_user)
        
        mysql.connection.commit()
        cursor.close()    
        return jsonify({"message": "Webhook processed"}), 200
    else:
        return jsonify({"message": "Invalid signature"}), 400

@payment_routes.route('/verify/<paymentId>', methods=['GET'])
@jwt_required()
def verify(paymentId):
    try:
        cursor = mysql.connection.cursor()
        response = PaymentHistory.get_payment_history_by_paymentId(cursor, paymentId)
        cursor.close()
        if response:
            return jsonify(response), 200
        else:
            return jsonify({"message": "Payment not found"}), 404
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500