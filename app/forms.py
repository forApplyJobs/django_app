from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Frame

class AddFrameForm(forms.ModelForm):
    class Meta:
        model = Frame
        fields = ['name', 'xmlFeedPath', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter frame name'
            }),
            'xmlFeedPath': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/feed.xml'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'name': 'Frame Name',
            'xmlFeedPath': 'XML Feed URL',
            'image': 'Frame Template Image'
        }
        help_texts = {
            'name': 'Choose a descriptive name for your frame project',
            'xmlFeedPath': 'Provide a valid XML feed URL containing product information',
            'image': 'Upload a high-quality frame template image (JPG/PNG)'
        }

class EditFrameForm(forms.ModelForm):
    class Meta:
        model = Frame
        fields = ['name', 'xmlFeedPath', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter frame name'
            }),
            'xmlFeedPath': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/feed.xml'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'name': 'Frame Name',
            'xmlFeedPath': 'XML Feed URL',
            'image': 'Frame Template Image'
        }
        help_texts = {
            'name': 'Update the frame project name',
            'xmlFeedPath': 'Update the XML feed URL (this won\'t affect existing outputs)',
            'image': 'Replace frame template (will require re-setting coordinates)'
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email (optional)'
        }),
        help_text='Optional: Add your email for account recovery'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })

class DeleteConfirmationForm(forms.Form):
    confirm_delete = forms.BooleanField(
        required=True,
        widget=forms.HiddenInput(),
        initial=True
    )
    
    def __init__(self, *args, **kwargs):
        self.item_name = kwargs.pop('item_name', 'item')
        super().__init__(*args, **kwargs)
    
    def clean_confirm_delete(self):
        confirmed = self.cleaned_data.get('confirm_delete')
        if not confirmed:
            raise forms.ValidationError(f'You must confirm deletion of {self.item_name}')
        return confirmed