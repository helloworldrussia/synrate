from django import forms

from parsers.models import Parser, ENGINE

class ParserForm(forms.ModelForm):
    class Meta:
        model = Parser
        fields = '__all__'


class EngineForm(forms.ModelForm):
    class Meta:
        model = ENGINE
        fields = '__all__'







