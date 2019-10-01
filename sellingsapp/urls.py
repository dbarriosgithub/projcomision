from django.conf.urls import url
from django.urls import path
from . import views
from .views import personIndex, personAdd, personDetail, solicitudIndex,searchSolicitud,solicitudDelete,solicitudAdd,solicitudDetail

urlpatterns = [
    path('person/',personIndex.as_view(), name='personList'),
    path('person-add/', views.personAdd, name='personAdd'),
    path('person-detail/<int:pk>/',personDetail.as_view(), name='personDetail'),
    path('person-delete/<int:id_person>/',views.personDelete, name='personDelete'),
    path('solicitud-search/', searchSolicitud.as_view(), name='solicitudSearch'),
    path('solicitud/', solicitudIndex.as_view(), name='solicitudList'),
    path('solicitud-add/',views.solicitudAdd, name='solicitudAdd'),
    path('solicitud-detail/<int:pk>/',views.solicitudDetail, name='solicitudDetail'),
    path('solicitud-delete/<int:id_solicitud>/',views.solicitudDelete, name='solicitudDelete'),
    path('solicitud/auto_complete_search/', views.autoCompleteSearchSolicitud, name='autoSearch'),
    path('proyection/',views.proyectionIndex, name='proyectionList'),

]
