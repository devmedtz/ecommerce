#Vodacom mpesa intergrations
from portalsdk import APIContext, APIMethodType, APIRequest 
from time import sleep
import json
import datetime
from django.conf import settings
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .utils import cookieCart, cartData, guestOrder
from .models import Product, Order, OrderItem, ShippingAddress
from .forms import MakePaymentForm
from .models import MakePayment


def MakePaymentView(request, order_id):

    order = Order.objects.get(id=order_id)
    cart_price = order.cart_total

    if request.method == 'POST':
        form = MakePaymentForm(request.POST or None)
        if form.is_valid():

            #Begin payment processing
            public_key = settings.PUBLIC_KEY

            # Create Context with API to request a Session ID
            api_context = APIContext()

            # Api key
            api_context.api_key = settings.API_KEY

            # Public key
            api_context.public_key = public_key

            # Use ssl/https
            api_context.ssl = True

            # Method type (can be GET/POST/PUT)
            api_context.method_type = APIMethodType.GET

            # API address
            api_context.address = 'openapi.m-pesa.com'

            # API Port
            api_context.port = 443

            # API Path
            api_context.path = '/sandbox/ipg/v2/vodacomTZN/getSession/'

            # Add/update headers
            api_context.add_header('Origin', '*')

            # Parameters can be added to the call as well that on POST will be in JSON format and on GET will be URL parameters
            # api_context.add_parameter('key', 'value')

            #Do the API call and put result in a response packet
            api_request = APIRequest(api_context)

            # Do the API call and put result in a response packet
            result = None
            try:
                result = api_request.execute()
            except Exception as e:
                print('Call Failed: ' + e)

            if result is None:
                raise Exception('SessionKey call failed to get result. Please check.')

            # Display results
            print(result.status_code)
            print(result.headers)
            print(result.body)

            # The above call issued a sessionID
            api_context = APIContext()
            api_context.api_key = result.body['output_SessionID']
            api_context.public_key = public_key
            api_context.ssl = True
            api_context.method_type = APIMethodType.POST
            api_context.address = 'openapi.m-pesa.com'
            api_context.port = 443
            api_context.path = '/sandbox/ipg/v2/vodacomTZN/c2bPayment/singleStage/'
            api_context.add_header('Origin', '*') #127.0.0.1:8000 or Domain name

            phone = request.POST.get('phone')

            amount = str(cart_price)
            phone = str(phone)
            item_id  = str(order_id)


            print('cart_price', cart_price)
            print('phone', phone)
            print('item_id', item_id)


            api_context.add_parameter('input_Amount', amount)
            api_context.add_parameter('input_Country', 'TZN')
            api_context.add_parameter('input_Currency', 'TZS')
            api_context.add_parameter('input_CustomerMSISDN', '0767176929')
            api_context.add_parameter('input_ServiceProviderCode', '000000')
            api_context.add_parameter('input_ThirdPartyConversationID', 'asv02e5958774f7ba228d83d0d689761')
            api_context.add_parameter('input_TransactionReference', item_id)
            api_context.add_parameter('input_PurchasedItemsDesc', item_id)

            api_request = APIRequest(api_context)

            sleep(30)

            result = None

            try:
                result = api_request.execute()
            except Exception as e:
                print('Call Failed: ' + e)

            if result is None:
                raise Exception('API call failed to get result. Please check.')

            print(result.status_code)
            print(result.headers)
            print(result.body)  

            if result.body['output_ResponseCode'] == 'INS-0':
                payment = form.save(commit=False)
                payment.customer = request.user.customer
                payment.order_id = order_id
                payment.save()

                #save transactionID and mark paid status true
                order.transaction_id = result.body['output_TransactionID']
                order.paid_status = True
                order.save()
                return HttpResponse('Your Payment was Successfully sent!')

            elif result.body['output_ResponseCode'] == 'INS-1':
                messages.add_message(request, messages.ERROR, 'Internal Error')

            elif result.body['output_ResponseCode'] == 'INS-6':
                messages.add_message(request, messages.ERROR, 'Transaction Failed')

            elif result.body['output_ResponseCode'] == 'INS-9':
                messages.add_message(request, messages.ERROR, 'Request timeout')

            elif result.body['output_ResponseCode'] == 'INS-10':
                messages.add_message(request, messages.ERROR, 'Duplicate Transaction')

            else:
                messages.add_message(request, messages.ERROR, 'Configuration Error')
                 
    else:
        form = MakePaymentForm()

    context = {'form': form, 'order_id':order_id, 'cart_price':cart_price}

    return render(request, 'store/payment.html', context)
