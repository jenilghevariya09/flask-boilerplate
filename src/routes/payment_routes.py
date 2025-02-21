from flask import Blueprint, request, jsonify
from controllers.token import refresh_broker_token, create_upstox_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.token import mysql
from models.user_model import mysql, User
import razorpay
import hmac
import hashlib
import datetime

payment_routes = Blueprint('payment_routes', __name__)

client = razorpay.Client(auth=("rzp_test_CQEcgPQabeIzXW", "BVUCLkharw8hJjcLp3UrSY3F"))


@payment_routes.route('/checkout', methods=['POST'])
@jwt_required()
def payment():
    cursor = mysql.connection.cursor()
    email = get_jwt_identity()
    user_data = User.get_user_by_email(cursor, email)
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid input"}), 400
    paymentData = {
        "amount": int(abs(data.get('amount')) * 100),
        "currency": "INR",
        "receipt": "test_receipt",
        "payment_capture": 1,
        "notes": {
            "name": user_data.get('first_name') + " " + user_data.get('last_name'),
            "contact": '+916355859435',
            "email": 'jenilghevariya000@gmail.com',
            "address": user_data.get('address')
            },
    }
    payment = client.order.create(data=paymentData)
    print('payment',payment)
    mysql.connection.commit()
    cursor.close()
    return payment


def format_payment_message(event, payment):
    notes = payment.get('notes', {})
    text = ''
    if event == 'payment.captured':
        text = (
            f"You received a new payment of *₹{payment['amount'] / 100}* on your Razorpay account - {client.auth[0]}\n\n"
            f"Payment ID : *{payment['id']}*\n"
            f"Customer : {payment.get('email', '')}\n"
            f"Contact : {payment.get('contact', '')}\n"
            f"Captured at : {datetime.datetime.now().strftime('%d-%m-%Y')}\n"
            f"Payment for : {notes.get('payment_for', '')}"
        )
    elif event == 'payment.failed':
        text = (
            f"Payment for *₹{payment['amount'] / 100}* failed\n\n"
            f"Payment ID : *{payment['id']}*\n"
            f"Customer : {payment.get('email', '')}\n"
            f"Contact : {payment.get('contact', '')}\n"
            f"Attempted at : {datetime.datetime.now().strftime('%d-%m-%Y')}\n"
            f"Payment for : {notes.get('payment_for', '')}\n"
            f"Payment via : {payment.get('method', '')}"
        )
    elif event == 'order.paid':
        text = (
            f"Order paid successfully for *₹{payment['amount'] / 100}*\n\n"
            f"Order ID : *{payment['order_id']}*\n"
            f"Payment ID : *{payment['id']}*\n"
            f"Customer : {payment.get('email', '')}\n"
            f"Contact : {payment.get('contact', '')}\n"
            f"Paid at : {datetime.datetime.now().strftime('%d-%m-%Y')}\n"
            f"Payment for : {notes.get('payment_for', '')}"
        )
    elif event == 'refund.processed':
        text = (
            f"Refund processed for *₹{payment['amount'] / 100}*\n\n"
            f"Refund ID : *{payment['refund_id']}*\n"
            f"Payment ID : *{payment['id']}*\n"
            f"Customer : {payment.get('email', '')}\n"
            f"Contact : {payment.get('contact', '')}\n"
            f"Processed at : {datetime.datetime.now().strftime('%d-%m-%Y')}\n"
            f"Refund for : {notes.get('payment_for', '')}"
        )
    return text

@payment_routes.route('/razorpay-webhook', methods=['POST'])
def webhook():
    webhook_secret = "0Sl7EYMtUt056Vr68hQuiZO/etjekbItCCaaqPE2"
    request_data = request.get_data(as_text=True)
    signature = request.headers.get('X-Razorpay-Signature')

    # Verify the webhook signature
    generated_signature = hmac.new(webhook_secret.encode(), request_data.encode(), hashlib.sha256).hexdigest()
    if hmac.compare_digest(generated_signature, signature):
        event = request.get_json()
        event_type = event['event']
        payment = event['payload']['payment']['entity']
        print('payment',payment)
        payment_id = payment['id']
        amount = payment['amount'] / 100

        # Update the database with payment success
        # cursor = mysql.connection.cursor()
        # if event_type == 'payment.captured':
        #     cursor.execute("UPDATE payments SET status='success' WHERE payment_id=%s", (payment_id,))
        # elif event_type == 'payment.failed':
        #     cursor.execute("UPDATE payments SET status='failed' WHERE payment_id=%s", (payment_id,))
        # elif event_type == 'order.paid':
        #     cursor.execute("UPDATE payments SET status='paid' WHERE payment_id=%s", (payment_id,))
        # elif event_type == 'refund.processed':
        #     cursor.execute("UPDATE payments SET status='refunded' WHERE payment_id=%s", (payment_id,))
        # mysql.connection.commit()
        # cursor.close()

        # Generate the message
        message = format_payment_message(event_type, payment)
        print('message', message)  # You can replace this with actual notification logic

        return jsonify({"message": "Webhook processed"}), 200
    else:
        return jsonify({"message": "Invalid signature"}), 400

