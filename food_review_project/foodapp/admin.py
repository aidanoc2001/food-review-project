from django.contrib import admin
from .models import Category, Restaurant, Review, Role, UserProfile

admin.site.register(Role)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Restaurant)
admin.site.register(Review)
