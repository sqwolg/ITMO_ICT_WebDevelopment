from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import date, timedelta
from project_first_app.models import Owner, Car, Ownership


class Command(BaseCommand):
    help = 'Создает тестовые данные: минимум 6 владельцев и 6 автомобилей'

    def handle(self, *args, **options):
        # Очистка существующих данных (опционально)
        # Owner.objects.all().delete()
        # Car.objects.all().delete()
        
        # Создание владельцев (6 владельцев)
        owners_data = [
            {
                'username': 'ivanov',
                'last_name': 'Иванов',
                'first_name': 'Иван',
                'email': 'ivanov@example.com',
                'passport_number': '1234567890',
                'address': 'Москва, ул. Ленина, д. 1',
                'nationality': 'Россия',
                'birth_date': date(1990, 5, 15)
            },
            {
                'username': 'petrov',
                'last_name': 'Петров',
                'first_name': 'Петр',
                'email': 'petrov@example.com',
                'passport_number': '2345678901',
                'address': 'Санкт-Петербург, ул. Пушкина, д. 2',
                'nationality': 'Россия',
                'birth_date': date(1985, 8, 20)
            },
            {
                'username': 'sidorov',
                'last_name': 'Сидоров',
                'first_name': 'Сидор',
                'email': 'sidorov@example.com',
                'passport_number': '3456789012',
                'address': 'Новосибирск, ул. Мира, д. 3',
                'nationality': 'Россия',
                'birth_date': date(1992, 3, 10)
            },
            {
                'username': 'kuznetsov',
                'last_name': 'Кузнецов',
                'first_name': 'Алексей',
                'email': 'kuznetsov@example.com',
                'passport_number': '4567890123',
                'address': 'Екатеринбург, ул. Советская, д. 4',
                'nationality': 'Россия',
                'birth_date': date(1988, 7, 25)
            },
            {
                'username': 'smirnov',
                'last_name': 'Смирнов',
                'first_name': 'Дмитрий',
                'email': 'smirnov@example.com',
                'passport_number': '5678901234',
                'address': 'Казань, ул. Гагарина, д. 5',
                'nationality': 'Россия',
                'birth_date': date(1995, 11, 5)
            },
            {
                'username': 'popov',
                'last_name': 'Попов',
                'first_name': 'Сергей',
                'email': 'popov@example.com',
                'passport_number': '6789012345',
                'address': 'Нижний Новгород, ул. Ломоносова, д. 6',
                'nationality': 'Россия',
                'birth_date': date(1987, 2, 14)
            }
        ]
        
        owners = []
        for owner_data in owners_data:
            user, user_created = User.objects.get_or_create(
                username=owner_data['username'],
                defaults={
                    'first_name': owner_data['first_name'],
                    'last_name': owner_data['last_name'],
                    'email': owner_data['email']
                }
            )
            if not user_created:
                user.first_name = owner_data['first_name']
                user.last_name = owner_data['last_name']
                user.email = owner_data['email']
                user.save()
            
            owner, created = Owner.objects.get_or_create(
                user=user,
                defaults={
                    'passport_number': owner_data['passport_number'],
                    'address': owner_data['address'],
                    'nationality': owner_data['nationality'],
                    'birth_date': owner_data['birth_date']
                }
            )
            owners.append(owner)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Создан владелец: {owner}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Владелец уже существует: {owner}')
                )
        
        # Создание автомобилей (6 автомобилей)
        cars_data = [
            {
                'license_plate': 'А123БВ777',
                'brand': 'Toyota',
                'model': 'Camry',
                'color': 'Черный'
            },
            {
                'license_plate': 'В456ГД777',
                'brand': 'BMW',
                'model': 'X5',
                'color': 'Белый'
            },
            {
                'license_plate': 'С789ЕЖ777',
                'brand': 'Mercedes-Benz',
                'model': 'C-Class',
                'color': 'Серебристый'
            },
            {
                'license_plate': 'Д012ЗИ777',
                'brand': 'Audi',
                'model': 'A4',
                'color': 'Синий'
            },
            {
                'license_plate': 'Е345КЛ777',
                'brand': 'Volkswagen',
                'model': 'Passat',
                'color': 'Красный'
            },
            {
                'license_plate': 'Ж678МН777',
                'brand': 'Ford',
                'model': 'Focus',
                'color': 'Зеленый'
            }
        ]
        
        cars = []
        for car_data in cars_data:
            car, created = Car.objects.get_or_create(
                license_plate=car_data['license_plate'],
                defaults={
                    'brand': car_data['brand'],
                    'model': car_data['model'],
                    'color': car_data['color']
                }
            )
            cars.append(car)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Создан автомобиль: {car}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Автомобиль уже существует: {car}')
                )
        
        # Создание связей владения (опционально)
        if len(owners) >= 6 and len(cars) >= 6:
            # Связываем владельцев с автомобилями
            ownerships_data = [
                (0, 0, 365),  # Иванов - Toyota
                (1, 1, 180),  # Петров - BMW
                (2, 2, 90),   # Сидоров - Mercedes
                (3, 3, 200),  # Кузнецов - Audi
                (4, 4, 150),  # Смирнов - Volkswagen
                (5, 5, 120),  # Попов - Ford
            ]
            
            for owner_idx, car_idx, days_ago in ownerships_data:
                if not Ownership.objects.filter(owner=owners[owner_idx], car=cars[car_idx]).exists():
                    Ownership.objects.create(
                        owner=owners[owner_idx],
                        car=cars[car_idx],
                        start_date=date.today() - timedelta(days=days_ago)
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nУспешно создано:\n'
                f'- Владельцев: {len(owners)}\n'
                f'- Автомобилей: {len(cars)}'
            )
        )

