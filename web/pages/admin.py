from django.contrib import admin
from .models import Affiliation, Workplace

# Register your models here.

class AffiliationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        ]
    fieldsets = (
        (None, {'fields': ('id', 'name',)}),)
    readonly_fields = ('id',)

class WorkplaceAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'affiliation',
        'body',
        'media',
        'coordinates',
        ]
    fieldsets = (
        (None, {'fields': ('id', 'name', 'affiliation', 'body', 'media', 'coordinates',)}),)
    readonly_fields = ('id',)

admin.site.register(Affiliation, AffiliationAdmin)
admin.site.register(Workplace, WorkplaceAdmin)
