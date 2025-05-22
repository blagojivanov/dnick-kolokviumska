from django import forms

from application.models import Property


class PropertyForm(forms.ModelForm):
    def __init__(self, *args ,**kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = Property
        fields = "__all__"