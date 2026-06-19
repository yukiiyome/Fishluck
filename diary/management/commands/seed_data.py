from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from diary.models import Angler, FishingSpot, FishingTrip
from datetime import date


class Command(BaseCommand):
    help = 'Создаёт тестовые данные для дашборда'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Имя пользователя, которому добавить данные')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Пользователь "{username}" не найден'))
            return

        angler, created = Angler.objects.get_or_create(
            user=user,
            defaults={'region': 'Свердловская область', 'favorite_fish': 'Щука'},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан профиль рыболова для {username}'))

        spots_data = [
            {'name': 'Озеро Шарташ', 'spot_type': 'lake', 'target_fish': 'Окунь, плотва'},
            {'name': 'Река Чусовая', 'spot_type': 'river', 'target_fish': 'Голавль, щука'},
            {'name': 'Озеро Балтым', 'spot_type': 'lake', 'target_fish': 'Карась, лещ'},
        ]
        spots = {}
        for sd in spots_data:
            spot, _ = FishingSpot.objects.get_or_create(
                angler=angler, name=sd['name'],
                defaults={'spot_type': sd['spot_type'], 'target_fish': sd['target_fish']},
            )
            spots[sd['name']] = spot
        self.stdout.write(self.style.SUCCESS(f'Водоёмов готово: {len(spots)}'))

        trips_data = [
            (date(2026, 4, 15), 'Озеро Шарташ', 12.0, 748, 'waxing', 1.8, 'Окунь'),
            (date(2026, 4, 28), 'Озеро Шарташ', 14.0, 752, 'full', 1.2, 'Плотва'),
            (date(2026, 5, 10), 'Река Чусовая', 17.0, 750, 'new', 4.5, 'Щука'),
            (date(2026, 5, 22), 'Озеро Шарташ', 19.0, 755, 'waxing', 3.2, 'Окунь, плотва'),
            (date(2026, 6, 5), 'Река Чусовая', 20.0, 745, 'new', 5.8, 'Щука, голавль'),
            (date(2026, 6, 15), 'Озеро Балтым', 22.0, 758, 'waning', 2.5, 'Карась'),
            (date(2026, 6, 18), 'Озеро Шарташ', 21.0, 750, 'waxing', 4.0, 'Окунь'),
            (date(2026, 6, 19), 'Река Чусовая', 22.0, 760, 'full', 1.5, 'Голавль'),
            (date(2026, 5, 30), 'Озеро Балтым', 18.0, 749, 'new', 3.7, 'Лещ'),
            (date(2026, 6, 10), 'Озеро Балтым', 23.0, 753, 'waxing', 2.8, 'Карась, лещ'),
        ]

        created_count = 0
        for trip_date, spot_name, temp, pressure, moon, weight, species in trips_data:
            trip, was_created = FishingTrip.objects.get_or_create(
                angler=angler, spot=spots[spot_name], date=trip_date,
                defaults={
                    'water_temp': temp, 'pressure': pressure, 'moon_phase': moon,
                    'catch_weight_kg': weight, 'fish_species': species,
                },
            )
            if was_created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Готово! Добавлено выездов: {created_count}'))