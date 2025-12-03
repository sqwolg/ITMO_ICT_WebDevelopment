from django.contrib import admin
from .models import Room, Guest, Staff, StaffSchedule


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'room_type', 'floor', 'price_per_day', 'is_occupied']
    list_filter = ['room_type', 'floor', 'is_occupied']
    search_fields = ['number']


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['surname', 'name', 'patronymic', 'city', 'room', 'check_in_date', 'check_out_date']
    list_filter = ['city', 'check_in_date', 'room']
    search_fields = ['surname', 'name', 'passport_number']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['surname', 'name', 'patronymic', 'is_active']
    list_filter = ['is_active']
    search_fields = ['surname', 'name']


@admin.register(StaffSchedule)
class StaffScheduleAdmin(admin.ModelAdmin):
    list_display = ['staff', 'floor', 'day_of_week']
    list_filter = ['day_of_week', 'floor']
    search_fields = ['staff__surname', 'staff__name']

