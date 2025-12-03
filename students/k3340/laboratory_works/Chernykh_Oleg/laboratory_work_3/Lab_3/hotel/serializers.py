from rest_framework import serializers
from .models import Room, Guest, Staff, StaffSchedule


class StaffScheduleSerializer(serializers.ModelSerializer):
    """Сериализатор расписания служащего"""
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = StaffSchedule
        fields = ['id', 'floor', 'day_of_week', 'day_of_week_display']


class StaffSerializer(serializers.ModelSerializer):
    """Сериализатор служащего"""
    schedules = StaffScheduleSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Staff
        fields = ['id', 'surname', 'name', 'patronymic', 'full_name', 'is_active', 'schedules']
    
    def get_full_name(self, obj):
        return f"{obj.surname} {obj.name} {obj.patronymic}".strip()


class GuestSerializer(serializers.ModelSerializer):
    """Сериализатор клиента"""
    room_number = serializers.CharField(source='room.number', read_only=True)
    room_type = serializers.CharField(source='room.room_type', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Guest
        fields = [
            'id', 'passport_number', 'surname', 'name', 'patronymic', 
            'full_name', 'city', 'check_in_date', 'check_out_date', 
            'room', 'room_number', 'room_type'
        ]
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        return f"{obj.surname} {obj.name} {obj.patronymic}".strip()


class RoomSerializer(serializers.ModelSerializer):
    """Сериализатор номера"""
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    guests = GuestSerializer(many=True, read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'number', 'room_type', 'room_type_display', 
            'price_per_day', 'phone', 'floor', 'is_occupied', 'guests'
        ]
        read_only_fields = ['id']


class StaffScheduleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания расписания"""
    
    class Meta:
        model = StaffSchedule
        fields = ['id', 'staff', 'floor', 'day_of_week']


class GuestCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания клиента"""
    
    class Meta:
        model = Guest
        fields = [
            'id', 'passport_number', 'surname', 'name', 'patronymic',
            'city', 'check_in_date', 'check_out_date', 'room'
        ]

