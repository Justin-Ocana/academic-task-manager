from django.contrib import admin
from .models import TaskHistory, GroupActivity, UserActionLog, RevertibleAction


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ['task_title', 'action', 'user', 'group', 'timestamp']
    list_filter = ['action', 'timestamp', 'group']
    search_fields = ['task_title', 'user__nombre', 'user__apellido']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(GroupActivity)
class GroupActivityAdmin(admin.ModelAdmin):
    list_display = ['group', 'action', 'user', 'affected_user', 'timestamp']
    list_filter = ['action', 'timestamp', 'group']
    search_fields = ['group__name', 'user__nombre', 'description']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(UserActionLog)
class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'timestamp', 'ip_address']
    list_filter = ['action_type', 'timestamp']
    search_fields = ['user__nombre', 'user__apellido', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(RevertibleAction)
class RevertibleActionAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'status', 'group', 'performed_by', 'timestamp']
    list_filter = ['action_type', 'status', 'timestamp']
    search_fields = ['group__name', 'performed_by__nombre']
    readonly_fields = ['timestamp', 'reverted_at']
    date_hierarchy = 'timestamp'
