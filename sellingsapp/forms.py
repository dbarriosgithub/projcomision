from django import forms
from django.forms import Textarea
from .models import Person
from .models import Solicitud,Metas,Tarifas
from django.forms import ModelChoiceField


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ('cc_id', 'first_name', 'last_name',
                  'address', 'email', 'celphone','canal_de_venta')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'celphone': forms.NumberInput(attrs={'class': 'form-control'}),
            'canal_de_venta': forms.Select(attrs={'class': 'form-control'}),
        }


class MetaForm(forms.ModelForm):

    class Meta:
        model = Metas
        fields = ('meta_ingresada', 'meta_instalada', 'mes',
                  'anio', 'canal_venta')
        widgets = {
            'meta_ingresada': forms.NumberInput(attrs={'class': 'form-control'}),
            'meta_instalada': forms.NumberInput(attrs={'class': 'form-control'}),
            'mes': forms.Select(attrs={'class': 'form-control'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Año'}),
            'canal_venta': forms.Select(attrs={'class': 'form-control'}),
        }

# --------------------------------------------------------------
#        Vista basada en clase form
# --------------------------------------------------------------
class SolicitudForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        
        super(SolicitudForm,self).__init__(*args, **kwargs)

        if hasattr(request, 'user'):
            user_name = request.user.get_username()
        else:
            user_name = None
            
        if user_name is not None:
            if user_name == "supervis@r" or user_name== "@dm1n":
                self.fields['asesor'].queryset = Person.objects.all()
            else:
                self.fields['asesor'].queryset = Person.objects.filter(
                        email=request.user.email)
        else:
            self.fields['asesor'].queryset = Person.objects.filter(
                id=request['asesor'])


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    class Meta:
        model = Solicitud
        fields = ('product_name', 'status', 'dia', 'mes',
                  'anio', 'product_cant', 'notes', 'asesor')

        widgets = {
            'product_name': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Nombre del pack o producto'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'dia': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Dia'}),
            'mes': forms.Select(attrs={'class': 'form-control'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Año'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholer': 'Notes', 'rows': 4, 'cols': 60}),
            'product_cant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad de productos'}),
            'asesor': forms.Select(attrs={'class': 'form-control'})
        }

# ------------------------------------------------------------------------
#        Vista basada en clase form para mostrar los rengos de comisiones
# ------------------------------------------------------------------------
class TarifaForm(forms.ModelForm):

    class Meta:
        model = Tarifas
        fields = ('limite_inf', 'limite_sup', 'nombre_rango',
                  'porce_title', 'canal_venta','comision')
        widgets = {
            'limite_inf': forms.NumberInput(attrs={'class': 'form-control'}),
            'limite_sup': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombre_rango': forms.Select(attrs={'class': 'form-control'}),
            'porce_title': forms.Select(attrs={'class': 'form-control'}),
            'canal_venta': forms.Select(attrs={'class': 'form-control'}),
            'comision': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Comisión'}),
        }
