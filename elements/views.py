import csv
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseBadRequest, \
    HttpResponseForbidden
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.text import slugify
from elements.models import List, Element
import logging

logger = logging.getLogger("elements")


# Créer une vue sur Google et un contexte qui signifie que le terme "lists" fait référence aux objets List.objects.filter par exemple
@login_required
def index(request):

    context = {}

    # récupère le nom de la liste dans l'url et affiche les éléments affiliés
    list_slug = request.GET.get('list')

    if not list_slug:
        return redirect(f"{reverse('home')}?list=bmw")


    list = get_object_or_404(List, slug=list_slug)

    # créer un contexte pour les listes et les éléments, pour récupérer les listes et les éléments liés à une liste spécifique
    context['lists'] = List.objects.order_by('slug')
    context['list'] = list
    context['elements'] = list.element_set.order_by("description")

    return render(request, 'elements/index.html', context=context)

# récupère le résultat du formulaire, et on crée un nouvel objet avec / escape pour se protéger des injections / get_or_created pour éviter un doublon
@login_required
def add_list(request):
    list_name = escape(request.POST.get('list-name'))
    list, created = List.objects.get_or_create(name=list_name, slug=slugify(list_name), user_id=request.user.id)

    if not created:

        return HttpResponse("La list existe déjà §", status=409)

    logger.info(f"{request.user} a tenté de créer une liste '{list_name}' à {timezone.now()}")

    return render(request, 'elements/list.html', context={"list" : list})

# crée un élément et lui assignons sa liste. Nous renvoyons une description pour l'afficher dans l'index
@login_required
def add_element(request):
    list = List.objects.get(slug=request.POST.get('list'))
    description = escape(request.POST.get('element-description'))
    quantity = escape(request.POST.get('element-quantity'))

    if not description or not quantity:
        return HttpResponseBadRequest("L'élément ou la quantité est vide")
    else:
        element = Element.objects.create(description=description, quantity=quantity, list=list)
        logger.info(f"{request.user} a ajouté un élément à la liste \"{list.name}\" de nom \"{element.description}\" de quantité \"{element.quantity}\" à {timezone.now()}")

    return render(request, 'elements/element.html', context={"element" : element})

# supprime un élément
@login_required
def delete_element(request, element_pk):
    element = get_object_or_404(Element, pk=element_pk)

    logger.info(f"{request.user} a supprimé l'élément \"{element.description}\" avec q= \"{element.quantity}\" à {timezone.now()}")

    element.delete()

    return HttpResponse("")

# supprime une list, les éléments associés et on redirige vers 'home'
@login_required
def delete_list(request, list_pk):
    list = get_object_or_404(List, pk=list_pk)

    logger.info(f"{request.user} a supprimé la liste \"{list.name}\" (ID={list.pk}) à {timezone.now()}")

    list.delete()

    return redirect('home')

# récupère les éléments d'une list en fonction sont list_pk
@login_required
def get_elements(request, list_pk):
    list = get_object_or_404(List, pk=list_pk)
    elements = list.element_set.order_by('description')

    logger.info(f"{request.user} a affiché les éléments de la liste \"{list.name}\" (ID={list.pk}) à {timezone.now()}")

    return render(request, 'elements/elements.html', context={'elements': elements, "list": list})

# renvoie vers la vue de modification d'élément
@login_required
def edit_element(request, element_pk):
    element = get_object_or_404(Element, id=element_pk)

    logger.info(f"{request.user} a ouvert l'édition de l'élément \"{element.description}\" (ID={element.pk}) à {timezone.now()}")

    return HttpResponse(render_to_string('elements/edit_element_inline.html', {'element': element}))

# enregistre l'élément modifié
@login_required
def save_element(request, element_pk):
    if request.method == "POST":
        element = get_object_or_404(Element, pk=element_pk)
        logger.info(f"{request.user} veut enregistré les modifications de l'élément \"{element.description}\" et q= \"{element.quantity}\"(ID={element_pk}) à {timezone.now()}")
        new_description = request.POST.get("description", "").strip()
        new_quantity = request.POST.get("quantity", "").strip()

        if new_description or new_quantity:
            element.description = new_description
            element.quantity = new_quantity
            logger.info(f"{request.user} a enregistré les modifications de l'élément \"{element.description}\" et q= \"{element.quantity}\ (ID={element_pk}) à {timezone.now()}")
            element.save()

            return render(request, "elements/element.html", {"element": element})
        return HttpResponse("Description invalide", status=400)
    return HttpResponseForbidden("Méthode invalide")

# recherche par filtrage une list
@login_required
def search_lists(request):

    query = request.POST.get('list-name', "").strip()

    logger.info(f"{request.user} a recherché une liste avec le mot-clé \"{query}\" à {timezone.now()}")

    if query:
        lists = List.objects.filter(name__icontains=query, user_id=request.user.id)
    else:
        lists = List.objects.filter(user_id=request.user.id)

    return render(request, 'elements/search_list.html', context={'lists': lists})

# recherche par filtrage un element
@login_required
def search_elements(request):

    list_slug = request.POST.get('list')
    query = request.POST.get('element-description', "").strip()

    logger.info(f"{request.user} a recherché les éléments avec le mot-clé \"{query}\" dans la liste slug \"{list_slug}\" à {timezone.now()}")

    quantity = request.POST.get('element-quantity', "")

    try:
        current_list = List.objects.get(slug=list_slug, user_id=request.user.id)
    except List.DoesNotExist:
        return HttpResponseNotFound("L'élément n'existe pas")

    elements = Element.objects.filter(list=current_list)

    if query and quantity and quantity.isdigit():
        elements = elements.filter(description__icontains=query, quantity=int(quantity))
    elif query:
        elements = elements.filter(description__icontains=query)
    elif quantity and quantity.isdigit():
        elements = elements.filter(quantity=int(quantity))

    return render(request, 'elements/search_element.html', context={'elements': elements})

# exporte tout ou une partie filtrée de la base de donnée de l'user dans un CSV
@login_required
def export_inventory_csv(request):

    # on récupère le slug ou le query s'il y a une recherche preçise
    list_slug = request.GET.get('list')

    logger.info(f"{request.user} a exporté en CSV les éléments de la liste slug \"{list_slug}\" à {timezone.now()}")

    query = request.GET.get('q', "").strip()

    # créé le type de réponse, le fichier csv et son nom, désigne le writer sur response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory.csv"'
    writer = csv.writer(response)

    #recupère uniquement les listes de l'utilisateur
    lists = List.objects.filter(user_id=request.user.id)

    #prefetch_related pour récupérer tous les elements d'une liste en une requête
    if lists:
        lists = List.objects.prefetch_related("element_set").all()
        # list toutes les lists
        if list_slug:
            lists = lists.filter(slug=list_slug)
            # sélectionne la lists rechercher
            for list in lists:
                elements = Element.objects.filter(list=list)
                writer.writerow(["List :"])
                # affiche-les elements de la ou les listes recherchées
                if query:
                    elements = elements.filter(description__icontains=query)
                    # affiche-les elements trié de la list
                if elements.exists():
                    writer.writerow([list.slug])
                    writer.writerow(["Description", "Quantity :"])
                    # écrit le nom de la list dans le csv
                    for element in elements:
                        element_description = element.description
                        element_quantity = element.quantity
                        writer.writerow([element_description, element_quantity])
                        # écrit l'élément
        elif lists:

            for list in lists:
                elements = Element.objects.filter(list=list)
                writer.writerow(["List :"])
                writer.writerow([list.slug])

                for element in elements:
                    element_description = element.description
                    element_quantity = element.quantity
                    writer.writerow(["Description", "Quantity :"])
                    writer.writerow([element_description, element_quantity])

    return response






















