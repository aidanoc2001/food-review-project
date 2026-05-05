from django import forms
from django.contrib.auth.models import User
from .models import Category, Restaurant, Review, Role, UserProfile

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ModelChoiceField(queryset=Role.objects.all())

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'location', 'description', 'category']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['restaurant', 'rating', 'comment']
