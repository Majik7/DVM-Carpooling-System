from django import forms
from network.models import Node, Edge
from . import utils


class NewTripForm(forms.Form):
    start_node = forms.ModelChoiceField(queryset=Node.objects.all())
    end_node = forms.ModelChoiceField(queryset=Node.objects.all())
    max_passengers = forms.IntegerField(min_value=1)