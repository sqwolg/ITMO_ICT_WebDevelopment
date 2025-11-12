from django.urls import path
from . import views

urlpatterns = [
    path('owners/', views.owners_list, name='owners_list'),
    path('owner/create/', views.owner_create, name='owner_create'),
    path('owner/<int:owner_id>/', views.owner_detail, name='owner_detail'),
    path('cars/', views.CarListView.as_view(), name='cars_list'),
    path('car/create/', views.CarCreateView.as_view(), name='car_create'),
    path('car/<int:pk>/', views.CarDetailView.as_view(), name='car_detail'),
    path('car/<int:pk>/update/', views.CarUpdateView.as_view(), name='car_update'),
    path('car/<int:pk>/delete/', views.CarDeleteView.as_view(), name='car_delete'),
]

