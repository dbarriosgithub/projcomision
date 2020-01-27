from django.conf.urls import url
from django.urls import path
from . import views
from .views import personIndex, personAdd, personDetail, solicitudIndex, searchSolicitud, solicitudDelete, solicitudAdd, solicitudDetail, metaAdd, metaIndex, metaDetail, metaDelete, tarifaAdd, tarifaIndex, tarifaDetail, tarifaDelete, feriadoAdd, feriadoDetail,feriadoIndex,feriadoDelete

urlpatterns = [
    path('person/', personIndex.as_view(), name='personList'),
    path('person-add/', views.personAdd, name='personAdd'),
    path('person-detail/<int:pk>/', personDetail.as_view(), name='personDetail'),
    path('person-delete/<int:id_person>/',
         views.personDelete, name='personDelete'),
    path('solicitud-search/', searchSolicitud.as_view(), name='solicitudSearch'),
    path('solicitud/', solicitudIndex.as_view(), name='solicitudList'),
    path('solicitud-add/', views.solicitudAdd, name='solicitudAdd'),
    path('solicitud-detail/<int:pk>/',
         views.solicitudDetail, name='solicitudDetail'),
    path('solicitud-delete/<int:id_solicitud>/',
         views.solicitudDelete, name='solicitudDelete'),
    path('solicitud/auto_complete_search/',
         views.autoCompleteSearchSolicitud, name='autoSearch'),
    path('proyection/', views.proyectionIndex, name='proyectionList'),
    path('meta-add/', views.metaAdd, name='metaAdd'),
    path('meta/', metaIndex.as_view(), name='metaList'),
    path('meta-detail/<int:pk>/', metaDetail.as_view(), name='metaDetail'),
    path('meta-delete/<int:id_meta>/', views.metaDelete, name='metaDelete'),
    path('tarifa-add/', views.tarifaAdd, name='tarifaAdd'),
    path('tarifa/', tarifaIndex.as_view(), name='tarifaList'),
    path('tarifa-detail/<int:pk>/', tarifaDetail.as_view(), name='tarifaDetail'),
    path('tarifa-delete/<int:id_tarifa>/',
         views.tarifaDelete, name='tarifaDelete'),
    path('feriado-add/', views.feriadoAdd, name='feriadoAdd'),
    path('feriado-detail/<int:pk>/', feriadoDetail.as_view(), name='feriadoDetail'),
    path('feriado/', feriadoIndex.as_view(), name='feriadoList'),
    path('feriado-delete/<int:id_feriado>/', views.feriadoDelete, name='feriadoDelete'),
#     url(r'^export/xls/$', views.export_solicitudes_xls, name='export_solicitudes_xls'),
    path('export-xls/', views.export_solicitudes_xls,name='exportExcel'),

]
