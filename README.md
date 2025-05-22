# Упатство за решавање на втор колоквиум / испит по предметот Дизајн на интеракцијата човек-компјутер

## Сетап на проект

### Чекор 1: Се стартува проект според упатството

### Чекор 2: Се креира апликација

```
python manage.py startapp application
```

### Чекор 3: Се креира static фолдерот и се додаваат следниве линии во settings.py

```python
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Чекор 4: Се додаваат админ апликацијата и креирана апликација во INSTALLED_APPS делот:

```python
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",  # dodava se za admin
    "application"  # dodava se toa sho e od startapp
]
```

### Чекор 5: Се извршуваат миграциите и се креира superuser

```
python manage.py migrate
python manage.py createsuperuser
```

### Чекор 6: Се додаваат патеките за media и static во urls.py

```python
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  path("admin/", admin.site.urls),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                           document_root=settings.MEDIA_ROOT)
```

## Процес на креирање на апликацијата

### 1. models.py

```python
from django.contrib.auth.models import User
from django.db import models


class Property(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    area = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    image = models.ImageField(upload_to="media/")
    reserved = models.BooleanField()
    sold = models.BooleanField()


class Agent(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    linkedin = models.CharField(max_length=100)
    num_sales = models.IntegerField(default=0)
    mail = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class AgentProperties(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)


class Characteristic(models.Model):
    name = models.CharField(max_length=50)
    value = models.IntegerField()


class PropertyCharacteristics(models.Model):
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
```

```
python manage.py makemigrations
python manage.py migrate
```

### 2. admin.py

```python
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
```

### 3.1. signals.py

```python
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from application.models import Property, AgentProperties


@receiver(post_save, sender=Property)
def check_if_sold(sender, instance, **kwargs):
    if instance.sold is True:
        agents = AgentProperties.objects.filter(property=instance)
        for agent_prop in agents:
            agent_prop.agent.num_sales += 1
            agent_prop.agent.save()
```

### 3.2. apps.py

```python
from django.apps import AppConfig


class ApplicationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "application"

    def ready(self):
        from . import signals
```

### 4. forms.py

```python
from django import forms  # vazhen import

from application.models import Property


class PropertyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Property
        fields = "__all__"
```

### 5.1. views.py

```python
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from application.forms import PropertyForm
from application.models import Property, PropertyCharacteristics


def index(request):
    properties = Property.objects.annotate(total_value=Sum('propertycharacteristics__characteristic__value'))
    return render(request, "index.html", context={"properties": properties})


def details(request, pid):
    property = Property.objects.get(id=pid)
    prop_characteristics = PropertyCharacteristics.objects.filter(property=property)

    total_v = prop_characteristics.aggregate(total_value=Sum('characteristic__value')) or 0
    total = total_v['total_value'] or 0

    return render(request, "details.html", context={"property": property, "total": total})


def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect("index.html")

    form = PropertyForm()
    return render(request, "add_property.html", context={"form": form})


def edit_property(request, prop_id):
    property = get_object_or_404(Property, pk=prop_id)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
        return redirect("index.html")

    form = PropertyForm(instance=property)
    return render(request, "add_property.html", context={"form": form, "prop_id": prop_id})
```

### 5.2. регистрирање во urls.py

```python
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

import application.views

urlpatterns = [
                  path("admin/", admin.site.urls),
                  path("", application.views.index, name="index"),
                  path("details/<pid>", application.views.details, name="details"),
                  path("add_property/", application.views.add_property, name="add_property"),
                  path("edit_property/<prop_id>", application.views.edit_property, name="edit_property"),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                           document_root=settings.MEDIA_ROOT)
```

### 6. templates

#### 6.1. base.html

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Properties App</title>
    <link rel="stylesheet" href="{% static 'boostrrap/css/bootstrap.css' %}">
    <script src="{% static 'boostrrap/js/bootstrap.bundle.js' %}"></script>
  </head>
  <body>
    <div class="container-fluid">
      <nav class="navbar navbar-expand-lg bg-body-tertiary">
        <div class="container-fluid">
          <a class="navbar-brand" href="#">Navbar</a>
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                  aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="ms-auto" id="navbarNav">
            <ul class="navbar-nav">
              <li class="nav-item">
                <a class="nav-link" href="#">About</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#">Projects</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#">Blabla</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#">Contact</a>
              </li>
              <li class="nav-item">
                <a class="btn btn-danger" href="/add_property">Add new</a>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      {% block content %}

      {% endblock %}
    </div>
  </body>
</html>
```

#### 6.2. index.html

```html
{% extends 'base.html' %}
{% load static %}
{% block content %}
<div class="container-fluid p-5">
  <div class="row d-flex justify-content-center align-items-center" style="height: 500px">
    <div class="col-6 d-flex justify-content-center">
      <img src="{% static 'logo.png' %}" style="height: 300px; width: 200px">
    </div>
    <div class="col-6 text-center">
      Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem
      aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo
      enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos
      qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet,
      consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam
      quaerat voluptatem.
    </div>
  </div>
  <h1 class="text-center">View our properties</h1>
  <div class="container-fluid">
    <div class="row d-flex justify-content-between">
      {% for property in properties %}
      <div class="col-4 d-flex justify-content-center">
        <div class="card" style="width: 18rem;">
          <img src="{{ property.image.url }}" class="card-img-top" alt="...">
          <div class="card-body">
            <h2 class="card-title">{{ property.name }}</h2>
            <p class="card-text">{{ property.area }}</p>
            <hr>
            <p class="card-text">{{ property.total_value }}</p>
            <a href="/details/{{ property.pk }}" class="btn btn-danger">Details</a>
            <a href="/edit_property/{{ property.pk }}" class="btn btn-warning">Edit</a>
          </div>
        </div>
      </div>
      {% endfor %}


    </div>
  </div>
</div>
{% endblock %}
```

#### 6.3. add_property.html

```html
add
{% extends 'base.html' %}
{% load static %}
{% block content %}
<div class="container-fluid p-5">


  <div class="container-fluid">
    <div class="py-5 d-flex justify-content-center bg-secondary-subtle">
      <form method="post" action="{% url 'add_property' %}" enctype="multipart/form-data">
        {% csrf_token %}
        {{ form.as_p }}
        <button class="btn btn-primary" type="submit">Submit</button>
      </form>
    </div>
  </div>
</div>
{% endblock %}
```

#### 6.4. edit_property.html (единствена разлика помеѓу овој темплејт и add_property темплејтот e во url-то на формата каде се праќа id нa property-то)

```html
{% extends 'base.html' %}
{% load static %}
{% block content %}
<div class="container-fluid p-5">
  <div class="container-fluid">
    <div class="py-5 d-flex justify-content-center bg-secondary-subtle">
      <form method="post" action="{% url 'edit_flight' prop_id %}" enctype="multipart/form-data">
        {% csrf_token %}
        {{ form.as_p }}
        <button class="btn btn-primary" type="submit">Submit</button>
      </form>
    </div>
  </div>
</div>
{% endblock %}
```

#### 6.5. details.html

```html
{% extends 'base.html' %}
{% load static %}
{% block content %}
<div class="container-fluid p-5">

  <h1 class="text-center">View our properties</h1>
  <div class="container-fluid">
    <div class="row">
      <div class="col-6">
        <p>{{ property.name }}</p>
        <p>{{ property.area }}</p>
        <p>{{ total }}</p>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```