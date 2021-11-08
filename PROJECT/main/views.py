from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail, BadHeaderError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.db.models.query_utils import Q
from django.views.generic import DetailView, View
from .filters import ItemFilter

from main.forms import UserAdminCreationForm
from main.models import *
from .utils import cookieCart, cartData, guestOrder
from main.tokens import account_activation_token
from django.conf import settings

import json
import datetime


User = get_user_model()


def index(request):

    data = cartData(request)
    cartItems = data['cartItems']
    categories = Category.objects.all()


    context = {
        'cartItems': cartItems,
        'categories': categories
    }

    return render(request, 'main/index.html', context)


def profile(request):

    data = cartData(request)
    cartItems = data['cartItems']
    categories = Category.objects.all()

    context = {
        'cartItems': cartItems,
        'categories': categories
    }
    return render(request, 'registration/profile.html', context)


def about(request):

    data = cartData(request)
    cartItems = data['cartItems']
    categories = Category.objects.all()

    context = {
        'cartItems': cartItems,
        'categories': categories
    }
    return render(request, 'main/about.html', context)


def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    categories = Category.objects.all()

    context = {'items': items,
               'order': order,
               'cartItems': cartItems,
               'categories': categories}
    return render(request, 'main/cart.html', context)


def checkout(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    categories = Category.objects.all()

    context = {'items': items,
               'order': order,
               'cartItems': cartItems,
               'categories': categories
               }
    return render(request, 'main/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Item.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    print('Data:', request.body)

    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    # total = int(['form']['total'])
    order.transaction_id = transaction_id

    # if total == order.get_cart_total:
    order.complete = True
    order.save()

    return JsonResponse('Payment complete', safe=False)


def product_page(request):

    data = cartData(request)
    cartItems = data['cartItems']

    categories = Category.objects.all()
    category_id = request.GET.get('category')

    if category_id:
        products = Item.objects.filter(category = category_id)
    else:
        products = Item.objects.all()

    myFilter = ItemFilter(request.GET, queryset=products)
    products = myFilter.qs

    context = {
        'products': products,
        'cartItems': cartItems,
        'categories': categories,
        'myFilter': myFilter
    }
    return render(request, 'main/products.html', context)



def product_detail(request, slug):

    data = cartData(request)
    cartItems = data['cartItems']
    categories = Category.objects.all()

    product = Item.objects.get(slug=slug)
    context = {
        'product': product,
        'cartItems': cartItems,
        'categories': categories
    }
    return render(request, 'main/product_detail.html', context)


def logoutUser(request):
    logout(request)
    return redirect('/')


def register(request):
    if request.method == 'POST':
        form = UserAdminCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Активация аккаунта'
            message = render_to_string('main/mail_body.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject,
                message,
                settings.EMAIL_HOST_USER,
                to=[to_email]
            )
            email.fail_silently=False
            email.send()
            return render(request, 'main/confirm_email_alert.html')
    else:
        form = UserAdminCreationForm()
    return render(request, 'main/register.html', {'form': form})


def activate(request, uidb64, token):

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        customer = Customer.objects.create(user=user, name = user.first_name + " " + user.last_name,
            email = user.email)
        login(request, user)
        # return redirect('home')
        return render(request, 'main/confirm_template.html', {'user': user})
    else:
        return HttpResponse('Ссылка недействительна. Попробуйте ещё раз.')


def password_reset(request):
    if request.method == "POST":
        form = PasswordAdminResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=email))
            if associated_users.exists():
                for user in associated_users:
                    mail_subject = "Смена пароля"
                    email_template_name = "main/password_reset_email.txt"
                    message = render_to_string(email_template_name, {
                        "email": user.email,
                        'domain': current_site.domain,
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': account_activation_token.make_token(user),
                        'protocol': 'https',
                    })
                    try:
                        to_email = form.cleaned_data.get('email')
                        email = EmailMessage(
                            mail_subject, message, to=[to_email]
                        )
                        email.send()
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordAdminResetForm()
    return render(request=request, template_name="main/password_reset.html",
                  context={"password_reset_form": password_reset_form})
