from django.contrib import admin

from .models import Company


# Add the Company model for the admin interface
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'visibility', 'created_at', 'updated_at', 'description')
    list_display_links = ('name', )
    list_editable = ('visibility', )
    search_fields = ('name', 'created_at', 'updated_at')
    list_filter = ('visibility', 'owner', 'created_at', 'updated_at')
    list_per_page = 50
    list_max_show_all = 200

    # fieldsets for the 'add' form for a new Company
    add_fieldsets = (
        ('Company', {'fields': ('name', )}),
        ('Info', {'fields': ('owner', 'visibility', 'description')}),
    )

    # fieldsets for the 'change' form for an existing Company
    fieldsets = (
        ('Company', {'fields': ('name', )}),
        ('Info', {'fields': ('owner', 'visibility', 'description')}),
    )
