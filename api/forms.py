from django import forms
from django.contrib.auth.models import User
from api.models import Transaction
from django.utils.translation import ugettext, ugettext_lazy as _

class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class PasswordForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

class PasswordChangeForm(PasswordForm):

    password = forms.CharField(label=_("auth"),
            widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        password1 = self.cleaned_data.get("password1")
        if password and password1 and password == password1:
            raise forms.ValidationError(
                    "Password shouldn't be the same",
                    code='password_equal')

        return password

    def save(self, commit=True):
        self.instance.set_password(self.cleaned_data["password1"])
        if commit:
            self.instance.save()
        return self.instance

class UserCreationForm(PasswordForm):

    class Meta:
        model = User
        fields = ("username", "email",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class PaymentForm(forms.ModelForm):

    class Meta:
        model = Transaction
        exclude = ('is_reviewed',)

class PageForm(forms.Form):

    page = forms.IntegerField()
    page_length = forms.IntegerField()

class 
