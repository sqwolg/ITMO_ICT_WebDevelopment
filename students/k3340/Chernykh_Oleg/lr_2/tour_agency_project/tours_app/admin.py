from django.contrib import admin
from .models import Tour, Reservation, Review


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'agency', 'country', 'start_date', 'end_date', 'price')
    list_filter = ('country', 'agency', 'start_date')
    search_fields = ('title', 'agency', 'description', 'country')
    date_hierarchy = 'start_date'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour', 'reservation_date', 'confirmed')
    list_filter = ('confirmed', 'reservation_date')
    search_fields = ('user__username', 'tour__title')
    list_editable = ('confirmed',)
    date_hierarchy = 'reservation_date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'tour')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour', 'rating', 'tour_date', 'created_at')
    list_filter = ('rating', 'created_at', 'tour_date')
    search_fields = ('user__username', 'tour__title', 'text')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'tour')
