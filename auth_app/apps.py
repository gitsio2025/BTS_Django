from django.apps import AppConfig

#Déclare la config de l’app, définit le type d’ID par défaut, déclare le nom de l’app pour Django
class AuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'
