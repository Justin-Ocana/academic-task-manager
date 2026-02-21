from django.contrib import admin
from .models import Group, GroupMember, JoinRequest, GroupActivity


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'invite_code', 'entry_type', 'max_members', 'is_invite_active', 'created_at']
    list_filter = ['entry_type', 'is_invite_active', 'created_at']
    search_fields = ['name', 'invite_code']
    readonly_fields = ['invite_code', 'created_at', 'updated_at']


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'role', 'warnings', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__nombre', 'user__apellido', 'group__name']


@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'status', 'created_at', 'reviewed_by']
    list_filter = ['status', 'created_at']
    search_fields = ['user__nombre', 'user__apellido', 'group__name']


@admin.register(GroupActivity)
class GroupActivityAdmin(admin.ModelAdmin):
    list_display = ['group', 'activity_type', 'user', 'target_user', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['group__name', 'user__nombre', 'description']
    readonly_fields = ['created_at']
