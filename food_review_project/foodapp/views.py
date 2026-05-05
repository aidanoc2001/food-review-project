from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import admin_required, login_required_simple
from .forms import LoginForm, ProfileForm, RestaurantForm, ReviewForm, UserForm
from .models import Restaurant, Review, Role, UserProfile


def ensure_profile(user):
    default_role, _ = Role.objects.get_or_create(name='user')
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': default_role}
    )
    if profile.role_id is None:
        profile.role = default_role
        profile.save()
    return profile


def is_admin_user(user):
    profile = ensure_profile(user)
    return profile.role.name == 'admin'


def home(request):
    restaurants = Restaurant.objects.all()[:6]
    return render(request, 'foodapp/home.html', {'restaurants': restaurants})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username'].strip()
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            profile = ensure_profile(user)
            request.session['role'] = profile.role.name
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'foodapp/login.html', {'form': form})


def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')


def unauthorized_view(request):
    return render(request, 'foodapp/unauthorized.html')


@login_required_simple
def dashboard(request):
    if is_admin_user(request.user):
        return render(request, 'foodapp/admin_dashboard.html')
    return render(request, 'foodapp/user_dashboard.html')


@login_required_simple
def profile_update(request):
    ensure_profile(request.user)
    form = ProfileForm(request.POST or None, instance=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated.')
        return redirect('dashboard')

    return render(request, 'foodapp/form_page.html', {'form': form, 'title': 'Update Profile'})


@admin_required
def user_list(request):
    users = User.objects.all().select_related('userprofile', 'userprofile__role')
    return render(request, 'foodapp/user_list.html', {'users': users})


@admin_required
def user_add(request):
    form = UserForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        role = form.cleaned_data['role']
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
        )
        UserProfile.objects.create(user=user, role=role)
        messages.success(request, 'User added successfully.')
        return redirect('user_list')

    return render(request, 'foodapp/form_page.html', {'form': form, 'title': 'Add User'})


@admin_required
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = ensure_profile(user)

    if request.method == 'POST':
        user.username = request.POST.get('username', '').strip()
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()

        role_id = request.POST.get('role')
        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))

        user.save()
        profile.role = get_object_or_404(Role, id=role_id)
        profile.save()

        messages.success(request, 'User updated successfully.')
        return redirect('user_list')

    roles = Role.objects.all()
    return render(request, 'foodapp/user_edit.html', {'edit_user': user, 'roles': roles})


@admin_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('user_list')

    return render(request, 'foodapp/confirm_delete.html', {'item': user, 'label': 'user'})


@login_required_simple
def restaurant_list(request):
    query = request.GET.get('q', '')
    restaurants = Restaurant.objects.all().select_related('category')

    if query:
        restaurants = restaurants.filter(name__icontains=query)

    return render(request, 'foodapp/restaurant_list.html', {'restaurants': restaurants, 'query': query})


@login_required_simple
def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant.objects.select_related('category'), id=restaurant_id)
    reviews = Review.objects.filter(restaurant=restaurant).select_related('user')

    return render(request, 'foodapp/restaurant_detail.html', {
        'restaurant': restaurant,
        'reviews': reviews,
        'average': restaurant.average_rating(),
    })


@admin_required
def restaurant_add(request):
    form = RestaurantForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Restaurant added successfully.')
        return redirect('restaurant_list')

    return render(request, 'foodapp/form_page.html', {'form': form, 'title': 'Add Restaurant'})


@admin_required
def restaurant_edit(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    form = RestaurantForm(request.POST or None, instance=restaurant)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Restaurant updated successfully.')
        return redirect('restaurant_list')

    return render(request, 'foodapp/form_page.html', {'form': form, 'title': 'Edit Restaurant'})


@admin_required
def restaurant_delete(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == 'POST':
        restaurant.delete()
        messages.success(request, 'Restaurant deleted successfully.')
        return redirect('restaurant_list')

    return render(request, 'foodapp/confirm_delete.html', {'item': restaurant, 'label': 'restaurant'})


@admin_required
def review_list_admin(request):
    reviews = Review.objects.all().select_related('user', 'restaurant')
    return render(request, 'foodapp/review_list_admin.html', {'reviews': reviews})


@login_required_simple
def review_history(request):
    reviews = Review.objects.filter(user=request.user).select_related('restaurant')
    return render(request, 'foodapp/review_history.html', {'reviews': reviews})


@login_required_simple
def review_add(request):
    ensure_profile(request.user)
    form = ReviewForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.save()
        messages.success(request, 'Review added successfully.')
        return redirect('review_history')

    return render(request, 'foodapp/form_page.html', {'form': form, 'title': 'Add Review'})


@login_required_simple
def review_edit(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    is_admin = is_admin_user(request.user)

    if not is_admin and review.user != request.user:
        return redirect('unauthorized')

    form = ReviewForm(request.POST or None, instance=review)

    if request.method == 'POST' and form.is_valid():
        updated_review = form.save(commit=False)
        updated_review.user = review.user
        updated_review.save()
        messages.success(request, 'Review updated successfully.')

        if is_admin:
            return redirect('review_list_admin')
        return redirect('review_history')

    return render(request, 'foodapp/form_page.html', {'form': form, 'title': 'Edit Review'})


@login_required_simple
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    is_admin = is_admin_user(request.user)

    if not is_admin and review.user != request.user:
        return redirect('unauthorized')

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted successfully.')

        if is_admin:
            return redirect('review_list_admin')
        return redirect('review_history')

    return render(request, 'foodapp/confirm_delete.html', {'item': review, 'label': 'review'})


@admin_required
def reports_dashboard(request):
    top_restaurants = Restaurant.objects.annotate(
        avg_rating=Avg('review__rating')
    ).order_by('-avg_rating')[:5]

    top_users = User.objects.annotate(
        review_total=Count('review')
    ).order_by('-review_total')[:5]

    ratings_by_category = Restaurant.objects.values(
        'category__name'
    ).annotate(
        avg_rating=Avg('review__rating')
    ).order_by('category__name')

    return render(request, 'foodapp/reports.html', {
        'top_restaurants': top_restaurants,
        'top_users': top_users,
        'ratings_by_category': ratings_by_category,
    })