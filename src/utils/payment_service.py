from models.plans_model import Plan
from models.coupon_model import Coupon
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal

def check_payment(cursor, data, user):
    try:
        plan_id = data.get('planId')
        if not plan_id:
            return {"isError": True, 'error': "plan Id is required", 'message': "plan Id is required"}

        plan = Plan.get_plan_by_id(cursor, plan_id)
        if not (plan and plan.get('isActive')):
            return {"isError": True, 'error': "Plan is not active", 'message': "Plan is not active"}

        # Determine subscription days
        subscription_days = {'monthly': 31, 'annual': 366, 'twoYear': 731}.get(plan.get('subscriptionPeriod'), 0)

        # Base payment data
        activation_date = datetime.now(timezone.utc)
        expiry_date = (activation_date + timedelta(days=subscription_days)).replace(hour=2, minute=0, second=0, tzinfo=timezone.utc)
        
        if user.get('status') == 'active' and user.get('expiryDate'):
            activation_date = user.get('expiryDate')
            current_expiry_date = user.get('expiryDate')
            additional_days = subscription_days - 1
            expiry_date = current_expiry_date + timedelta(days=additional_days)
            
        price = Decimal(str(plan.get('price')))  # Convert price to Decimal

        payment_data = {
            'planId': plan.get('id'),
            'userId': user.get('id'),
            'activationDate': activation_date,
            'expiryDate': expiry_date,
            'subTotalAmount': price,
            'subscriptionPeriod': plan.get('subscriptionPeriod'),
            'subscriptionDays': subscription_days
        }
        couponError = None
        # Handle coupon logic
        coupon = None
        coupon_code = data.get('couponCode')

        if coupon_code:
            coupon = Coupon.get_coupon_by_code(cursor, coupon_code) if coupon_code else None
            
        if coupon_code and not coupon:
            couponError = "Invalid coupon code"

        if coupon:
            if coupon and not coupon.get('isActive'):
                couponError = "Coupon is not active"

            if coupon and coupon.get('maxRedemption') <= coupon.get('redeemCount'):
                couponError = "Coupon is not available"

            if coupon and Decimal(str(coupon.get('minimumBillAmount') or '0')) > price:
                couponError = "Coupon is not applicable for this bill amount"
            
            if not str(plan_id) in json.loads(coupon.get('forPlans') or '[]'):
                couponError = "Coupon is not applicable for this plan"

        if coupon and coupon.get('isActive') and coupon.get('maxRedemption') > coupon.get('redeemCount') and Decimal(str(coupon.get('minimumBillAmount') or '0')) <= price and str(plan_id) in json.loads(coupon.get('forPlans') or '[]'):
            payment_data.update({
                'couponCode': coupon.get('code'),
                'offerType': coupon.get('offerType')
            })
            amount_str = str(coupon.get('value') or '0')
            amount = Decimal(amount_str)
            if coupon.get('offerType') == 'Amount':
                # Discount calculation
                if coupon.get('amountType') == 'Percentage':
                    discount = (amount / Decimal('100')) * price
                else:
                    discount = amount
                after_discount = max(price - discount, Decimal('0'))
            elif coupon.get('offerType') == 'Month':
                # Offer in days
                extra_days = (int(coupon.get('value')) * 30)
                payment_data['expiryDate'] = (expiry_date + timedelta(days=extra_days + 1)).replace(hour=2, minute=0, second=0, tzinfo=timezone.utc)
                after_discount = price
                discount = Decimal('0')

            # Final amount with tax (using Decimal)
            tax_amount = after_discount * Decimal('0.18')
            payment_data.update({
                'discountAmount': discount,
                'afterDiscountAmount': after_discount,
                'couponValue': coupon.get('value'),
                'taxAmount': tax_amount,
                'totalAmount': after_discount + tax_amount
            })

        else:
            # No valid coupon applied
            tax_amount = price * Decimal('0.18')
            payment_data.update({
                'taxAmount': tax_amount,
                'totalAmount': price + tax_amount
            })

        return {"isError": False, 'data': payment_data, 'couponError': couponError}
    except Exception as e:
        return {"isError": True, 'error': str(e), 'message': "An error occurred"}   
