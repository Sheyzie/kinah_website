from django.contrib import admin
from .models import Vehicle, Dispatch


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_type', 'vehicle_brand', 'plate_number', 'color']
    list_filter = ['vehicle_type', 'vehicle_brand', 'plate_state']
    search_fields = ['-created_at', 'vehicle_type', 'vehicle_brand']



@admin.register(Dispatch)
class DispatchAdmin(admin.ModelAdmin):
    list_display = ['driver__email', 'company_name', 'is_active', 'total_order','status']
    list_filter = ['company_address__state', 'company_address__country', 'is_active','status']
    search_fields = ['-created_at', 'company_name', 'status']
