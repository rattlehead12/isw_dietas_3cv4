# -*- encoding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from apps.catalogos.funciones import logger
from apps.usuarios.funciones import get_red_loggeo
from apps.usuarios.models import Usuario, PerfilUsuario, CuentaBancaria, DocumentoUsuario, RedSocialUser


# PARA validar el correo del usuario
class validar_correo_usuario():
    pass


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50,
                               required=True,
                               label='Nombre de usuario/Email',
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'required': 'true',
                               }))
    password = forms.CharField(max_length=50,
                               required=True,
                               label='Password',
                               widget=forms.TextInput(attrs={
                                   'type': 'password',
                                   'class': 'form-control',
                                   'required': 'true',
                               }))

    recordarme = forms.BooleanField(required=False,
                                    widget=forms.CheckboxInput())

    def clean(self):
        cleaned_data = self.cleaned_data
        recordarme = self.cleaned_data.get('recordarme')
        if not recordarme:
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
        else:
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False


class SignUpForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
            }),
            'email': forms.EmailInput(attrs={
                'type': 'email',
                'class': 'form-control',
                'required': 'true',
            }),
            'password': forms.TextInput(attrs={
                'type': 'password',
                'class': 'form-control psw',
                'required': 'true',
            }),
        }
        labels = {
            'username': _("Nombre de usuario"),
            'email': _("Correo Electronico"),
            'password': _("Contraseña"),
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        usuario = True
        correo = True
        if len(cleaned_data.get("username")) < 4:
            self._errors['username'] = self.error_class(["El nombre de usuario debe contener mínimo 4 caracteres"])
            usuario = False
        if len(cleaned_data.get("password")) < 6:
            self._errors['password'] = self.error_class(["La contraseña debe contener mínimo 6 caracteres"])
        if Usuario.objects.filter(username=cleaned_data.get("username").lower()):
            # print("El nombre de usuario ya esta en uso")
            self._errors['username'] = self.error_class(["El nombre de usuario ya esta en uso"])
            usuario = False
        if Usuario.objects.filter(email__iexact=cleaned_data.get("email").lower()).exists():
            # print("El email ya esta en uso...")
            tipo = get_red_loggeo(Usuario.objects.filter(email__iexact=cleaned_data.get("email").lower()))
            if tipo is not None:
                self._errors['email'] = self.error_class(["El email ya esta en uso con %s..." % tipo])
                correo = False
            else:
                self._errors['email'] = self.error_class(["El email ya esta en uso ..."])
                correo = False

        if usuario and correo:
            return cleaned_data

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['email'].required = True
        self.fields['password'].required = True


class DesactivarForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('email', 'password')
        widgets = {
            'email': forms.TextInput(attrs={
                'type': 'email',
                'placeholder': 'Correo Electronico',
                'class': 'form-control',
            }),

        }

    def clean(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if Usuario.objects.filter(email=email):
            return cleaned_data
        raise forms.ValidationError('el correo "%s" , y el pass  "%s coinciden con el usuario".' % (email, password))


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not Usuario.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError("No tenemos tu correo registrado, o tu cuenta aun no ha sido validada ")

        return email


class editarPerfilUsuarioForm(forms.ModelForm):
    nombre = forms.CharField(max_length=50,
                             required=False,
                             widget=forms.TextInput(attrs={
                                 'class': 'form-control',
                             }))
    apellidos = forms.CharField(max_length=50,
                                required=False,
                                widget=forms.TextInput(attrs={
                                    'class': 'form-control',
                                }))

    fechaNac = forms.CharField(required=False,
                               label='Fecha de nacimiento',
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'type': 'date',
                               }))

    email = forms.EmailField(max_length=60,
                             required=False,
                             widget=forms.TextInput(attrs={
                                 'class': 'form-control',
                                 'type': 'email',
                             }))

    anonimo = forms.BooleanField(required=False,
                                 widget=forms.RadioSelect(attrs={
                                     'class': 'form-control',
                                 }))

    class Meta:
        model = PerfilUsuario

        fields = ('sexo', 'imagen', 'codigoPostal', 'pais', 'telefono', 'celular',)
        widgets = {
            'codigoPostal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Codigo Postal'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0000-0000'
            }),
            'celular': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(55)-0000-0000'
            }),

            'pais': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'sexo': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super(editarPerfilUsuarioForm, self).__init__(*args, **kwargs)
        self.fields['sexo'].required = False
        self.fields['imagen'].required = False
        self.fields['codigoPostal'].label = 'Codigo Postal'
        self.fields['telefono'].required = False
        self.fields['celular'].required = False
        self.fields['pais'].required = False

    def clean(self):
        cleaned_data = self.cleaned_data
        # si el usuario manda el correo lo cambiamos si esta disponible, si es el mismo no hacemos modificadcion
        return cleaned_data


class datos_extra_perfil_usuario_form(forms.ModelForm):
    class Meta:
        model = PerfilUsuario

        fields = ('IFE', 'RFC', 'tipo_persona',)
        widgets = {
            'RFC': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'RFC'
            }),
            'tipo_persona': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super(datos_extra_perfil_usuario_form, self).__init__(*args, **kwargs)
        self.fields['IFE'].required = False
        self.fields['IFE'].label = 'Imagen escaneada de tu IFE'

        self.fields['RFC'].required = False
        self.fields['RFC'].label = 'TU RFC'
        self.fields['RFC'].pattern = '[0-9]{6,}'

        self.fields['tipo_persona'].required = False
        self.fields['tipo_persona'].label = 'Persona'

    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data


class CuentasForm(forms.ModelForm):
    class Meta:
        model = CuentaBancaria
        fields = ('titular',
                  'sucursal',
                  'clabe',
                  'banco',
                  'numero_de_cuenta',)

        widgets = {
            'titular': forms.TextInput(attrs={
                'placeholder': 'Titular de la cuenta',
                'class': 'form-control',
            }),
            'sucursal': forms.TextInput(attrs={
                'placeholder': '(4 digitos)',
                'class': 'form-control',
            }),
            'clabe': forms.TextInput(attrs={
                'placeholder': 'Clabe interbancaria',
                'class': 'form-control',
            }),
            'banco': forms.TextInput(attrs={
                'placeholder': 'Nombre de la sucursal',
                'class': 'form-control',
            }),
            'numero_de_cuenta': forms.TextInput(attrs={
                'placeholder': 'Numeró de cuenta',
                'class': 'form-control',

            }),
        }

    def __init__(self, *args, **kwargs):
        super(CuentasForm, self).__init__(*args, **kwargs)
        self.fields['titular'].label = "Titular"
        self.fields['sucursal'].label = "Numeró de sucursal"
        # self.fields['clabe'].max_length = 16

    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data


class DocumentosForm(forms.ModelForm):
    class Meta:
        model = DocumentoUsuario

        fields = ('descripcion', 'archivo')

        widgets = {
            'descripcion': forms.TextInput(attrs={
                'placeholder': 'Descripcion archivo',
                'class': 'form-control',
            }),
            'archivo': forms.FileInput(),
            # 'tipoDoc': forms.ChoiceInput(),
        }

    def __init__(self, *args, **kwargs):
        super(DocumentosForm, self).__init__(*args, **kwargs)


class RedSocialForm(forms.ModelForm):
    class Meta:
        model = RedSocialUser

        fields = ('url', 'tipo_red_social')

        widgets = {
            'url': forms.URLInput(attrs={
                'placeholder': 'URL',
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(RedSocialForm, self).__init__(*args, **kwargs)
        self.fields['tipo_red_social'].label = "Red Social"


# para optener correo de twitter y fb (cuando hace cosas random)
class terminar_registro_Form(forms.ModelForm):
    class Meta:
        model = Usuario

        fields = ('email',)
        widgets = {
            'email': forms.TextInput(attrs={
                'placeholder': 'Tu email ejemplo@ejemplo.com',
                'class': 'form-control',
                'type': 'email',
                'required': 'true',
            }),
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        email = self.cleaned_data.get('email')
        valido = True
        if (email == ''):
            self._errors['email'] = self.error_class(["Necesitamos una cuenta de correo para poder crea tu cuenta"])
            valido = False
        else:
            try:
                usuario = Usuario.objects.get(email=email)
                self._errors['email'] = self.error_class(["Ya existe un usuario con ese email, disculpa"])
                valido = False
                # print(usuario)

            except Exception as e:
                # logger.exception(e)
                pass
        if (valido):
            return cleaned_data

    def __init__(self, *args, **kwargs):
        super(terminar_registro_Form, self).__init__(*args, **kwargs)
        self.fields['email'].autofocus = True
        self.fields['email'].required = True


# para pedir nombre y apellido
class pedir_nombre_Form(forms.Form):
    nombre = forms.CharField(max_length=18,
                             widget=forms.TextInput(attrs={
                                 'placeholder': 'Nombre(s)',
                                 'class': 'form-control',
                                 'required': 'false',
                             }))

    apellidos = forms.CharField(max_length=18,
                                widget=forms.TextInput(attrs={
                                    'placeholder': 'Apellidos',
                                    'class': 'form-control',
                                    'required': 'false',
                                }))

    def clean(self):
        cleaned_data = self.cleaned_data
        nombre = self.cleaned_data.get('nombre')
        apellidos = self.cleaned_data.get('apellidos')
        valido = True
        if (nombre == ''):
            self._errors['nombre'] = self.error_class(["Es necesario que nos proporciones tus nombres"])
            valido = False
        if (apellidos == ''):
            self._errors['apellidos'] = self.error_class(["Es necesario que nos proporciones tus apellidos"])
            valido = False
        if (valido):
            return cleaned_data

    def __init__(self, *args, **kwargs):
        super(pedir_nombre_Form, self).__init__(*args, **kwargs)
        self.fields['nombre'].required = False
        self.fields['apellidos'].required = False


# para pedir imagen dell ife
class pedir_ife_Form(forms.Form):
    imagen_ife = forms.ImageField()

    def clean(self):
        cleaned_data = self.cleaned_data
        imagen_ife = self.cleaned_data.get('imagen_ife')
        # print('imagen_ife')
        if imagen_ife == '':
            self._errors['imagen_ife'] = self.error_class(
                ["Es necesario que nos proporciones una imagen de tu ife para evitar lavado de dinero"])
            # print ('no mando nada ')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(pedir_ife_Form, self).__init__(*args, **kwargs)
        self.fields['imagen_ife'].required = True
