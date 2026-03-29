from django.contrib import admin
from .models import Complaint, ComplaintUpdate, Rating


class ComplaintUpdateInline(admin.TabularInline):
    model = ComplaintUpdate
    extra = 1
    readonly_fields = ('timestamp',)


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'title', 'category', 'status', 'priority', 'created_at', 'is_anonymous')
    list_filter = ('status', 'category', 'priority', 'is_anonymous', 'created_at')
    search_fields = ('reference_number', 'title', 'description', 'first_name', 'last_name', 'email')
    readonly_fields = ('reference_number', 'created_at', 'updated_at')
    inlines = [ComplaintUpdateInline, RatingInline]
    fieldsets = (
        ('Reference', {'fields': ('reference_number', 'status', 'priority', 'assigned_to')}),
        ('Complainant', {'fields': ('user', 'is_anonymous', 'first_name', 'last_name', 'email', 'phone')}),
        ('Complaint Details', {'fields': ('category', 'title', 'description', 'location_address', 'ward_number', 'photo')}),
        ('Notifications', {'fields': ('notify_email', 'notify_whatsapp', 'notify_sms')}),
        ('Admin', {'fields': ('admin_notes', 'created_at', 'updated_at', 'resolved_at')}),
    )

    def save_model(self, request, obj, form, change):
        if change:
            old = Complaint.objects.get(pk=obj.pk)
            if old.status != obj.status:
                ComplaintUpdate.objects.create(
                    complaint=obj,
                    message=f'Status updated from {old.get_status_display()} to {obj.get_status_display()}.',
                    updated_by=request.user.get_full_name() or request.user.username,
                    new_status=obj.status
                )
        super().save_model(request, obj, form, change)


@admin.register(ComplaintUpdate)
class ComplaintUpdateAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'updated_by', 'new_status', 'timestamp')
    list_filter = ('new_status', 'timestamp')
    readonly_fields = ('timestamp',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'stars', 'comment', 'created_at')
    list_filter = ('stars',)
    readonly_fields = ('created_at',)
