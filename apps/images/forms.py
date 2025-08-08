from django import forms


from django.contrib.auth import get_user_model

# CONSTANTS
User = get_user_model()


class ImageForm(forms.Form):
    prompt = forms.CharField(max_length=100, help_text="Example: 'A photo of a cat sitting on a couch'")
    num_results = forms.IntegerField(min_value=1, max_value=4, help_text="Number of results")
    sync = forms.BooleanField(required=False, help_text="Sync with Bria")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prompt'].widget.attrs.update({'class': 'form-control'})
        self.fields['num_results'].widget.attrs.update({'class': 'form-control', 'max': 4})
        self.fields['sync'].widget.attrs.update({'class': 'form-check-input'})

    