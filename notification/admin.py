from django.contrib import admin

from .models import Notification


# Add the Notification model for the admin interface
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'text', 'status', 'created_at', 'updated_at')
    list_display_links = ('id', )
    list_editable = ('status', )
    search_fields = ('recipient', 'text', 'status', 'created_at', 'updated_at')
    list_filter = ('recipient', 'text', 'status', 'created_at', 'updated_at')
    list_per_page = 50
    list_max_show_all = 200

    # fieldsets for the 'add' form for a new Notification
    add_fieldsets = (
        ('Recipient', {'fields': ('recipient', )}),
        ('Info', {'fields': ('text', 'status')}),
    )

    # fieldsets for the 'change' form for an existing Notification
    fieldsets = (
        ('Recipient', {'fields': ('recipient', )}),
        ('Info', {'fields': ('text', 'status')}),
    )
