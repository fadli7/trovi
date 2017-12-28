from django import forms
from api.models import Transaction, Persona, EmailConfirmation, User
from django.utils.translation import ugettext, ugettext_lazy as _
import hashlib

class PasswordMixin(forms.Form):
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

class UserCreationForm(PasswordMixin, forms.ModelForm):

    class Meta:
        model = User
        fields = ("username", "email",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False

        if commit:
            user.save()
        return user

class EmailConfirmationForm(forms.ModelForm):

    class Meta:
        model = EmailConfirmation
        fields = ('key',)

    def clean_key(self):
        key = self.cleaned_data.get('key')
        try:
            self.instance = EmailConfirmation.objects.get(key=key)
        except:
            raise forms.ValidationError(
                    'error in getting EmailConfirmation object',
                    code='get_object_failed'
                    )

        return key

    def save(self):
        user = self.instance.user
        user.is_active = True
        user.save()
        self.instance.delete()


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)

class PasswordChangeForm(PasswordMixin, forms.ModelForm):

    password = forms.CharField(label=_("auth"),
            widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = '__all__'

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

class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ('tutorial', 'payment_proof')

    def save(self, user, commit=True):
        transaction = super().save(commit=False)
        transaction.user = user
        transaction.price = self.cleaned_data['tuorial'].price

        if commit:
            transaction.save()

        return transaction

class PaginationForm(forms.Form):

    page = forms.IntegerField()
    page_length = forms.IntegerField()

    def raise_error_under_one(self, val, name):
        if val < 1:
            return forms.ValidationError(
                    "{} can't be lesser than 1".format(name),
                    code="{}_value_error".format(name)
                    )

    def clean_page(self):
        page = self.cleaned_data.get('page')
        self.raise_error_under_one(page, "page")
        return page

    def clean_page_length(self):
        page = self.cleaned_data.get('page_length')
        self.raise_error_under_one(page, "page_length")
        return page

class PersonaForm(forms.ModelForm):

    class Meta:
        model = Persona
        fields = '__all__'
