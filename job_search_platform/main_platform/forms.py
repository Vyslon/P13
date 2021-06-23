from django import forms


class RegistrationForm(forms.Form):
    """
    Forms for registration, used by "registration" view
    """
    username = forms.CharField(label="Nom d'utilisateur",
                               max_length=250,
                               widget=forms.TextInput(attrs={'class':
                                                             'control',
                                                             'id':
                                                             'id_username'}),
                               required=True
                               )
    password = forms.CharField(label="Mot de passe",
                               max_length=50,
                               widget=forms.PasswordInput(attrs={'class':
                                                                 'control',
                                                                 'id':
                                                                 'id_password'}),
                               required=True
                               )
    email = forms.EmailField(label="e-mail",
                             max_length=150,
                             widget=forms.EmailInput(attrs={'class':
                                                            'control',
                                                            'id':
                                                            'id_email'}),
                             required=True
                             )


class ChangeAddressForm(forms.Form):
    """
    Forms used to change address on user_info, used by "changeAddress" view
    """
    address = forms.CharField(label="adresse",
                              max_length=200,
                              widget=forms.TextInput(attrs={'class':
                                                            'input'}),
                              required=True
                              )
