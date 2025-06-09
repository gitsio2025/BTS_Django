
# Définition d'un routeur de base de données pour Django
# Ce routeur redirige toutes les opérations de l'app 'auth_app' vers la base 'users'
class AppDatabaseRouter:

    # Détermine la base à utiliser pour les requêtes en lecture (SELECT)
    def db_for_read(self, model, **hints):

        # Si le modèle appartient à l'app 'auth_app', utiliser la base 'users'
        if model._meta.app_label == 'auth_app':
            return 'users'

        # Sinon, Django choisira la base par défaut
        return None

    # Détermine la base à utiliser pour les requêtes en écriture (INSERT, UPDATE, DELETE)
    def db_for_write(self, model, **hints):

        # Même logique que pour la lecture : 'auth_app' → base 'users'
        if model._meta.app_label == 'auth_app':
            return 'users'
        return None

    # Contrôle la migration des modèles : vers quelle base appliquer makemigrations/migrate
    def allow_migrate(self, db, app_label, model_name=None, **hints):

        # Pour 'auth_app', on autorise les migrations uniquement dans la base 'users'
        if app_label == 'auth_app':
            return db == 'users'

        # Pour les autres apps, Django décide tout seul (None = comportement par défaut)
        return None