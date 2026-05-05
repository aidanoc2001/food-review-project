from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('unauthorized/', views.unauthorized_view, name='unauthorized'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('profile/', views.profile_update, name='profile_update'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/edit/<int:user_id>/', views.user_edit, name='user_edit'),
    path('users/delete/<int:user_id>/', views.user_delete, name='user_delete'),

    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/add/', views.restaurant_add, name='restaurant_add'),
    path('restaurants/edit/<int:restaurant_id>/', views.restaurant_edit, name='restaurant_edit'),
    path('restaurants/delete/<int:restaurant_id>/', views.restaurant_delete, name='restaurant_delete'),
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),

    path('reviews/', views.review_list_admin, name='review_list_admin'),
    path('reviews/history/', views.review_history, name='review_history'),
    path('reviews/add/', views.review_add, name='review_add'),
    path('reviews/edit/<int:review_id>/', views.review_edit, name='review_edit'),
    path('reviews/delete/<int:review_id>/', views.review_delete, name='review_delete'),

    path('reports/', views.reports_dashboard, name='reports_dashboard'),
]
