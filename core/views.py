from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages as toast
from django.contrib.auth import authenticate, login as auth_login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProductForm,VideoProductForm
from .forms import *
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import JsonResponse
from django.utils.text import slugify
from decimal import Decimal, InvalidOperation
from .models import ScrollingImages
from django.forms import modelformset_factory, inlineformset_factory
from .models import Product, ProductImage, Cart,Profile,VideoProduct,Payment
from django.db import transaction
import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Blog


INDIAN_PINCODES = {
    'serviceable': [
        '110001', '400001', '600001', '700001', '560001',
        '500001', '380001', '302001', '122001', '201301'
    ],
    'non_serviceable': ['517214']
}

@csrf_exempt
def check_delivery(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pincode = data.get('pincode', '').strip()
            
            if not pincode.isdigit() or len(pincode) != 6:
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter a valid 6-digit Indian pincode'
                })
            
            if pincode in INDIAN_PINCODES['serviceable']:
                return JsonResponse({
                    'success': True,
                    'message': 'Delivery available to this pincode!',
                    'delivery_time': '3-5 business days',
                    'cod_available': True
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Currently we are not available in this pincode!',
                    'delivery_time': '5-7 business days',
                    'cod_available': False
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


def home(request):
    scrolling_images = ScrollingImages.objects.all()
    categories = Category.objects.all()
    new_arrivals = Product.objects.all().order_by('-created_at')[:3]
    banners = Banner.objects.all()
    products = Product.objects.all()
    video = VideoProduct.objects.all()
    
    home_blogs = Blog.objects.filter(is_active=True, show_on_home=True).order_by('-priority')[:3]
    
    return render(request, 'frontend/index.html', {
        'scrolling_images': scrolling_images,
        'categories': categories, 
        'new_arrivals': new_arrivals,
        'banners': banners, 
        'products': products,
        'video': video,
        'latest_blogs': home_blogs
    })


def signup_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if password != confirm_password:
            toast.error(request, "Passwords do not match")
            return render(request, 'frontend/signup.html')

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                )

                Profile.objects.create(
                    user=user,
                    name=name,
                    gender=gender[0].upper(),
                    phone_number=mobile,
                    email=email,
                )

                toast.success(request, "Account created successfully! Please log in.")
                return redirect('login')
        except Exception as e:
            toast.error(request, f"Error: {str(e)}")
            return render(request, 'frontend/signup.html')

    return render(request, 'frontend/signup.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            toast.success(request, "Logged in successfully.")
            return redirect('home')
        else:
            toast.error(request, 'Invalid credentials.')

    return render(request, 'frontend/login.html')

def logout_page(request):
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all() 
    cart_count = Cart.objects.filter(user=request.user).count()


    return render(request, 'frontend/logout-page.html', {
        'products': products,
        'categories': categories,
        'cart_count': cart_count
    })


def admin_login(request):
    if request.user.is_authenticated:
        
        if request.user.is_superuser:
            return redirect('dashboard')
        else:
            toast.error(request, "Access denied. Superuser only.")
            return redirect('login')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                auth_login(request, user)
                toast.success(request, "Logged in successfully.")
                return redirect('dashboard')
            else:
                toast.error(request, "Only superusers can access this page.")
                return redirect('login')
        else:
            toast.error(request, 'Invalid credentials.')

    return render(request, 'backend/login.html')


def signout(request):
    logout(request)
    return redirect('login')


def video_products_list(request):
    video = VideoProduct.objects.all().order_by('-created_at')
    context = {'video': video}
    return render(request, 'backend/video_products/list.html', context)


def create_video_product(request):
    if request.method == 'POST':
        form = VideoProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            toast.success(request, 'Video product created successfully!')
            return redirect('video_products_list')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    toast.error(request, f"{field}: {error}")
    else:
        form = VideoProductForm()
    
    context = {'form': form, 'title': 'Create Video Product'}
    return render(request, 'backend/video_products/form.html', context)


def edit_video_product(request, pk):
    product = get_object_or_404(VideoProduct, pk=pk)
    if request.method == 'POST':
        form = VideoProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            toast.add_message(request, toast.SUCCESS, 'Video product updated successfully!')
            return redirect('video_products_list')
        else:
            toast.add_message(request, toast.ERROR, 'Please correct the errors below.')
    else:
        form = VideoProductForm(instance=product)
    
    context = {'form': form, 'title': 'Edit Video Product'}
    return render(request, 'backend/video_products/form.html', context)

def delete_video_product(request, pk):
    product = get_object_or_404(VideoProduct, pk=pk)
    if request.method == 'POST':
        product.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required(login_url='login')
def cart_items(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    addresses = request.user.addresses.all()

    for product_id, item in cart.items():
        total_price = item['price'] * item['quantity']
        items.append({
            'id': product_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total_price': total_price,
            'image_url': item['image_url'],
        })
        total += total_price

    return JsonResponse({'items': items, 'cart_total': total ,'addresses': addresses})

 
@login_required(login_url='login')
def cart_view(request):
    """Display all cart items of the logged-in user"""
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    cart_total = sum(item.subtotal() for item in cart_items)
    categories = Category.objects.all()
    category = Category.objects.all()
    addresses = request.user.addresses.all()


    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'category': category,
        'categories': categories,
        'addresses': addresses

    }
    return render(request, 'frontend/cart.html', context)


@login_required(login_url='login')
def delete_cart_item(request, cart_id):
    if request.method == "POST":
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        cart_item.delete()
        return JsonResponse({
            "success": True,
            "message": "Item removed successfully"
        })
    else:
        return JsonResponse({
            "success": False,
            "error": "Invalid request method"
        }, status=400)
from django.views.decorators.csrf import csrf_exempt
import json
@login_required
@csrf_exempt
def update_cart_quantity(request, cart_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            action = data.get("action")

            cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)

            # Adjust quantity
            if action == "increment":
                cart_item.quantity += 1
            elif action == "decrement" and cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                return JsonResponse({"success": False, "error": "Invalid action or quantity"})

            cart_item.save()

            return JsonResponse({
                "success": True,
                "new_quantity": cart_item.quantity,
                "new_subtotal": float(cart_item.subtotal()),
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def get_cart_items(request):
    """
    """
    cart_items = Cart.objects.filter(user=request.user)
    data = []
    cart_total = 0

    for item in cart_items:
        total_price = item.quantity * item.price_at_addition
        cart_total += total_price
        data.append({
            "id": item.id,
            "name": item.product.name,
            "image_url": item.product.image.url if item.product.image else "",
            "quantity": item.quantity,
            "price": float(item.price_at_addition),
            "total_price": float(total_price),
        })

    return JsonResponse({
        "cart_items": data,
        "cart_total": float(cart_total)
    })

@login_required(login_url='login')
def add_to_cart_ajax(request):
    return 



@login_required(login_url='login')
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")
            quantity = int(data.get("quantity", 1))

            product = Product.objects.get(id=product_id)

            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={"quantity": quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return JsonResponse({"success": True, "message": f"{product.name} added to cart."})

        except Product.DoesNotExist:
            return JsonResponse({"success": False, "message": "Product not found."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)





@login_required
@csrf_exempt
def checkout_from_cart(request):
    """
    POST /checkout/
    JSON payload:
    {
        "address_id": 5,
        "payment_method": "cod" | "online"
    }
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    address_id = data.get("address_id")
    payment_method = data.get("payment_method")

    if not address_id:
        return JsonResponse({"success": False, "message": "address_id is required"}, status=400)
    if payment_method not in ["cod", "online"]:
        return JsonResponse({"success": False, "message": "Invalid payment_method"}, status=400)

    # Fetch address
    try:
        address = Address.objects.get(id=address_id, user=request.user)
    except Address.DoesNotExist:
        return JsonResponse({"success": False, "message": "Address not found"}, status=404)

    # Fetch cart items
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    if not cart_items.exists():
        return JsonResponse({"success": False, "message": "Cart is empty"}, status=400)

    # === ONLINE PAYMENT DISABLED ===
    if payment_method == "online":
        return JsonResponse({
            "success": False,
            "message": "Online payment is currently disabled. Please use Cash on Delivery."
        }, status=400)

    # === CASH ON DELIVERY → status = completed ===
    order_status = "completed" if payment_method == "cod" else "pending"

    with transaction.atomic():
        # Create Order
        total = sum(item.subtotal() for item in cart_items)
        order = Order.objects.create(
            user=request.user,
            address=address,
            payment_method=payment_method,
            status=order_status,
            total_amount=total
        )

        # Create OrderItems & clear cart
        order_items = []
        for cart_item in cart_items:
            order_items.append(
                OrderItem(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.product.discounted_price
                )
            )
        OrderItem.objects.bulk_create(order_items)

        # Empty cart
        cart_items.delete()

    return JsonResponse({
        "success": True,
        "message": "Order placed successfully!",
        "order_id": order.id,
        "status": order.status,
        "total": float(order.total_amount)
    })






@login_required(login_url='login') 
def profile_page(request):
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all() 
    cart_count = Cart.objects.filter(user=request.user).count()
    user_orders_count = request.user.orders.count()  # count orders related to logged-in user



    return render(request, 'frontend/profile-page.html', {
        'products': products,
        'categories': categories,
        'cart_count': cart_count,
        'user_orders_count': user_orders_count,

    })

@login_required
def orders_page(request):
    # Get user's orders with related items
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')

    # Common context (keep your existing sidebar data)
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all()
    cart_count = Cart.objects.filter(user=request.user).count()

    return render(request, 'frontend/orders-page.html', {
        'orders': orders,
        'products': products,
        'categories': categories,
        'cart_count': cart_count
    })


@login_required
def address_profile(request):    
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all() 
    cart_count = Cart.objects.filter(user=request.user).count()
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')

    return render(request, 'frontend/address-page.html', {
        'products': products,
        'categories': categories,
        'cart_count': cart_count,
        'addresses': addresses,
    })


@csrf_exempt
@login_required
def create_address(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        if data.get('is_default'):
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        address = Address.objects.create(
            user=request.user,
            first_name=data['first_name'],
            last_name=data['last_name'],
            mobile_number=data['mobile_number'],
            address_type=data['address_type'],
            address_line_one=data['address_line_one'],
            address_line_two=data.get('address_line_two', ''),
            city=data['city'],
            zip_code=data['zip_code'],
            is_default=data.get('is_default', False)
        )
        return JsonResponse({
            'id': address.id,
            'first_name': address.first_name,
            'last_name': address.last_name,
            'mobile_number': address.mobile_number,
            'address_type': address.get_address_type_display(),
            'address_line_one': address.address_line_one,
            'address_line_two': address.address_line_two,
            'city': address.city,
            'zip_code': address.zip_code,
            'is_default': address.is_default
        })
    return JsonResponse({'error': 'Invalid request method'})


@login_required
def get_address(request, pk):
    address = get_object_or_404(Address, id=pk, user=request.user)
    data = {
        "first_name": address.first_name,
        "last_name": address.last_name,
        "mobile_number": address.mobile_number,
        "address_type": address.address_type,
        "address_line_one": address.address_line_one,
        "address_line_two": address.address_line_two,
        "city": address.city,
        "zip_code": address.zip_code,
        "is_default": address.is_default,
    }
    return JsonResponse(data)


@login_required
def update_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        address.first_name = data['first_name']
        address.last_name = data['last_name']
        address.mobile_number = data['mobile_number']
        address.address_type = data['address_type']
        address.address_line_one = data['address_line_one']
        address.address_line_two = data.get('address_line_two', '')
        address.city = data['city']
        address.zip_code = data['zip_code']
        address.is_default = data.get('is_default', False)

        if address.is_default:
            Address.objects.filter(user=request.user, is_default=True).exclude(id=pk).update(is_default=False)

        address.save()

        return JsonResponse({
            'id': address.id,
            'first_name': address.first_name,
            'last_name': address.last_name,
            'mobile_number': address.mobile_number,
            'address_type': address.get_address_type_display(),
            'address_line_one': address.address_line_one,
            'address_line_two': address.address_line_two,
            'city': address.city,
            'zip_code': address.zip_code,
            'is_default': address.is_default
        })



@login_required
def delete_address(request, pk):
    Address.objects.filter(id=pk, user=request.user).delete()
    return JsonResponse({'success': True})


@login_required
def set_default_address(request, pk):
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    Address.objects.filter(id=pk, user=request.user).update(is_default=True)
    return JsonResponse({'success': True})



@login_required
def update_profile(request):
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all() 
    cart_count = Cart.objects.filter(user=request.user).count()
    cart_count = Cart.objects.filter(user=request.user).count()

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user
        error = None

        # Update username and email
        if username:
            user.username = username
        if email:
            user.email = email

        # Update password if fields are filled
        if current_password or new_password or confirm_password:
            if not user.check_password(current_password):
                error = "Current password is incorrect."
            elif new_password != confirm_password:
                error = "New passwords do not match."
            else:
                user.set_password(new_password)
                update_session_auth_hash(request, user)  # Keep user logged in after password change

        if error:
            messages.error(request, error)
        else:
            user.save()
            messages.success(request, "Profile updated successfully!")

    return render(request, 'frontend/update-profile.html', {
        'products': products,
        'categories': categories,
        'cart_count': cart_count,
        'user': request.user,
    })


@login_required
def profile(request):
    return render(request, 'frontend/profile.html', {'user': request.user})

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in
            return JsonResponse({'success': True})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'errors': errors})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Order
# views.py
 

def order_detail(request, order_id):
    if request.user.is_superuser:
        order = get_object_or_404(
            Order.objects.select_related('user').prefetch_related('items__product'),
            id=order_id
        )

        return render(request, 'backend/order-details.html', {
            'order': order
        })
    else:
        return redirect('home')

def orders_list(request):
    orders = Order.objects.select_related('user').prefetch_related('items').all().order_by('-created_at')

    total_orders = orders.count()
    cancelled_orders = orders.filter(status='cancelled').count()
    delivered_orders = orders.filter(status='completed').count()

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'cancelled_orders': cancelled_orders,
        'delivered_orders': delivered_orders,
    }

    return render(request, 'backend/orders-list.html', context)
@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')

    return render(request, 'frontend/orders.html', {
        'orders': orders
    })



from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Wishlist


@login_required
def toggle_wishlist(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    )

    if wishlist_item.exists():
        wishlist_item.delete()
        return JsonResponse({'status': 'removed'})
    else:
        Wishlist.objects.create(user=request.user, product=product)
        return JsonResponse({'status': 'added'})

@login_required
def wishlist_page(request):
    wishlist_products = Wishlist.objects.filter(user=request.user).select_related('product')
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'frontend/wishlist.html', {
        'wishlist_products': wishlist_products,
        'products': products,
        'categories': categories
    })

def terms_and_conditions(request):
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all() 
    return render(request, 'frontend/terms-and-conditions.html', {
        'products': products,
        'categories': categories,
    })

def privacy_policy(request):
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all() 
    return render(request, 'frontend/privacy-and-policy.html', {
        'products': products,
        'categories': categories,
    })

def return_policy(request):
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all() 
    return render(request, 'frontend/return-policy.html', {
        'products': products,
        'categories': categories,
    })

def faq(request):
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all() 
    return render(request, 'frontend/faq.html', {
        'products': products,
        'categories': categories,
    })

def booking_policy(request):
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all() 
    return render(request, 'frontend/booking-policy.html', {
        'products': products,
        'categories': categories,
    })


from django.shortcuts import render, get_object_or_404
from .models import Blog


def blog_list(request):
    blogs = Blog.objects.filter(is_active=True).order_by('-created_at')
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'frontend/blogs.html', {
        'blogs': blogs,
        'products': products,
        'categories': categories
    })

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug, is_active=True)
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'frontend/blog-detail.html', {
        'blog': blog,
        'products': products,
        'categories': categories
    })


def contactus(request):
    success = False
    if request.method == 'POST':
        # Process form (add send_mail later)
        success = True
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'frontend/contactus.html', {
        'success': success,
        'products': products,
        'categories': categories
    })



def shop(request, ):
    product = get_object_or_404(Product.objects.prefetch_related('accordions'), slug=request.GET.get('product')) if request.GET.get('product') else None
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all()

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    selected_categories = request.GET.getlist('category')
    selected_colors = request.GET.getlist('color')

    if min_price:
        products = products.filter(discounted_price__gte=min_price)

    if max_price:
        products = products.filter(discounted_price__lte=max_price)

    if selected_categories:
        products = products.filter(category__id__in=selected_categories)

    if selected_colors:
        products = products.filter(color__in=selected_colors)

    colors = Product.objects.values_list('color', flat=True).distinct()

    return render(request, 'frontend/shop.html', {
        'products': products,
        'categories': categories,
        'colors': colors,
        'selected_categories': selected_categories,
        'product': product,
        'selected_colors': selected_colors,
        'min_price': min_price,
        'max_price': max_price,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.prefetch_related('accordions'), slug=slug)
    categories = Category.objects.all() 
    new_arrivals = Product.objects.all().order_by('-created_at')[:3]
    product_list = Product.objects.all()

    context = {
        'categories': categories,
        'product': product,
        'new_arrivals': new_arrivals,
        'products': product_list

    }
    return render(request, 'frontend/product-detail.html', context)

def cateogry_products(request, slug):
    categories = Category.objects.all()
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter(category=category)

    wishlist_product_ids = []

    if request.user.is_authenticated:
        wishlist_product_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'wishlist_product_ids': wishlist_product_ids,
    }

    return render(request, 'frontend/category-products.html', context)


ProductImageFormSet = inlineformset_factory(
    Product, ProductImage,
    fields=('image',),
    extra=3,
    can_delete=True
)
 

def rc_gallery(request):
    categories = Category.objects.all()
    category = Category.objects.all()
    products = Product.objects.all()


    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'frontend/gallery.html', context)


# logout
@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('login')




# BACKEND
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'backend/index.html')

@login_required(login_url='login')
def categories(request):
    # notifications_list = Notification.objects.filter(read_status = False).order_by('-created_at')

    categories = Category.objects.all().order_by('-created_at')
    category_slug = request.GET.get('edit') or request.GET.get('delete')
    print(category_slug)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
    else:
        category = None

    print(request.POST)

    if request.method == 'POST':
        print(request.POST)
        if 'slug' in request.POST:
            form = CategoryForm(request.POST, request.FILES, instance=category)
        else:
            form = CategoryForm(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            toast.success(request, 'Category updated successfully!' if category else 'Category created successfully!')
            return redirect('categories')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    print(error)
                    toast.error(request, f"{field}: {error}")
            toast.error(request, 'Please correct the errors below.')

    elif request.method == 'GET' and category and 'delete' in request.GET:
        category.delete()
        toast.success(request, 'Category deleted successfully!')
        return redirect('categories')

    else:
        form = CategoryForm(instance=category)

    return render(request, 'backend/categories.html', {
        'form': form,
        'categories': categories,
        'edit_mode': bool(category),
    })


def admin_logout(request):
    logout(request)
    return redirect('login')



@login_required(login_url='login')
def products(request):
    product_list = Product.objects.all()
    return render(request, 'backend/products.html', {'products': product_list})



@login_required(login_url='login')
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        image_formset = ProductImageFormSet(request.POST, request.FILES, prefix='images')
        accordion_formset = AccordionFormSet(request.POST, prefix='accordions')
        
        if form.is_valid() and image_formset.is_valid() and accordion_formset.is_valid():
            product = form.save()
            
            # Save images
            image_formset.instance = product
            image_formset.save()
            
            # Save accordions
            accordion_formset.instance = product
            accordion_formset.save()
            
            toast.success(request, 'Product created successfully.')
            return redirect('products')
        else:
            print(form.errors)
            toast.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
        image_formset = ProductImageFormSet(prefix='images')
        accordion_formset = AccordionFormSet(prefix='accordions')
    
    return render(request, 'backend/create-product.html', {
        'form': form,
        'image_formset': image_formset,
        'accordion_formset': accordion_formset,
    })
@login_required(login_url='login')
def edit_product(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            print("Form is valid")

            product = form.save()

            # ✅ ADD NEW IMAGES
            if 'additional_images' in request.FILES:
                for image in request.FILES.getlist('additional_images'):
                    ProductImage.objects.create(product=product, image=image)

            # ✅ DELETE IMAGES
            delete_images = request.POST.getlist('delete_images')
            if delete_images:
                ProductImage.objects.filter(id__in=delete_images, product=product).delete()

            # DELETE accordions
            delete_accordions = request.POST.getlist('delete_accordions')
            if delete_accordions:
                product.accordions.filter(id__in=delete_accordions).delete()

            # UPDATE existing accordions
            for accordion in product.accordions.all():
                title = request.POST.get(f'accordion-title-{accordion.id}')
                desc = request.POST.get(f'accordion-desc-{accordion.id}')

                if title and desc:
                    accordion.name = title
                    accordion.description = desc
                    accordion.save()

            # ADD new accordions
            new_titles = request.POST.getlist('new-accordion-title[]')
            new_descs = request.POST.getlist('new-accordion-desc[]')

            for title, desc in zip(new_titles, new_descs):
                if title and desc:
                    Accordion.objects.create(
                        product=product,
                        name=title,
                        description=desc
                    )

            toast.success(request, 'Product updated successfully.')
            return redirect('products')

        else:
            print("FORM ERRORS:", form.errors)
            toast.error(request, 'Please correct the errors below.')

    else:
        form = ProductForm(instance=product)

    return render(request, 'backend/edit-product.html', {
        'form': form,
        'product': product,
    })



@login_required(login_url='login')
def delete_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        product.delete()
        return JsonResponse({'success': True})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})

@login_required(login_url='login')
def add_banner(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            toast.success(request, "Banner Created Successfully")
            return redirect('banners')
        else:
            print(form.errors)  # Fixed the typo here
            toast.error(request, 'Failed to Create banner. Please check the form for errors.')
    form = BannerForm()
    context = {
        'form': form
    }
    return render(request, 'backend/add-banners.html', context)


@login_required(login_url='login')
def banners(request):
    banners = Banner.objects.all()
    context = {'banners': banners}
    return render(request, 'backend/banners.html',context)



@login_required(login_url='login')
def update_banner(request, pk):
    banner = get_object_or_404(Banner, id=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            toast.success(request, 'Banner Updated Successfully')
            return redirect('banners')
        else:
            toast.error(request, 'Failed to update banner. Please check the form for errors.')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'backend/update-banner.html', {'form': form, 'banner': banner})



@login_required(login_url='login')
def delete_banner(request, pk):
    try:
        banner = Banner.objects.get(pk=pk)
        banner.delete()
        toast.success(request, 'Banner deleted successfully.')
        return redirect('banners')
    except Banner.DoesNotExist:
        toast.error(request, 'Banner not found.')
        return redirect('banners')



@login_required(login_url='login')
def customer_list(request):
    customers = Profile.objects.select_related('user').all()
    return render(request, 'backend/customer_list.html', {'customers': customers})
import datetime
from .models import Cart
@login_required(login_url='login')
def customer_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    wishlist_items = Wishlist.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    orders = Order.objects.filter(user=user)

    context = {
        'user': user,
        'profile': profile,
        'wishlist_items': wishlist_items,
        'cart_items': cart_items,
        'orders': orders,
    }
    return render(request, 'backend/customer_detail.html', context)



@login_required(login_url='login')
def orders(request):
    return render(request, 'backend/orders.html')

def order_details(request):
    return render(request, 'backend/order-details.html')


@login_required(login_url='adminlogin')
def collect_cash(request, order_id):

    if request.user.is_superuser:

        order = get_object_or_404(Order, id=order_id)
        order.status = 'delivered'
        order.save()

        try:
            payment = Payment.objects.get(order=order)
            payment.status = "success"
            payment.save()
        except Payment.DoesNotExist:
            pass

        # redirect back to same page
        return redirect(request.META.get('HTTP_REFERER', 'orders_list'))

    else:
        return redirect('home')
    

# message view 
@login_required(login_url='login')
def messages(request):
   
    inbox = Message.objects.all().order_by('-created_at')
    inbox_count = Message.objects.all().count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    context = {'inbox': inbox, 'now':now, 'inbox_count': inbox_count}
    return render(request, 'backend/messages.html', context)


@login_required(login_url='login')
def view_messages(request):
    return render(request, 'backend/view-toast.html')

@login_required(login_url='login')
def payments(request):
    return render(request, 'backend/payments.html')

@login_required(login_url='adminlogin')
def payment_list(request):

    if request.user.is_superuser:

        payments = Payment.objects.filter(status='success').select_related(
            'order','user'
        ).prefetch_related(
            'order__items',
            'order__items__product'
        )

        return render(request,'backend/payment-list.html',{
            'payments':payments
        })

    else:
        return redirect('home')

def payment_detail(request, payment_id):

    if request.user.is_superuser:

        payment = get_object_or_404(
            Payment.objects.select_related('order','user').prefetch_related('order__items__product'),
            id=payment_id
        )

        return render(request,'backend/payment-detail.html',{
            'payment':payment
        })

    else:
        return redirect('home')

@login_required(login_url='login')
def gallery(request):

    galleries = Gallery.objects.all()
    context = {
        'galleries': galleries
    }

    return render(request, 'backend/gallery.html', context)

@login_required(login_url='login')
def add_gallery(request):
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            toast.success(request, " Image Added Successfully")
            return redirect('gallery')
        else:
           toast.error(request, 'Failed to Add Image. Please check the form for errors.')

    form = GalleryForm()
    context = {
        'form': form
    }
    return render(request, 'backend/add-gallery.html', context)




@login_required(login_url='login')
def delete_gallery(request, pk):
    try:
        gallery = Gallery.objects.get(id=pk)
        gallery.delete()
        toast.success(request, 'image deleted successfully.')
        return redirect('gallery')
    except Gallery.DoesNotExist:
        toast.error(request, 'image not found.')
        return redirect('gallery')





@login_required(login_url='login')
def scrolling_images(request):
    
    scrolling_images = ScrollingImages.objects.all()
    context = {
        'scrolling_images': scrolling_images
    }
    return render(request, 'backend/scrolling-images.html', context)




@login_required(login_url='login')
def add_scrolling_images(request):
    if request.method == 'POST':
        form = ScrollingImagesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            toast.success(request, " Scrolling Image Added Successfully")
            return redirect('scrolling_images')
        else:
           toast.error(request, 'Failed to Add Image. Please check the form for errors.')

    form = ScrollingImagesForm()
    context = {
        'form': form
    }
    return render(request, 'backend/add-scroll.html', context)




def delete_scrolling_images(request, pk):  # Change from id to pk
    image = get_object_or_404(ScrollingImages, id=pk)
    image.delete()
    return redirect('scrolling_images')



# blog for dashboard
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Blog
from .forms import BlogForm

# Blog listing page
def dashboard_blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'backend/blog_list.html', {'blogs': blogs})

# Blog create page
def dashboard_blog_add(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard_blog_list')
    else:
        form = BlogForm()
    return render(request, 'backend/blog_add.html', {'form': form})

# Blog edit page
def dashboard_blog_edit(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('dashboard_blog_list')
    else:
        form = BlogForm(instance=blog)
    return render(request, 'backend/blog_add.html', {'form': form})

# Blog delete page
def dashboard_blog_delete(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    blog.delete()
    return redirect('dashboard_blog_list')

