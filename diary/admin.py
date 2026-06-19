from django.contrib import admin
from .models import Angler, FishingSpot, FishingTrip


@admin.register(Angler)
class AnglerAdmin(admin.ModelAdmin):
    list_display = ('user', 'region', 'favorite_fish')
    search_fields = ('user__username', 'region')


@admin.register(FishingSpot)
class FishingSpotAdmin(admin.ModelAdmin):
    list_display = ('name', 'angler', 'spot_type', 'target_fish')
    list_filter = ('spot_type',)
    search_fields = ('name',)


@admin.register(FishingTrip)
class FishingTripAdmin(admin.ModelAdmin):
    list_display = ('date', 'angler', 'spot', 'water_temp', 'pressure', 'moon_phase', 'catch_weight_kg')
    list_filter = ('moon_phase', 'date')
    search_fields = ('spot__name', 'fish_species')