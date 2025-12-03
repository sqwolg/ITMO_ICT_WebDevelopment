from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import date, timedelta
from project_first_app.models import Owner, Car, Ownership, DriverLicense


class Command(BaseCommand):
    help = 'Создает тестовые данные: 6-7 владельцев, 5-6 автомобилей, удостоверения и владения'

    def handle(self, *args, **options):
        # Очистка существующих данных (опционально)
        # Owner.objects.all().delete()
        # Car.objects.all().delete()
        
        # Создание владельцев (7 владельцев)
        owners_data = [
            {
                'username': 'ivanov',
                'last_name': 'Иванов',
                'first_name': 'Иван',
                'email': 'ivanov@example.com',
                'passport_number': '1234567890',
                'address': 'Москва, ул. Ленина, д. 1',
                'nationality': 'Россия',
                'birth_date': date(1990, 5, 15),
                'license_number': '77АВ123456',
                'license_type': 'B',
                'license_issue_date': date(2010, 6, 1)
            },
            {
                'username': 'petrov',
                'last_name': 'Петров',
                'first_name': 'Петр',
                'email': 'petrov@example.com',
                'passport_number': '2345678901',
                'address': 'Санкт-Петербург, ул. Пушкина, д. 2',
                'nationality': 'Россия',
                'birth_date': date(1985, 8, 20),
                'license_number': '78ВС234567',
                'license_type': 'B',
                'license_issue_date': date(2008, 9, 15)
            },
            {
                'username': 'sidorov',
                'last_name': 'Сидоров',
                'first_name': 'Сидор',
                'email': 'sidorov@example.com',
                'passport_number': '3456789012',
                'address': 'Новосибирск, ул. Мира, д. 3',
                'nationality': 'Россия',
                'birth_date': date(1992, 3, 10),
                'license_number': '54СД345678',
                'license_type': 'B',
                'license_issue_date': date(2012, 4, 20)
            },
            {
                'username': 'kuznetsov',
                'last_name': 'Кузнецов',
                'first_name': 'Алексей',
                'email': 'kuznetsov@example.com',
                'passport_number': '4567890123',
                'address': 'Екатеринбург, ул. Советская, д. 4',
                'nationality': 'Россия',
                'birth_date': date(1988, 7, 25),
                'license_number': '66ЕЖ456789',
                'license_type': 'BC',
                'license_issue_date': date(2009, 8, 10)
            },
            {
                'username': 'smirnov',
                'last_name': 'Смирнов',
                'first_name': 'Дмитрий',
                'email': 'smirnov@example.com',
                'passport_number': '5678901234',
                'address': 'Казань, ул. Гагарина, д. 5',
                'nationality': 'Россия',
                'birth_date': date(1995, 11, 5),
                'license_number': '16ЗИ567890',
                'license_type': 'B',
                'license_issue_date': date(2015, 12, 1)
            },
            {
                'username': 'popov',
                'last_name': 'Попов',
                'first_name': 'Сергей',
                'email': 'popov@example.com',
                'passport_number': '6789012345',
                'address': 'Нижний Новгород, ул. Ломоносова, д. 6',
                'nationality': 'Россия',
                'birth_date': date(1987, 2, 14),
                'license_number': '52КЛ678901',
                'license_type': 'B',
                'license_issue_date': date(2007, 3, 5)
            },
            {
                'username': 'volkov',
                'last_name': 'Волков',
                'first_name': 'Андрей',
                'email': 'volkov@example.com',
                'passport_number': '7890123456',
                'address': 'Краснодар, ул. Красная, д. 7',
                'nationality': 'Россия',
                'birth_date': date(1993, 9, 18),
                'license_number': '23МН789012',
                'license_type': 'BC',
                'license_issue_date': date(2013, 10, 12)
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
            
            # Создание удостоверения для владельца
            license_obj, license_created = DriverLicense.objects.get_or_create(
                license_number=owner_data['license_number'],
                defaults={
                    'owner': owner,
                    'license_type': owner_data['license_type'],
                    'issue_date': owner_data['license_issue_date']
                }
            )
            if license_created:
                self.stdout.write(
                    self.style.SUCCESS(f'  Создано удостоверение: {license_obj}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  Удостоверение уже существует: {license_obj}')
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
        
        # Создание связей владения: каждому владельцу от 1 до 3 автомобилей
        # Используем внутренние методы ORM для создания ассоциативной сущности Ownership
        ownerships_mapping = [
            # Иванов - 2 автомобиля
            (0, [0, 1], [365, 200]),
            # Петров - 1 автомобиль
            (1, [1], [180]),
            # Сидоров - 3 автомобиля
            (2, [2, 3, 4], [90, 120, 150]),
            # Кузнецов - 2 автомобиля
            (3, [3, 5], [200, 100]),
            # Смирнов - 1 автомобиль
            (4, [4], [150]),
            # Попов - 2 автомобиля
            (5, [5, 0], [120, 300]),
            # Волков - 3 автомобиля
            (6, [0, 2, 4], [250, 80, 180]),
        ]
        
        ownerships_created = 0
        for owner_idx, car_indices, days_ago_list in ownerships_mapping:
            if owner_idx < len(owners):
                owner = owners[owner_idx]
                for car_idx, days_ago in zip(car_indices, days_ago_list):
                    if car_idx < len(cars):
                        car = cars[car_idx]
                        # Проверяем, не существует ли уже такая связь
                        if not Ownership.objects.filter(owner=owner, car=car).exists():
                            # Создаем ассоциативную сущность Ownership через ORM
                            ownership = Ownership.objects.create(
                                owner=owner,
                                car=car,
                                start_date=date.today() - timedelta(days=days_ago)
                            )
                            ownerships_created += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  Создано владение: {owner} -> {car} (с {ownership.start_date})'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  Владение уже существует: {owner} -> {car}'
                                )
                            )
        
        # Отображение созданных объектов
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*60}\n'
                f'РЕЗУЛЬТАТЫ СОЗДАНИЯ ТЕСТОВЫХ ДАННЫХ:\n'
                f'{"="*60}\n'
                f'Владельцев: {len(owners)}\n'
                f'Автомобилей: {len(cars)}\n'
                f'Удостоверений: {DriverLicense.objects.filter(owner__in=owners).count()}\n'
                f'Владений: {ownerships_created}\n'
                f'{"="*60}\n'
            )
        )
        
        # Детальный вывод созданных объектов
        self.stdout.write(self.style.SUCCESS('\nСозданные владельцы:'))
        for owner in owners:
            licenses = DriverLicense.objects.filter(owner=owner)
            cars_count = Ownership.objects.filter(owner=owner).count()
            self.stdout.write(
                f'  - {owner} (паспорт: {owner.passport_number}, '
                f'удостоверений: {licenses.count()}, автомобилей: {cars_count})'
            )
        
        self.stdout.write(self.style.SUCCESS('\nСозданные автомобили:'))
        for car in cars:
            owners_count = Ownership.objects.filter(car=car).count()
            self.stdout.write(
                f'  - {car} (владельцев: {owners_count})'
            )
        
        self.stdout.write(self.style.SUCCESS('\nСозданные удостоверения:'))
        for owner in owners:
            licenses = DriverLicense.objects.filter(owner=owner)
            for license_obj in licenses:
                self.stdout.write(
                    f'  - {license_obj} (тип: {license_obj.license_type}, '
                    f'выдано: {license_obj.issue_date})'
                )
        
        self.stdout.write(self.style.SUCCESS('\nСозданные владения:'))
        for owner in owners:
            ownerships = Ownership.objects.filter(owner=owner)
            for ownership in ownerships:
                self.stdout.write(
                    f'  - {ownership}'
                )