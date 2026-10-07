from django import forms
from .models import Maps

class noOfNodes(forms.Form):
    nodes = forms.IntegerField()
    stations = forms.IntegerField()

class MapsForm(forms.ModelForm):
    class Meta:
        model = Maps
        fields = ('nodes', 'stations')

