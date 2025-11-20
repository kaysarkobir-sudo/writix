"""
Custom template filters for attendance templates

Place this file in: student_management/templatetags/attendance_filters.py
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Template filter to get item from dictionary by key
    Usage: {{ dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def attendance_percentage(present, total):
    """
    Calculate attendance percentage
    Usage: {{ present_count|attendance_percentage:total_count }}
    """
    if total == 0:
        return 0
    return round((present / total) * 100, 1)
