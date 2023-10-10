from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

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
