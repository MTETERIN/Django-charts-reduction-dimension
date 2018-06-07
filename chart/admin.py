from django.contrib import admin

# Register your models here.
from chart.models import Recomendation,Message, Feedback

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('theme', 'customer_name', 'date',)
    list_filter = ('theme', 'date',)
    search_fields = ('theme__name', 'details',)
 
    class Meta:
        model = Feedback
 
admin.site.register(Recomendation)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Message)