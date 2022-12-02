
from django.urls import path
from django.urls import include
from django.contrib.auth import views as auth
from . import views

app_name = str(views.app_name)

urlpatterns = [
   path('', views.index, name='index'),
   path('links/', views.LinkListView.as_view(), name='links'),
   path('link/<int:pk>/', views.LinkDetailView.as_view(), name='link-detail'),
   path('addlink', views.add_link, name='addlink'),
   path('importlinks', views.import_links, name='importlinks'),
   path('removelink/<int:pk>/', views.remove_link, name='removelink'),
   path('removealllinks/', views.remove_all_links, name='removealllinks'),
   path('editlink/<int:pk>/', views.edit_link, name='editlink'),

   path('export/', views.export_data, name='exportdata'),
   path('configuration/', views.configuration, name='configuration'),

   path('accounts/', include('django.contrib.auth.urls')),
   path('logout/', auth.LogoutView.as_view(template_name ='news/index.html'), name ='logout'),
]
