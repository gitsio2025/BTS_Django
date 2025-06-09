
from django.contrib import admin
from django.urls import path
from elements import views as elements_views
from auth_app import views as auth_app_views


urlpatterns = [

    #path for elements
    path('menu', elements_views.index, name="home"),
    path('add-list/', elements_views.add_list, name="add-list"),
    path('search-lists/', elements_views.search_lists, name="search-lists"),
    path('search-elements/', elements_views.search_elements, name="search-elements"),
    path('add-element/', elements_views.add_element, name="add-element"),
    path('edit-element/<int:element_pk>/', elements_views.edit_element, name="edit-element"),
    path('save-element/<int:element_pk>/', elements_views.save_element, name="save-element"),
    path('delete-element/<int:element_pk>/', elements_views.delete_element, name="delete-element"),
    path('delete-list/<int:list_pk>/', elements_views.delete_list, name="delete-list"),
    path('get_elements/<int:list_pk>/', elements_views.get_elements, name= "get-elements"),
    path('admin/', admin.site.urls),
    path('export_inventory_csv', elements_views.export_inventory_csv, name= "export_inventory_csv"),


    #path for auth_app
    path('inscription', auth_app_views.inscription, name='inscription'),
    path('', auth_app_views.connexion, name='connexion'),
    path('deconnexion', auth_app_views.deconnexion, name='deconnexion'),
]
