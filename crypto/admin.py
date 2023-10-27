from django.contrib import admin

from crypto.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass
