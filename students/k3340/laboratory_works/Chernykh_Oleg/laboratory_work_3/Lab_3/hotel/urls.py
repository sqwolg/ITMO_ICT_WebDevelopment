from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoomViewSet, GuestViewSet, StaffViewSet,
    StaffScheduleViewSet, ReportViewSet
)

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'guests', GuestViewSet, basename='guest')
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'staff-schedules', StaffScheduleViewSet, basename='staff-schedule')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]

