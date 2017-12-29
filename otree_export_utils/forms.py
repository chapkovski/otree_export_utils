import floppyforms as forms
from .models import TestModel

class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel
        fields = ('title', 'comment', )


class SendBonusForm(forms.Form):
    bonus_amount=forms.FloatField(min_value=0)
    reason=forms.CharField(widget=forms.Textarea)
class SendMessageForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message_text=forms.CharField(widget=forms.Textarea)