from django.contrib import admin
from django.contrib.admin import ModelAdmin
from Biometric.models import Employee, Log

admin.site.site_header = "Biometric checkin system"


class EmployeeAdmin(ModelAdmin):
    # The forms to add and change Employee
    table_name = 'Employee'
    list_display = ('user', 'mobile', 'gender')
    fieldsets = (
        ("Employee", {'fields': ('user', 'mobile', 'gender')}),
    )

    search_fields = ('mobile',)
    ordering = ('user',)


class LogAdmin(ModelAdmin):
    # The forms to add and change Employee
    table_name = 'Log'
    list_display = ('employee', 'date', 'nature')
    fieldsets = (
        ("Log", {'fields': ('employee', 'date', 'nature')}),
    )

    search_fields = ('employee',)
    ordering = ('date',)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Log, LogAdmin)
