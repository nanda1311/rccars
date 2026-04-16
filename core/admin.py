from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser

# Register your models here.
admin.site.register(Banner)
admin.site.register(Gallery)
admin.site.register(ScrollingImages)
admin.site.register(Message)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(VideoProduct)
admin.site.register(Profile)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Order)
admin.site.register(OrderItem)
# Custom admin for Blog
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active', 'show_on_home', 'priority')
    prepopulated_fields = {"slug": ("title",)}  # Automatically fill slug from title
    search_fields = ('title',)
    list_filter = ('created_at', 'is_active', 'show_on_home')
    ordering = ('-priority', 'created_at')  # Order by priority first, then date