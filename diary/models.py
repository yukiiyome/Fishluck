from django.db import models
from django.contrib.auth.models import User


class Angler(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='angler', verbose_name='Пользователь')
    region = models.CharField(max_length=100, verbose_name='Регион')
    favorite_fish = models.CharField(max_length=100, blank=True, verbose_name='Любимая рыба')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Рыболов'
        verbose_name_plural = 'Рыболовы'

    def __str__(self):
        return f"Angler {self.user.username}"


class FishingSpot(models.Model):
    SPOT_TYPES = [
        ('lake', 'Озеро'),
        ('river', 'Река'),
        ('pond', 'Пруд'),
        ('reservoir', 'Водохранилище'),
        ('sea', 'Море'),
    ]

    angler = models.ForeignKey(Angler, on_delete=models.CASCADE, related_name='spots', verbose_name='Рыболов')
    name = models.CharField(max_length=200, verbose_name='Название')
    spot_type = models.CharField(max_length=20, choices=SPOT_TYPES, verbose_name='Тип водоёма')
    target_fish = models.CharField(max_length=100, blank=True, verbose_name='Целевая рыба')
    notes = models.TextField(blank=True, verbose_name='Заметки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Водоём'
        verbose_name_plural = 'Водоёмы'

    def __str__(self):
        return self.name


class FishingTrip(models.Model):
    MOON_PHASES = [
        ('new', 'Новолуние'),
        ('waxing', 'Растущая'),
        ('full', 'Полнолуние'),
        ('waning', 'Убывающая'),
    ]

    angler = models.ForeignKey(Angler, on_delete=models.CASCADE, related_name='trips', verbose_name='Рыболов')
    spot = models.ForeignKey(FishingSpot, on_delete=models.CASCADE, related_name='trips', verbose_name='Водоём')
    date = models.DateField(verbose_name='Дата')
    water_temp = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Температура воды (°C)')
    pressure = models.PositiveIntegerField(verbose_name='Давление (мм рт. ст.)')
    moon_phase = models.CharField(max_length=20, choices=MOON_PHASES, verbose_name='Фаза луны')
    catch_weight_kg = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Вес улова (кг)')
    fish_species = models.CharField(max_length=100, blank=True, verbose_name='Виды рыбы')
    notes = models.TextField(blank=True, verbose_name='Заметки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        ordering = ['-date']
        verbose_name = 'Выезд'
        verbose_name_plural = 'Выезды'

    def __str__(self):
        return f"{self.date} - {self.spot.name}"

    @property
    def bite_score(self):
        score = 0
        temp = float(self.water_temp)
        if 15 <= temp <= 22:
            score += 4
        elif 10 <= temp < 15 or 22 < temp <= 26:
            score += 2
        elif 5 <= temp < 10 or 26 < temp <= 30:
            score += 1

        if 745 <= self.pressure <= 755:
            score += 3
        elif 740 <= self.pressure < 745 or 755 < self.pressure <= 760:
            score += 2
        elif 735 <= self.pressure < 740 or 760 < self.pressure <= 765:
            score += 1

        moon_coef = {'new': 3, 'waxing': 2, 'full': 1, 'waning': 2}
        score += moon_coef.get(self.moon_phase, 0)

        return min(score, 10)

    @property
    def score_color(self):
        s = self.bite_score
        if s >= 7:
            return 'success'
        elif s >= 4:
            return 'warning'
        else:
            return 'danger'