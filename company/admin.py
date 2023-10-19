from django.contrib import admin

from .models import Company, CompanyMember, InvitationToCompany


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


@admin.register(CompanyMember)
class CompanyMemberAdmin(admin.ModelAdmin):
    list_display = ('company', 'member', 'admin', 'created_at', 'updated_at')
    list_display_links = ('company', )
    list_editable = ('member', 'admin')
    search_fields = ('created_at', 'updated_at')
    list_filter = ('company', 'member', 'admin', 'created_at', 'updated_at')
    list_per_page = 50
    list_max_show_all = 200

    add_fieldsets = (
        ('Company', {'fields': ('company', )}),
        ('Info', {'fields': ('member', 'admin')}),
    )

    fieldsets = (
        ('Company', {'fields': ('company', )}),
        ('Info', {'fields': ('member', 'admin')}),
    )


@admin.register(InvitationToCompany)
class InvitationToCompanyAdmin(admin.ModelAdmin):
    list_display = ('company', 'recipient', 'status', 'created_at', 'updated_at')
    list_display_links = ('company', )
    list_editable = ('recipient', )
    search_fields = ('created_at', 'updated_at')
    list_filter = ('company', 'recipient', 'status', 'created_at', 'updated_at')
    list_per_page = 50
    list_max_show_all = 200

    add_fieldsets = (
        ('Company', {'fields': ('company', )}),
        ('Info', {'fields': ('recipient', 'status')}),
    )

    fieldsets = (
        ('Company', {'fields': ('company', )}),
        ('Info', {'fields': ('recipient', 'status')}),
    )
