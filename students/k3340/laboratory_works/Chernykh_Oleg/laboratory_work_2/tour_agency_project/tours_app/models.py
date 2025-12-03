from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Tour(models.Model):
    """Тур"""
    title = models.CharField(max_length=200, verbose_name='Название тура')
    agency = models.CharField(max_length=200, verbose_name='Турагенство')
    description = models.TextField(verbose_name='Описание тура')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    payment_terms = models.TextField(verbose_name='Условия оплаты')
    country = models.CharField(max_length=100, verbose_name='Страна')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', default=0)
    
    class Meta:
        verbose_name = 'Тур'
        verbose_name_plural = 'Туры'
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} ({self.country})"


class Reservation(models.Model):
    """Резервирование тура"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, verbose_name='Тур')
    reservation_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата резервирования')
    confirmed = models.BooleanField(default=False, verbose_name='Подтверждено')
    
    class Meta:
        verbose_name = 'Резервирование'
        verbose_name_plural = 'Резервирования'
        ordering = ['-reservation_date']
    
    def __str__(self):
        status = "Подтверждено" if self.confirmed else "Ожидает подтверждения"
        return f"{self.user.username} - {self.tour.title} ({status})"


class Review(models.Model):
    """Отзыв к туру"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, verbose_name='Тур', related_name='reviews')
    tour_date = models.DateField(verbose_name='Дата тура')
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Рейтинг (1-10)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.tour.title} (Рейтинг: {self.rating})"
