from django.contrib import admin
from analytics.models import APIRequestLog

@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'endpoint', 'method', 'status_code', 'timestamp', 'short_ip', 'short_user_agent')

    def short_ip(self, obj):
        return obj.ip_address or "N/A"

    def short_user_agent(self, obj):
        return (obj.user_agent[:50] + '...') if obj.user_agent and len(obj.user_agent) > 50 else obj.user_agent

    short_ip.short_description = "IP Address"
    short_user_agent.short_description = "User Agent"