from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta


class Author(models.Model):
    """Модель автора книги"""
    name = models.CharField(max_length=200, verbose_name="Имя автора")
    
    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ReadingHall(models.Model):
    """Модель читального зала"""
    number = models.IntegerField(unique=True, verbose_name="Номер зала")
    name = models.CharField(max_length=200, verbose_name="Название зала")
    capacity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Вместимость")
    
    class Meta:
        verbose_name = "Читальный зал"
        verbose_name_plural = "Читальные залы"
        ordering = ['number']
    
    def __str__(self):
        return f"{self.number} - {self.name}"


class Reader(models.Model):
    """Модель читателя"""
    EDUCATION_CHOICES = [
        ('primary', 'Начальное'),
        ('secondary', 'Среднее'),
        ('higher', 'Высшее'),
        ('degree', 'Ученая степень'),
    ]
    
    ticket_number = models.CharField(max_length=50, unique=True, verbose_name="Номер читательского билета")
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    passport_number = models.CharField(max_length=50, verbose_name="Номер паспорта")
    birth_date = models.DateField(verbose_name="Дата рождения")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Номер телефона")
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES, verbose_name="Образование")
    has_degree = models.BooleanField(default=False, verbose_name="Наличие ученой степени")
    reading_hall = models.ForeignKey(
        ReadingHall, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='readers',
        verbose_name="Читальный зал"
    )
    registration_date = models.DateField(auto_now_add=True, verbose_name="Дата регистрации")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    class Meta:
        verbose_name = "Читатель"
        verbose_name_plural = "Читатели"
        ordering = ['ticket_number']
    
    def __str__(self):
        return f"{self.ticket_number} - {self.full_name}"


class Book(models.Model):
    """Модель книги"""
    title = models.CharField(max_length=300, verbose_name="Название")
    authors = models.ManyToManyField(Author, related_name='books', verbose_name="Авторы")
    publisher = models.CharField(max_length=200, verbose_name="Издательство")
    publication_year = models.IntegerField(verbose_name="Год издания")
    section = models.CharField(max_length=100, verbose_name="Раздел")
    code = models.CharField(max_length=100, unique=True, verbose_name="Шифр книги")
    assignment_date = models.DateField(null=True, blank=True, verbose_name="Дата закрепления за читателем")
    
    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['title']
    
    def __str__(self):
        return f"{self.code} - {self.title}"


class BookCopy(models.Model):
    """Модель экземпляра книги в зале"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies', verbose_name="Книга")
    reading_hall = models.ForeignKey(ReadingHall, on_delete=models.CASCADE, related_name='book_copies', verbose_name="Читальный зал")
    quantity = models.IntegerField(validators=[MinValueValidator(0)], default=0, verbose_name="Количество экземпляров")
    
    class Meta:
        verbose_name = "Экземпляр книги в зале"
        verbose_name_plural = "Экземпляры книг в залах"
        unique_together = ['book', 'reading_hall']
        ordering = ['book', 'reading_hall']
    
    def __str__(self):
        return f"{self.book.title} в зале {self.reading_hall.number} - {self.quantity} шт."


class BookAssignment(models.Model):
    """Модель закрепления книги за читателем"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='assignments', verbose_name="Книга")
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='book_assignments', verbose_name="Читатель")
    assignment_date = models.DateField(auto_now_add=True, verbose_name="Дата закрепления")
    is_returned = models.BooleanField(default=False, verbose_name="Возвращена")
    
    class Meta:
        verbose_name = "Закрепление книги"
        verbose_name_plural = "Закрепления книг"
        ordering = ['-assignment_date']
    
    def __str__(self):
        return f"{self.book.title} -> {self.reader.full_name}"

