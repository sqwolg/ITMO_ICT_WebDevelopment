from django.db import models
from django.core.validators import MinValueValidator


class Room(models.Model):
    """Модель номера гостиницы"""
    ROOM_TYPES = [
        ('single', 'Одноместный'),
        ('double', 'Двухместный'),
        ('triple', 'Трехместный'),
    ]
    
    number = models.CharField(max_length=10, unique=True, verbose_name='Номер')
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, verbose_name='Тип номера')
    price_per_day = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name='Стоимость за сутки'
    )
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    floor = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Этаж')
    is_occupied = models.BooleanField(default=False, verbose_name='Занят')
    
    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'
        ordering = ['number']
    
    def __str__(self):
        return f"Номер {self.number} ({self.get_room_type_display()})"


class Guest(models.Model):
    """Модель клиента гостиницы"""
    passport_number = models.CharField(max_length=20, unique=True, verbose_name='Номер паспорта')
    surname = models.CharField(max_length=100, verbose_name='Фамилия')
    name = models.CharField(max_length=100, verbose_name='Имя')
    patronymic = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    city = models.CharField(max_length=100, verbose_name='Город')
    check_in_date = models.DateField(verbose_name='Дата поселения')
    check_out_date = models.DateField(null=True, blank=True, verbose_name='Дата выселения')
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        related_name='guests',
        verbose_name='Номер'
    )
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['surname', 'name']
    
    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic}"


class Staff(models.Model):
    """Модель служащего гостиницы"""
    surname = models.CharField(max_length=100, verbose_name='Фамилия')
    name = models.CharField(max_length=100, verbose_name='Имя')
    patronymic = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    is_active = models.BooleanField(default=True, verbose_name='Работает')
    
    class Meta:
        verbose_name = 'Служащий'
        verbose_name_plural = 'Служащие'
        ordering = ['surname', 'name']
    
    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic}"


class StaffSchedule(models.Model):
    """Модель расписания работы служащего"""
    DAYS_OF_WEEK = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]
    
    staff = models.ForeignKey(
        Staff, 
        on_delete=models.CASCADE, 
        related_name='schedules',
        verbose_name='Служащий'
    )
    floor = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Этаж')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name='День недели')
    
    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'
        unique_together = ['staff', 'floor', 'day_of_week']
        ordering = ['staff', 'day_of_week', 'floor']
    
    def __str__(self):
        return f"{self.staff} - {self.get_day_of_week_display()}, этаж {self.floor}"

