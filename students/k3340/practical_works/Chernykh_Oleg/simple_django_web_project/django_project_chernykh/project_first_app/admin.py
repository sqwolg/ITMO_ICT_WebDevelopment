from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Owner, Car, Ownership, DriverLicense


class OwnerInline(admin.StackedInline):
    model = Owner
    can_delete = False
    verbose_name_plural = 'Owner'


class UserAdmin(BaseUserAdmin):
    inlines = (OwnerInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'passport_number', 'address', 'nationality', 'birth_date')
    list_filter = ('nationality',)
    search_fields = ('user__first_name', 'user__last_name', 'passport_number', 'address')


admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)
