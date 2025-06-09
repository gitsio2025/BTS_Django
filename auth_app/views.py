from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.utils import timezone

from .form import CustomUserCreationForm
from auth_app.form import CustomUserCreationForm
import logging

logger = logging.getLogger("elements")

# créé un user / vérifie les règles de sécurités / enregistre l'user sur la bdd
def inscription(request):

    form = CustomUserCreationForm(request.POST or None)

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, using='users')

        if form.is_valid():
            logger.info(f"Un nouveau compte a été créé pour {request.user} à {timezone.now()}")
            user = form.save(commit=False)
            user.save(using='users')
            return redirect('connexion')

        else: # Gestion des erreurs spécifiques

            if 'password1' in form.errors:
                for error in form.errors['password1']:
                    messages.error(request, f"Mot de passe : {error}")
            elif 'username' in form.errors:
                for error in form.errors['username']:
                    messages.error(request, "Nom d'utilisateur invalide ou déjà utilisé.")
            elif 'password2' in form.errors:
                messages.error(request, "Les mots de passe ne correspondent pas.")
            else:
                messages.error(request, "Erreur inconnue.")



    return render(request, 'inscription.html', {'form': form})

# vérifie si l'user est bien en bdd et que ses infos sont correctes
def connexion(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST': # vérifie que l'user ets bien en bdd
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if form.is_valid(): # connecte l'user (si user is true)
            logger.info(f"{request.user} c'est connecté à {timezone.now()}")
            user = form.get_user()
            login(request, user)
            return redirect('home')

        else: # Gestion des erreurs spécifiques

            if 'username' in form.errors:
                for error in form.errors['username']:
                    messages.error(request, f"Mot de passe : {error}")
            elif 'password' in form.errors:
                for error in form.errors['password']:
                    messages.error(request, "Nom d'utilisateur invalide ou déjà utilisé.")

    return render(request, 'connexion.html', {'form': form})

# déconnecte l'user avec un bouton
@login_required
def deconnexion(request):
    logger.info(f"{request.user} c'est déconnecté à {timezone.now()}")
    logout(request)
    return redirect('connexion')


