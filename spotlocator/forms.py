from django import forms
from django.contrib.auth import get_user_model
from spotlocator.models import MenuList

User = get_user_model()


class OwnerProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email', 'number', 'spotname', 'address', 'city', 'state', 'recovery_email',
                  'recovery_phone', 'instagram_handle', 'logo']
        widgets = {
            'email': forms.EmailInput(attrs={'class':'form-control form-control-submit'}),
            'number': forms.TextInput(attrs={'class':'form-control form-control-submit'}),
            'spotname': forms.TextInput(attrs={'class':'form-control form-control-submit'}),
            'address': forms.Textarea(attrs={'cols':2, 'rows': 2, 'class':'form-control form-control-sumbit'}),
            'city': forms.TextInput(attrs={'class': 'form-control form-control-submit'}),
            'state': forms.TextInput(attrs={'class': 'form-control form-control-submit'}),
            'recovery_email': forms.EmailInput(attrs={'class':'form-control form-control-submit'}),
            'recovery_phone': forms.TextInput(attrs={'class':'form-control form-control-submit'}),
            'instagram_handle': forms.URLInput(attrs={'class':'form-control form-control-submit'}),
            'logo': forms.ClearableFileInput(attrs={'class':'form-control form-control-submit'}),

        }

    def clean(self):
        # extra form-data validation logic will be here
        pass


class MenuCreateForm(forms.ModelForm):


    class Meta:
        model = MenuList
        fields = ['order_name', 'order_price', 'content', 'excludes', 'order_upload']
        widgets ={
            'order_name': forms.Select(attrs={'class':'form-control form-control-submit'}),
            'order_price': forms.NumberInput(attrs={'class':'form-control form-control-submit'}),
            'content': forms.Textarea(attrs={'cols':2, 'rows': 2,'class':'form-control form-control-submit',
                                             'placeholder': 'separate each item by comma'}),
            'excludes': forms.Textarea(attrs={'cols':2, 'rows': 2,'class':'form-control form-control-submit',
                                              'placeholder': 'separate each item by comma'}),
            'order_upload': forms.ClearableFileInput(attrs={'class':'form-control form-control-submit'}),
        }


    def clean(self):
        # extra form-data validation logic will be here.
        pass