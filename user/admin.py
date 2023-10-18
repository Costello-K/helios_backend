from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from user.models import RequestToCompany

User = get_user_model()


# add the CustomUser model for the admin interface
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'date_joined', 'is_active', 'is_staff',
                    'is_superuser']
    list_display_links = ['username']
    list_editable = ['is_active', 'first_name', 'last_name']
    search_fields = ('username', 'email', 'is_superuser')

    # fieldsets for the 'add' form for a new user
    add_fieldsets = (
        ('User', {'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')})
    )

    # fieldsets for the 'add' form for a new user
    fieldsets = (
        ('User', {'fields': ('username', 'first_name', 'last_name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )


@admin.register(RequestToCompany)
class RequestToCompanyAdmin(admin.ModelAdmin):
    list_display = ('company', 'sender', 'status', 'created_at', 'updated_at')
    list_display_links = ('company', )
    list_editable = ('sender', )
    search_fields = ('created_at', 'updated_at')
    list_filter = ('company', 'sender', 'status', 'created_at', 'updated_at')
    list_per_page = 50
    list_max_show_all = 200

    add_fieldsets = (
        ('Company', {'fields': ('company', )}),
        ('Info', {'fields': ('sender', 'status')}),
    )

    fieldsets = (
        ('Company', {'fields': ('company', )}),
        ('Info', {'fields': ('sender', 'status')}),
    )
