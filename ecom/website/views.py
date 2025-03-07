import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Product, Category, Order
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("/signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("/signup")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect("/login")

    return render(request, "signup.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("/")
        else:
            messages.error(request, "Invalid username or password!")
            return redirect("/login")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("/")

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def index(request):
    featured = Product.objects.filter(featured=True)
    cat = Category.objects.all()
    return render(request, 'home.html', {"featured": featured, "categories": cat})

def see_product(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, "product.html", {"product": product})

def buy_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('/login')
    product = Product.objects.get(id=product_id)

    if product.quantity < 1:
        return redirect(f"/product/{product_id}")

    # Razorpay Order Details
    order_amount = int(product.rate * 100)  # Razorpay expects amount in paisa (INR * 100)
    order_currency = 'INR'
    order_receipt = f'order_rcptid_{product.pk}'

    # Create Razorpay Order with payment_capture=0 (manual capture)
    razorpay_order = razorpay_client.order.create({
        'amount': order_amount,
        'currency': order_currency,
        'receipt': order_receipt,
        'payment_capture': '0',  # Manual capture
        'notes': {'product_id': product.pk, "user": request.user.email}  # Store product ID in notes
    })

    # Store order_id in session
    request.session['razorpay_order_id'] = razorpay_order['id']


    return render(request, "payment.html", {
        "rs":order_amount/100,
        "product": product,
        "order_id": razorpay_order['id'],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": order_amount
    })
@csrf_exempt
def capture_payment(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")

        try:
            # Fetch order details from Razorpay
            order_details = razorpay_client.order.fetch(order_id)
            product_id = order_details['notes'].get('product_id')
            user_email = order_details['notes'].get('user')
            if not product_id:
                return JsonResponse({"error": "Product ID not found in notes"}, status=400)

            product = Product.objects.get(id=product_id)

            # Capture the payment
            capture_response = razorpay_client.payment.capture(payment_id, order_details['amount'])
            
            # Reduce product quantity after successful payment capture
            if product.quantity > 0:
                product.quantity -= 1
                product.save()
            user = User.objects.get(email = user_email)
            order = Order.objects.create(user=user, product=product)
            order.save()
            return redirect('/payment_success')
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

def payment_success(request):
    return render(request, "success.html")

def browse_category(request, cat_id):
    category = Category.objects.get(id=cat_id)
    products = Product.objects.filter(category=category)
    return render(request, "explore_category.html", {"category": category, "products": products})


def myorders(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    orders = Order.objects.filter(user=request.user).order_by("-ordered_at")
    return render(request, "myorders.html", {"orders": orders})