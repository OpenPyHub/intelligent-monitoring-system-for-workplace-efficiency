from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportMixin
from .models import CustomUser
from .forms import CustomUserCreationForm

# Register your models here.

class CustomUserAdmin(ImportExportMixin, UserAdmin):
    add_form = CustomUserCreationForm
    model = CustomUser
    list_display = [
        "username",
        "affiliation",
        "email",
        "is_staff",
        ]
    fieldsets = UserAdmin.fieldsets + (('Organization info', {'fields': ('affiliation',)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Organization info', {'fields': ('affiliation',)}),)

admin.site.register(CustomUser, CustomUserAdmin)
