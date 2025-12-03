from django.db import models
from django.contrib.auth.models import User


class Owner(models.Model):
    """Car Owner - расширенная модель пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User')
    passport_number = models.CharField(max_length=20, verbose_name='Passport Number')
    address = models.CharField(max_length=200, verbose_name='Address')
    nationality = models.CharField(max_length=100, verbose_name='Nationality')
    birth_date = models.DateField(verbose_name='Birth Date')

    class Meta:
        verbose_name = 'Owner'
        verbose_name_plural = 'Owners'

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"
    
    @property
    def first_name(self):
        return self.user.first_name
    
    @property
    def last_name(self):
        return self.user.last_name


class Car(models.Model):
    """Car"""
    license_plate = models.CharField(max_length=20, unique=True, verbose_name='License Plate')
    brand = models.CharField(max_length=100, verbose_name='Brand')
    model = models.CharField(max_length=100, verbose_name='Model')
    color = models.CharField(max_length=50, verbose_name='Color')
    owners = models.ManyToManyField(Owner, through='Ownership', verbose_name='Owners', related_name='cars')

    class Meta:
        verbose_name = 'Car'
        verbose_name_plural = 'Cars'

    def __str__(self):
        return f"{self.brand} {self.model} ({self.license_plate})"


class Ownership(models.Model):
    """Ownership"""
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, verbose_name='Owner', related_name='ownerships')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Car', related_name='ownerships')
    start_date = models.DateField(verbose_name='Start Date')
    end_date = models.DateField(null=True, blank=True, verbose_name='End Date')

    class Meta:
        verbose_name = 'Ownership'
        verbose_name_plural = 'Ownerships'

    def __str__(self):
        return f"{self.owner} - {self.car} ({self.start_date})"


class DriverLicense(models.Model):
    """Driver License"""
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, verbose_name='Owner', related_name='licenses')
    license_number = models.CharField(max_length=20, unique=True, verbose_name='License Number')
    license_type = models.CharField(max_length=10, verbose_name='License Type')
    issue_date = models.DateField(verbose_name='Issue Date')

    class Meta:
        verbose_name = 'Driver License'
        verbose_name_plural = 'Driver Licenses'

    def __str__(self):
        return f"{self.owner} - {self.license_number}"
