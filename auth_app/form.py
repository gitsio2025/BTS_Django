from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# Récupère dynamiquement le modèle utilisateur actif (CustomUser),
# tel que défini dans AUTH_USER_MODEL — compatible avec tous les projets
CustomUser = get_user_model()

# Formulaire personnalisé basé sur UserCreationForm
# Permet de créer un utilisateur CustomUser avec une gestion manuelle des mots de passe et du multi-base
class CustomUserCreationForm(UserCreationForm):

    # Champ mot de passe principal avec widget sécurisé (input type="password")
    password1 = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),) # Aide les navigateurs à ne pas auto-remplir

    # Champ de confirmation de mot de passe, identique au champ précédent
    password2 = forms.CharField(
        label='Password confirmation',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    # Meta-infos de la classe : on associe ce formulaire au modèle CustomUser
    class Meta:
        model = CustomUser
        fields = ("username",)


    # Redéfinit le constructeur pour capturer un paramètre 'using' → permet de cibler une base de données spécifique
    def __init__(self, *args, **kwargs):
        self._db = kwargs.pop('using', None)
        super().__init__(*args, **kwargs)

    # Validation personnalisée du champ username
    def clean_username(self):

        username = self.cleaned_data.get("username")

        # Vérifie si un utilisateur avec ce nom existe déjà dans la base spécifiée (_db)
        if CustomUser.objects.using(self._db).filter(username=username).exists():

            raise ValidationError("Ce nom d'utilisateur est déjà utilisé.")

        return username

    # Validation globale du formulaire : vérifie que les deux mots de passe sont identiques
    def clean(self):
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get("password1")
        pwd2 = cleaned_data.get("password2")
        if pwd1 and pwd2 and pwd1 != pwd2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    # Méthode save personnalisée : assigne le mot de passe chiffré et utilise la bonne base de données
    def save(self, commit=True):
        user = super().save(commit=False) # On crée l'objet sans encore le sauvegarder
        user.set_password(self.cleaned_data["password1"]) # On chiffre le mot de passe avec la méthode Django
        if commit:
            user.save(using=self._db) # Sauvegarde explicite dans la base _db si précisée
        return user


