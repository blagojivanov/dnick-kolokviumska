import datetime

from django.contrib import admin

from application.models import Agent, Property, Characteristic, AgentProperties, PropertyCharacteristics


# Register your models here.
class AgentInline(admin.TabularInline):
    model = AgentProperties
    extra = 0


class CharacteristicInline(admin.TabularInline):
    model = PropertyCharacteristics
    extra = 0


class PropertyAdmin(admin.ModelAdmin):
    inlines = [AgentInline, CharacteristicInline]

    list_display = ['name', 'area', 'description']

    def has_add_permission(self, request):
        if not Agent.objects.all().exists():
            return True
        return Agent.objects.filter(user=request.user).exists()

    def save_model(self, request, obj, form, change):
        agent = Agent.objects.get(user=request.user)
        super(PropertyAdmin, self).save_model(request, obj, form, change)
        if change is None:
            AgentProperties.objects.craete(agent=agent, property=obj)

    def has_delete_permission(self, request, obj=None):
        return not PropertyCharacteristics.objects.filter(property=obj).exists()

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Property.objects.filter(date=datetime.date.today())
        return Property.objects.all()


class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'surname']

    def has_add_permission(self, request):
        return request.user.is_superuser


class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']

    def has_add_permission(self, request):
        return request.user.is_superuser


admin.site.register(Property, PropertyAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(Characteristic, CharacteristicAdmin)
