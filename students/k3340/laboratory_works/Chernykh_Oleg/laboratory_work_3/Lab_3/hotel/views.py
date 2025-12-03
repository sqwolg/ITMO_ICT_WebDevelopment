from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Room, Guest, Staff, StaffSchedule
from .serializers import (
    RoomSerializer, GuestSerializer, GuestCreateSerializer,
    StaffSerializer, StaffScheduleSerializer, StaffScheduleCreateSerializer
)


class RoomViewSet(viewsets.ModelViewSet):
    """ViewSet для номеров"""
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        method='get',
        operation_description='Получить список свободных номеров',
        responses={200: RoomSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def free_rooms(self, request):
        """Получить список свободных номеров"""
        free_rooms = Room.objects.filter(is_occupied=False)
        serializer = self.get_serializer(free_rooms, many=True)
        return Response({
            'count': free_rooms.count(),
            'rooms': serializer.data
        })
    
    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('room_id', openapi.IN_PATH, description='ID номера', type=openapi.TYPE_INTEGER),
            openapi.Parameter('start_date', openapi.IN_QUERY, description='Начальная дата (YYYY-MM-DD)', type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description='Конечная дата (YYYY-MM-DD)', type=openapi.TYPE_STRING),
        ],
        responses={200: GuestSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def guests_in_period(self, request, pk=None):
        """Получить клиентов, проживавших в номере в заданный период"""
        room = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Необходимо указать start_date и end_date (формат: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Клиенты, которые пересекаются с периодом
        guests = Guest.objects.filter(
            room=room
        ).filter(
            Q(check_in_date__lte=end) & 
            (Q(check_out_date__isnull=True) | Q(check_out_date__gte=start))
        )
        
        serializer = GuestSerializer(guests, many=True)
        return Response(serializer.data)


class GuestViewSet(viewsets.ModelViewSet):
    """ViewSet для клиентов"""
    queryset = Guest.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return GuestCreateSerializer
        return GuestSerializer
    
    def create(self, request, *args, **kwargs):
        """Поселить клиента (check-in)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        room = serializer.validated_data['room']
        if room.is_occupied:
            return Response(
                {'error': 'Номер уже занят'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        guest = serializer.save()
        room.is_occupied = True
        room.save()
        
        response_serializer = GuestSerializer(guest)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        method='post',
        operation_description='Выселить клиента (check-out)',
        responses={200: GuestSerializer}
    )
    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        """Выселить клиента"""
        guest = self.get_object()
        
        if guest.check_out_date:
            return Response(
                {'error': 'Клиент уже выселен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        guest.check_out_date = timezone.now().date()
        guest.save()
        
        # Освобождаем номер, если нет других активных клиентов
        room = guest.room
        active_guests = Guest.objects.filter(
            room=room,
            check_out_date__isnull=True
        ).exclude(id=guest.id)
        
        if not active_guests.exists():
            room.is_occupied = False
            room.save()
        
        serializer = GuestSerializer(guest)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('city', openapi.IN_QUERY, description='Название города', type=openapi.TYPE_STRING),
        ],
        responses={200: openapi.Response('Количество клиентов', schema=openapi.Schema(type=openapi.TYPE_OBJECT))}
    )
    @action(detail=False, methods=['get'])
    def count_by_city(self, request):
        """Получить количество клиентов из заданного города"""
        city = request.query_params.get('city')
        
        if not city:
            return Response(
                {'error': 'Необходимо указать параметр city'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        count = Guest.objects.filter(city__iexact=city).count()
        return Response({'city': city, 'count': count})
    
    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('guest_id', openapi.IN_PATH, description='ID клиента', type=openapi.TYPE_INTEGER),
            openapi.Parameter('start_date', openapi.IN_QUERY, description='Начальная дата (YYYY-MM-DD)', type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description='Конечная дата (YYYY-MM-DD)', type=openapi.TYPE_STRING),
        ],
        responses={200: GuestSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def overlapping_guests(self, request, pk=None):
        """Получить список клиентов, которые проживали в те же дни, что и заданный клиент"""
        guest = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Необходимо указать start_date и end_date (формат: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Период проживания заданного клиента
        guest_start = guest.check_in_date
        guest_end = guest.check_out_date if guest.check_out_date else timezone.now().date()
        
        # Находим пересечение периодов
        period_start = max(guest_start, start)
        period_end = min(guest_end, end) if guest_end else end
        
        if period_start > period_end:
            return Response([])
        
        # Клиенты, которые пересекаются с периодом проживания заданного клиента
        overlapping = Guest.objects.filter(
            ~Q(id=guest.id)
        ).filter(
            Q(check_in_date__lte=period_end) & 
            (Q(check_out_date__isnull=True) | Q(check_out_date__gte=period_start))
        )
        
        serializer = GuestSerializer(overlapping, many=True)
        return Response(serializer.data)


class StaffViewSet(viewsets.ModelViewSet):
    """ViewSet для служащих"""
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        method='post',
        operation_description='Принять на работу служащего',
        responses={200: StaffSerializer}
    )
    @action(detail=True, methods=['post'])
    def hire(self, request, pk=None):
        """Принять на работу служащего"""
        staff = self.get_object()
        staff.is_active = True
        staff.save()
        serializer = self.get_serializer(staff)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='post',
        operation_description='Уволить служащего',
        responses={200: StaffSerializer}
    )
    @action(detail=True, methods=['post'])
    def fire(self, request, pk=None):
        """Уволить служащего"""
        staff = self.get_object()
        staff.is_active = False
        staff.save()
        serializer = self.get_serializer(staff)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('guest_id', openapi.IN_QUERY, description='ID клиента', type=openapi.TYPE_INTEGER),
            openapi.Parameter('day_of_week', openapi.IN_QUERY, description='День недели (0-6)', type=openapi.TYPE_INTEGER),
        ],
        responses={200: StaffSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_guest_and_day(self, request):
        """Получить служащих, которые убирали номер указанного клиента в заданный день недели"""
        guest_id = request.query_params.get('guest_id')
        day_of_week = request.query_params.get('day_of_week')
        
        if not guest_id or not day_of_week:
            return Response(
                {'error': 'Необходимо указать guest_id и day_of_week (0-6)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            guest = Guest.objects.get(id=guest_id)
            day = int(day_of_week)
            if day < 0 or day > 6:
                raise ValueError
        except (Guest.DoesNotExist, ValueError):
            return Response(
                {'error': 'Неверный guest_id или day_of_week (должен быть 0-6)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Находим служащих, которые убирают этаж этого номера в указанный день
        staff_list = Staff.objects.filter(
            is_active=True,
            schedules__floor=guest.room.floor,
            schedules__day_of_week=day
        ).distinct()
        
        serializer = self.get_serializer(staff_list, many=True)
        return Response(serializer.data)


class StaffScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet для расписания служащих"""
    queryset = StaffSchedule.objects.all()
    serializer_class = StaffScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StaffScheduleCreateSerializer
        return StaffScheduleSerializer
    
    @swagger_auto_schema(
        method='post',
        operation_description='Изменить расписание служащего',
        request_body=StaffScheduleCreateSerializer(many=True),
        responses={200: StaffScheduleSerializer(many=True)}
    )
    @action(detail=False, methods=['post'], url_path='update-staff-schedule')
    def update_staff_schedule(self, request):
        """Изменить расписание служащего (удалить старое и создать новое)"""
        staff_id = request.data.get('staff_id')
        schedules_data = request.data.get('schedules', [])
        
        if not staff_id:
            return Response(
                {'error': 'Необходимо указать staff_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            staff = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            return Response(
                {'error': 'Служащий не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Удаляем старое расписание
        StaffSchedule.objects.filter(staff=staff).delete()
        
        # Создаем новое расписание
        created_schedules = []
        for schedule_data in schedules_data:
            schedule_data['staff'] = staff_id
            serializer = StaffScheduleCreateSerializer(data=schedule_data)
            if serializer.is_valid():
                schedule = serializer.save()
                created_schedules.append(schedule)
            else:
                # Откатываем изменения при ошибке
                StaffSchedule.objects.filter(staff=staff).delete()
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        response_serializer = StaffScheduleSerializer(created_schedules, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ReportViewSet(viewsets.ViewSet):
    """ViewSet для отчетов"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter('quarter', openapi.IN_QUERY, description='Квартал (1-4)', type=openapi.TYPE_INTEGER),
            openapi.Parameter('year', openapi.IN_QUERY, description='Год', type=openapi.TYPE_INTEGER),
        ],
        responses={200: openapi.Response('Квартальный отчет')}
    )
    @action(detail=False, methods=['get'], url_path='quarterly')
    def quarterly_report(self, request):
        """Получить квартальный отчет о работе гостиницы"""
        quarter = request.query_params.get('quarter')
        year = request.query_params.get('year', timezone.now().year)
        
        if not quarter:
            return Response(
                {'error': 'Необходимо указать quarter (1-4)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quarter = int(quarter)
            year = int(year)
            if quarter < 1 or quarter > 4:
                raise ValueError
        except ValueError:
            return Response(
                {'error': 'Неверный формат quarter (должен быть 1-4) или year'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Определяем даты квартала
        quarter_start_month = (quarter - 1) * 3 + 1
        start_date = datetime(year, quarter_start_month, 1).date()
        end_date = (start_date + relativedelta(months=3) - timedelta(days=1))
        
        # Клиенты за период по номерам
        guests_by_room = Guest.objects.filter(
            check_in_date__lte=end_date,
            check_out_date__gte=start_date
        ).values('room').annotate(
            client_count=Count('id')
        ).order_by('room')
        
        # Количество номеров на каждом этаже
        rooms_by_floor = Room.objects.values('floor').annotate(
            room_count=Count('id')
        ).order_by('floor')
        
        # Общая сумма дохода за каждый номер
        room_revenue = []
        for room in Room.objects.all():
            guests_in_room = Guest.objects.filter(
                room=room,
                check_in_date__lte=end_date,
                check_out_date__gte=start_date
            )
            
            total_revenue = 0
            for guest in guests_in_room:
                check_in = max(guest.check_in_date, start_date)
                check_out = min(guest.check_out_date or end_date, end_date)
                days = (check_out - check_in).days + 1
                total_revenue += float(room.price_per_day) * days
            
            room_revenue.append({
                'room_number': room.number,
                'room_id': room.id,
                'revenue': round(total_revenue, 2)
            })
        
        # Суммарный доход по всей гостинице
        total_hotel_revenue = sum(r['revenue'] for r in room_revenue)
        
        # Формируем отчет
        report = {
            'period': {
                'quarter': quarter,
                'year': year,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'clients_by_room': list(guests_by_room),
            'rooms_by_floor': list(rooms_by_floor),
            'revenue_by_room': room_revenue,
            'total_hotel_revenue': round(total_hotel_revenue, 2)
        }
        
        return Response(report)
