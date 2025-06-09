from django.db import models
from django.utils.text import slugify


# List est un objet qui sera une base des éléments.
class List(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField()
    user_id = models.IntegerField()

    # nom d'affichage de l'instance dans le tableau d'administration
    def __str__(self):
        return self.name

    # créer le slug avec le slug d'origine ou pour un nouveau slug, slug = nom
    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.name)
        super().save(*args, **kwargs)

# Si la liste est supprimée alors les éléments aussi, les éléments sont associés à une liste avec ForeignKey
class Element(models.Model):
    description = models.TextField(max_length=500)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    # nom d'affichage de l'instance dans le tableau d'administration
    def __str__(self):
        return f"{self.description} {self.quantity}"