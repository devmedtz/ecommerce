import json
import datetime
import re
from django.conf import settings
from django.shortcuts import render, Http404, HttpResponse
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

from .utils import cookieCart, cartData, guestOrder
from .models import Product, Order, OrderItem, ShippingAddress


@csrf_exempt
def validate_phone(request):

    if request.method == "GET":
        raise Http404("URL doesn't exists")
    else:   
        response_data = {}

        phone = request.POST["phone"]
        
        x = re.search("^2557[0-9]{8}$", phone)

        if not x:
            response_data["is_success"] = False
        else:
            response_data["is_success"] = True

        return JsonResponse(response_data)




# Create your views here.
def store(request):
    data = cartData(request)

    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems': cartItems}
    
    return render(request, 'store/cart.html', context)


def checkout(request):

    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems': cartItems}
    
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body) 
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item is added', safe=False)


def processOrder(request):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])

    if total == order.get_cart_total:
        order.complete = True
        order.cart_total = order.get_cart_total
    order.save()

    order_id = order.id

    print('order_id', order_id)

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted...', safe=False)
