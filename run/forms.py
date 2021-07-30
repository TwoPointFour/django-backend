from django import forms
from .models import Questionnaire


class TestAlgorithm(forms.ModelForm):
    class Meta:
        model = Questionnaire
        fields = '__all__'
