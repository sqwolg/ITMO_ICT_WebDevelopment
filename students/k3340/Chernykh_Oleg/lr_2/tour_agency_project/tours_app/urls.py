from django.urls import path
from . import views

urlpatterns = [
    path('', views.TourListView.as_view(), name='tour_list'),
    path('tour/<int:pk>/', views.TourDetailView.as_view(), name='tour_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('tour/<int:tour_id>/reserve/', views.create_reservation, name='create_reservation'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('reservation/<int:reservation_id>/edit/', views.edit_reservation, name='edit_reservation'),
    path('reservation/<int:reservation_id>/delete/', views.delete_reservation, name='delete_reservation'),
    path('tour/<int:tour_id>/review/', views.create_review, name='create_review'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/sold-tours/', views.sold_tours_by_country, name='sold_tours_by_country'),
]

