from django.shortcuts import render
from django.http import JsonResponse
from django_daraja.mpesa.core import MpesaClient
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Payment
from dashboard.models import UserSubscription, SubscriptionPlan

def home(request):
    return render(request, 'pay.html')

def lipa_na_mpesa(request):
    if request.method == 'POST':
        phone_number = request.POST.get("phone")
        amount = int(request.POST.get("amount"))
        account_reference = "grok"
        transaction_desc = "payment for school fees"
        callback_url = "https://nonbituminous-flatteredly-jaunita.ngrok-free.dev/payments/callback/"

        cl = MpesaClient()
        response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)

        # Decode HTTPResponse into JSON dict
        response_data = json.loads(response.content.decode("utf-8"))

        # Extract checkout request ID
        checkout_request_id = response_data.get("CheckoutRequestID")

        # Save pending payment with checkout_request_id
        Payment.objects.create(
            user=request.user,
            amount=amount,
            phone_number=phone_number,
            status='pending',
            checkout_request_id=checkout_request_id
        )
        return JsonResponse(response_data)
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        print("Callback data:", data)

        # Extract transaction details
        stk_callback = data.get("Body", {}).get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")
        checkout_request_id = stk_callback.get("CheckoutRequestID")

        # Find the payment record
        payment = Payment.objects.filter(checkout_request_id=checkout_request_id).first()

        if result_code == 0 and payment:  # Success
            # Extract M-Pesa receipt number
            items = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            mpesa_receipt = None
            for item in items:
                if item.get("Name") == "MpesaReceiptNumber":
                    mpesa_receipt = item.get("Value")

            # Update payment record
            payment.status = 'success'
            payment.transaction_id = mpesa_receipt
            payment.result_desc = result_desc
            payment.save()

            # Activate subscription
            plan = SubscriptionPlan.objects.filter(price_kes=payment.amount).first()
            if plan:
                sub, created = UserSubscription.objects.get_or_create(user=payment.user)
                sub.activate(plan)

        elif payment:
            payment.status = 'failed'
            payment.result_desc = result_desc
            payment.save()

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    return JsonResponse({"error": "Invalid request method"}, status=400)
