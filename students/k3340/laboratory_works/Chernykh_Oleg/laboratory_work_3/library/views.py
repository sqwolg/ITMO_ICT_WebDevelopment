from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, F, Sum
from django.utils import timezone
from datetime import timedelta, datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Author, ReadingHall, Reader, Book, BookCopy, BookAssignment
from .serializers import (
    AuthorSerializer, ReadingHallSerializer, ReaderSerializer,
    BookSerializer, BookCopySerializer, BookAssignmentSerializer
)


class AuthorViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с авторами"""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class ReadingHallViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с читальными залами"""
    queryset = ReadingHall.objects.all()
    serializer_class = ReadingHallSerializer
    
    @swagger_auto_schema(
        operation_description="Получить читальный зал с читателями",
        responses={200: ReadingHallSerializer}
    )
    @action(detail=True, methods=['get'])
    def readers(self, request, pk=None):
        """Получить список читателей зала"""
        hall = self.get_object()
        readers = hall.readers.filter(is_active=True)
        serializer = ReaderSerializer(readers, many=True)
        return Response(serializer.data)


class ReaderViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с читателями"""
    queryset = Reader.objects.all()
    serializer_class = ReaderSerializer
    
    @swagger_auto_schema(
        operation_description="Получить читателя с закрепленными книгами",
        responses={200: ReaderSerializer}
    )
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        """Получить список книг, закрепленных за читателем"""
        reader = self.get_object()
        assignments = reader.book_assignments.filter(is_returned=False)
        serializer = BookAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


class BookViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с книгами"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    @swagger_auto_schema(
        operation_description="Получить книгу с экземплярами в залах",
        responses={200: BookSerializer}
    )
    @action(detail=True, methods=['get'])
    def copies(self, request, pk=None):
        """Получить список экземпляров книги в залах"""
        book = self.get_object()
        copies = book.copies.all()
        serializer = BookCopySerializer(copies, many=True)
        return Response(serializer.data)


class BookCopyViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с экземплярами книг в залах"""
    queryset = BookCopy.objects.all()
    serializer_class = BookCopySerializer


class BookAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с закреплениями книг"""
    queryset = BookAssignment.objects.all()
    serializer_class = BookAssignmentSerializer


class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet для аналитических запросов"""
    
    @swagger_auto_schema(
        operation_description="Какие книги закреплены за заданным читателем?",
        manual_parameters=[
            openapi.Parameter('reader_id', openapi.IN_QUERY, description="ID читателя", type=openapi.TYPE_INTEGER)
        ],
        responses={200: BookAssignmentSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def reader_books(self, request):
        """Какие книги закреплены за заданным читателем?"""
        reader_id = request.query_params.get('reader_id')
        if not reader_id:
            return Response({'error': 'reader_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            reader = Reader.objects.get(id=reader_id)
            assignments = reader.book_assignments.filter(is_returned=False)
            serializer = BookAssignmentSerializer(assignments, many=True)
            return Response(serializer.data)
        except Reader.DoesNotExist:
            return Response({'error': 'Reader not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="Кто из читателей взял книгу более месяца тому назад?",
        responses={200: ReaderSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def old_assignments(self, request):
        """Кто из читателей взял книгу более месяца тому назад?"""
        month_ago = timezone.now().date() - timedelta(days=30)
        assignments = BookAssignment.objects.filter(
            assignment_date__lt=month_ago,
            is_returned=False
        )
        readers = Reader.objects.filter(
            id__in=assignments.values_list('reader_id', flat=True).distinct()
        )
        serializer = ReaderSerializer(readers, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="За кем из читателей закреплены книги, количество экземпляров которых в библиотеке не превышает 2?",
        responses={200: ReaderSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def readers_with_rare_books(self, request):
        """За кем из читателей закреплены книги, количество экземпляров которых в библиотеке не превышает 2?"""
        # Находим книги с общим количеством экземпляров <= 2
        books_with_low_quantity = Book.objects.annotate(
            total_quantity=Sum('copies__quantity')
        ).filter(total_quantity__lte=2)
        
        # Находим читателей, у которых есть такие книги
        assignments = BookAssignment.objects.filter(
            book__in=books_with_low_quantity,
            is_returned=False
        )
        readers = Reader.objects.filter(
            id__in=assignments.values_list('reader_id', flat=True).distinct()
        )
        serializer = ReaderSerializer(readers, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Сколько в библиотеке читателей младше 20 лет?",
        responses={200: openapi.Response('Количество читателей', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'count': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ))}
    )
    @action(detail=False, methods=['get'])
    def young_readers_count(self, request):
        """Сколько в библиотеке читателей младше 20 лет?"""
        twenty_years_ago = timezone.now().date() - timedelta(days=365*20)
        count = Reader.objects.filter(
            birth_date__gt=twenty_years_ago,
            is_active=True
        ).count()
        return Response({'count': count})
    
    @swagger_auto_schema(
        operation_description="Сколько читателей в процентном отношении имеют начальное образование, среднее, высшее, ученую степень?",
        responses={200: openapi.Response('Процентное соотношение', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'primary': openapi.Schema(type=openapi.TYPE_NUMBER),
                'secondary': openapi.Schema(type=openapi.TYPE_NUMBER),
                'higher': openapi.Schema(type=openapi.TYPE_NUMBER),
                'degree': openapi.Schema(type=openapi.TYPE_NUMBER)
            }
        ))}
    )
    @action(detail=False, methods=['get'])
    def education_statistics(self, request):
        """Сколько читателей в процентном отношении имеют начальное образование, среднее, высшее, ученую степень?"""
        total = Reader.objects.filter(is_active=True).count()
        if total == 0:
            return Response({
                'primary': 0,
                'secondary': 0,
                'higher': 0,
                'degree': 0
            })
        
        primary = Reader.objects.filter(education='primary', is_active=True).count()
        secondary = Reader.objects.filter(education='secondary', is_active=True).count()
        higher = Reader.objects.filter(education='higher', is_active=True).count()
        degree = Reader.objects.filter(has_degree=True, is_active=True).count()
        
        return Response({
            'primary': round(primary / total * 100, 2),
            'secondary': round(secondary / total * 100, 2),
            'higher': round(higher / total * 100, 2),
            'degree': round(degree / total * 100, 2)
        })


class LibrarianOperationsViewSet(viewsets.ViewSet):
    """ViewSet для операций библиотекаря"""
    
    @swagger_auto_schema(
        operation_description="Записать в библиотеку нового читателя",
        request_body=ReaderSerializer,
        responses={201: ReaderSerializer}
    )
    @action(detail=False, methods=['post'])
    def register_reader(self, request):
        """Записать в библиотеку нового читателя"""
        serializer = ReaderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(is_active=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Исключить из списка читателей людей, записавшихся в библиотеку более года назад и не прошедших перерегистрацию",
        responses={200: openapi.Response('Результат', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'excluded_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                'excluded_readers': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER))
            }
        ))}
    )
    @action(detail=False, methods=['post'])
    def exclude_old_readers(self, request):
        """Исключить из списка читателей людей, записавшихся в библиотеку более года назад и не прошедших перерегистрацию"""
        year_ago = timezone.now().date() - timedelta(days=365)
        old_readers = Reader.objects.filter(
            registration_date__lt=year_ago,
            is_active=True
        )
        excluded_ids = list(old_readers.values_list('id', flat=True))
        old_readers.update(is_active=False)
        return Response({
            'excluded_count': len(excluded_ids),
            'excluded_readers': excluded_ids
        })
    
    @swagger_auto_schema(
        operation_description="Списать старую или потерянную книгу",
        manual_parameters=[
            openapi.Parameter('book_id', openapi.IN_QUERY, description="ID книги", type=openapi.TYPE_INTEGER),
            openapi.Parameter('reading_hall_id', openapi.IN_QUERY, description="ID зала", type=openapi.TYPE_INTEGER),
            openapi.Parameter('quantity', openapi.IN_QUERY, description="Количество для списания", type=openapi.TYPE_INTEGER)
        ],
        responses={200: openapi.Response('Результат')}
    )
    @action(detail=False, methods=['post'])
    def write_off_book(self, request):
        """Списать старую или потерянную книгу"""
        book_id = request.data.get('book_id')
        reading_hall_id = request.data.get('reading_hall_id')
        quantity = request.data.get('quantity', 1)
        
        if not book_id or not reading_hall_id:
            return Response(
                {'error': 'book_id and reading_hall_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            book_copy = BookCopy.objects.get(book_id=book_id, reading_hall_id=reading_hall_id)
            if book_copy.quantity < quantity:
                return Response(
                    {'error': 'Not enough copies to write off'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            book_copy.quantity -= quantity
            book_copy.save()
            return Response({'message': 'Book written off successfully', 'remaining_quantity': book_copy.quantity})
        except BookCopy.DoesNotExist:
            return Response({'error': 'Book copy not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="Принять книгу в фонд библиотеки",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'book_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'reading_hall_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required=['book_id', 'reading_hall_id', 'quantity']
        ),
        responses={200: BookCopySerializer}
    )
    @action(detail=False, methods=['post'])
    def accept_book(self, request):
        """Принять книгу в фонд библиотеки"""
        book_id = request.data.get('book_id')
        reading_hall_id = request.data.get('reading_hall_id')
        quantity = request.data.get('quantity', 1)
        
        if not book_id or not reading_hall_id:
            return Response(
                {'error': 'book_id and reading_hall_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            book_copy, created = BookCopy.objects.get_or_create(
                book_id=book_id,
                reading_hall_id=reading_hall_id,
                defaults={'quantity': quantity}
            )
            if not created:
                book_copy.quantity += quantity
                book_copy.save()
            serializer = BookCopySerializer(book_copy)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReportViewSet(viewsets.ViewSet):
    """ViewSet для отчетов"""
    
    @swagger_auto_schema(
        operation_description="Отчет о работе библиотеки в течение месяца",
        manual_parameters=[
            openapi.Parameter('year', openapi.IN_QUERY, description="Год", type=openapi.TYPE_INTEGER),
            openapi.Parameter('month', openapi.IN_QUERY, description="Месяц (1-12)", type=openapi.TYPE_INTEGER)
        ],
        responses={200: openapi.Response('Отчет')}
    )
    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        """Отчет о работе библиотеки в течение месяца"""
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        
        # Определяем начало и конец месяца
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()
        
        report_data = {
            'period': f"{year}-{month:02d}",
            'daily_statistics': [],
            'total_books': 0,
            'total_readers': 0,
            'new_readers_count': 0,
            'new_readers_by_hall': {}
        }
        
        # Статистика по дням
        current_date = start_date
        while current_date < end_date:
            # Количество книг на этот день (берем последнее состояние)
            # Для упрощения берем текущее состояние
            total_books = BookCopy.objects.aggregate(total=Sum('quantity'))['total'] or 0
            
            # Количество активных читателей на этот день
            total_readers = Reader.objects.filter(
                registration_date__lte=current_date,
                is_active=True
            ).count()
            
            # Количество читателей по залам
            readers_by_hall = {}
            for hall in ReadingHall.objects.all():
                count = Reader.objects.filter(
                    reading_hall=hall,
                    registration_date__lte=current_date,
                    is_active=True
                ).count()
                readers_by_hall[hall.id] = {
                    'hall_name': hall.name,
                    'readers_count': count
                }
            
            report_data['daily_statistics'].append({
                'date': current_date.isoformat(),
                'books_count': total_books,
                'readers_count': total_readers,
                'readers_by_hall': readers_by_hall
            })
            
            current_date += timedelta(days=1)
        
        # Общая статистика за месяц
        report_data['total_books'] = BookCopy.objects.aggregate(total=Sum('quantity'))['total'] or 0
        report_data['total_readers'] = Reader.objects.filter(is_active=True).count()
        
        # Новые читатели за месяц
        new_readers = Reader.objects.filter(
            registration_date__gte=start_date,
            registration_date__lt=end_date
        )
        report_data['new_readers_count'] = new_readers.count()
        
        # Новые читатели по залам
        for hall in ReadingHall.objects.all():
            count = new_readers.filter(reading_hall=hall).count()
            report_data['new_readers_by_hall'][hall.id] = {
                'hall_name': hall.name,
                'new_readers_count': count
            }
        
        return Response(report_data)

