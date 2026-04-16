from django.contrib import admin
from django.urls import path,include
from . import views
from django.shortcuts import render
from .models import Product
from django.conf import settings
from django.conf.urls.static import static


from .views import customer_list, customer_detail



urlpatterns = [
     # signin and signup for frontent
     path('account/signin/', views.admin_login, name='login'),
     path('check-delivery/', views.check_delivery, name='check_delivery'),

    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart-ajax/', views.add_to_cart_ajax, name='add_to_cart_ajax'), # <--- ADD THIS
    path('cart/update/<int:cart_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/delete/<int:cart_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),

    path('checkout/', views.checkout_from_cart, name='checkout'),


    path('profile/', views.profile_page, name='profile'),
    path('profile/address/', views.address_profile, name='address_profile'),
    path('profile/orders/', views.orders_page, name='orders_page'),
    path('profile/update-profile/', views.update_profile, name='update_profile'),
    path('profile/logout/', views.logout_page, name='logout_page'),


    path('blogs/', views.blog_list, name='blog_list'),  # Blog listing page
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),  # Single blog

    path('profile/address/', views.address_profile, name='address_profile'),
    path('addresses/create/', views.create_address, name='create_address'),
    path('addresses/create/', views.create_address, name='create_address'),
    path('addresses/get/<int:pk>/', views.get_address, name='get_address'),
    path('addresses/update/<int:pk>/', views.update_address, name='update_address'),
    path('addresses/delete/<int:pk>/', views.delete_address, name='delete_address'),
    path('addresses/set-default/<int:pk>/', views.set_default_address, name='set_default_address'),

     path('signup/', views.signup_view, name='signup'),
     path('login/', views.login_view, name='login'),


     path('wishlist/', views.wishlist_page, name='wishlist'),
     path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),


     path('', views.home, name="home"),
     path('contactus/', views.contactus, name='contactus'),
     path('shop/', views.shop, name='shop'),
     path('product/<slug:slug>/', views.product_detail, name='product_detail'),
     path('product/category/<slug:slug>/', views.cateogry_products, name='cateogry_products'),
     path('gallery/', views.rc_gallery, name='rc_gallery'),

     path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
     path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
     path('return-policy/', views.return_policy, name='return_policy'),
     path('booking-policy/', views.booking_policy, name='booking_policy'),
     path('faq/', views.faq, name='faq'),

     #login is for dashboard
     path('account/logout/', views.logout_user, name="logout"),
      

     # backend
     path('account/', views.dashboard, name="dashboard"),



     # category
     path('account/categories/', views.categories, name="categories"),
     path('category/<slug:slug>/edit/', views.categories, name='edit_category'),
     path('category/<slug:slug>/delete/', views.categories, name='delete_category'),


     # product
     path('account/products/', views.products, name='products'),
     path('account/create/product/', views.create_product, name='create_product'),
     path('account/update/product/<slug:slug>/', views.edit_product, name='edit_product'),
     path('account/delete/product/<slug:slug>/', views.delete_product, name='delete_product'),



     path('account/blogs/', views.dashboard_blog_list, name='dashboard_blog_list'),
     path('account/create/blog/', views.dashboard_blog_add, name='dashboard_blog_add'),
     path('account/update/blog/<slug:slug>/', views.dashboard_blog_edit, name='dashboard_blog_edit'),
     path('account/delete/blog/<slug:slug>/', views.dashboard_blog_delete, name='dashboard_blog_delete'),

     #BANNERS
     path('account/add-banner/', views.add_banner, name="add_banner"),
     path('account/banners/update/<str:pk>/', views.update_banner, name='update_banner'),
     path('account/banners/delete/<str:pk>/', views.delete_banner, name='delete_banner'),
     path('account/banners/', views.banners, name="banners"),

     path('account/orders/', views.orders, name="orders"),
     path('account/orders-list/', views.orders_list, name="orders_list"),
     path('account/order-detail/<int:order_id>/', views.order_detail, name='order_detail'),

     path('account/customers/', customer_list, name='customer_list'),
     path('account/customers/<int:user_id>/', customer_detail, name='customer_detail'),


     path('account/order/collect-cash/<int:order_id>/', views.collect_cash, name='collect_cash'),



     path('account/payments/', views.payments, name="payments"),
     path('account/payment-list/', views.payment_list, name="payment_list"),
     path('account/payment-detail/<int:payment_id>/', views.payment_detail, name='payment_detail'),

     path('account/video-products/', views.video_products_list, name="video_products_list"),
     path('account/video-products/create/', views.create_video_product, name="create_video_product"),
     path('account/video-products/edit/<int:pk>/', views.edit_video_product, name="edit_video_product"),
     path('account/video-products/delete/<int:pk>/', views.delete_video_product, name="delete_video_product"),

     # gallery
     path('account/gallery/', views.gallery, name="gallery"),
     path('account/add-gallery/', views.add_gallery, name="add_gallery"),
     path('account/gallery/delete/<str:pk>/', views.delete_gallery, name='delete_gallery'),

     # scrolling images
     path('account/scrolling-images/', views.scrolling_images, name="scrolling_images"),
     path('account/add-scrolling/', views.add_scrolling_images, name="add_scrolling_images"),
     path('account/scrolling-images/delete/<str:pk>/', views.delete_scrolling_images, name='delete_scrolling_images'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)