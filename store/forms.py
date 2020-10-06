import re
from django import forms
from .models import MakePayment


class MakePaymentForm(forms.ModelForm):

    class Meta:
        model = MakePayment
        fields = ['phone',]
        

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        x = re.search("^[0-9]{12,14}$", phone)

        if not x:
            raise forms.ValidationError("Phone number must in format 255xxxxxxxxx")
        return phone