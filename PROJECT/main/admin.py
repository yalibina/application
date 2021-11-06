from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from django.urls import reverse
from django.utils.html import format_html

from .models import *


def linkify(field_name):
    """
    Converts a foreign key value into clickable links.

    If field_name is 'parent', link text will be str(obj.parent)
    Link will be admin url for the admin url for obj.parent.id:change
    """

    def _linkify(obj):
        linked_obj = getattr(obj, field_name)
        if linked_obj is None:
            return '-'
        app_label = linked_obj._meta.app_label
        model_name = linked_obj._meta.model_name
        view_name = f'admin:{app_label}_{model_name}_change'
        link_url = reverse(view_name, args=[linked_obj.pk])
        return format_html('<a href="{}">{}</a>', link_url, linked_obj)

    _linkify.short_description = field_name  # Sets column name
    return _linkify


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    search_fields = ('title',)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', linkify(field_name='customer'), 'complete']


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', linkify(field_name='user')]


class OrderItemAdmin(admin.ModelAdmin):
    list_display = [linkify(field_name='product'), linkify(field_name='order')]


class ItemAdmin(admin.ModelAdmin):
    list_display = ('title',)



admin.site.register(Category, CategoryAdmin)
admin.site.register(Item)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)


class CustomUserAdmin(UserAdmin):
    """Define admin model for custom User model with no username field."""
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


admin.site.register(get_user_model(), CustomUserAdmin)
