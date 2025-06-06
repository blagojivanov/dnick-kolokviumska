from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from application.forms import PropertyForm
from application.models import Property, PropertyCharacteristics, Characteristic


# Create your views here.

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
            property = form.save()
            characteristics = request.POST.get('characteristics')

            characteristics_list = characteristics.split(",")
            for charac in characteristics_list:
                char = Characteristic.objects.filter(name=charac).get()
                PropertyCharacteristics.objects.create(property=property, characteristic=char)
        return redirect("index")

    form = PropertyForm()
    return render(request, "add_property.html", context={"form": form})


def edit_property(request, prop_id):
    prop = get_object_or_404(Property, pk=prop_id)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=prop)
        if form.is_valid():
            form.save()
            characteristics = request.POST.get('characteristics')

            characteristics_list = characteristics.split(",")
            for charac in characteristics_list:
                char = Characteristic.objects.filter(name=charac).get()
                PropertyCharacteristics.objects.create(property=prop, characteristic=char)
        return redirect("index")

    form = PropertyForm(instance=prop)
    characteristics = PropertyCharacteristics.objects.filter(property=prop)
    char_str = ""
    for char in characteristics:
        char_str+=char.characteristic.name+","

    return render(request, "edit_property.html", context={"form": form, "prop_id": prop_id, "char_str":char_str})
