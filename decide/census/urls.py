from django.urls import path, include
from . import views
from .views import census

urlpatterns = [
    path("", views.CensusCreate.as_view(), name="census_create"),
    path('details<int:voting_id>', views.CensusDetail.as_view(), name='census_details'),
    path('details/',views.GetId),
    path("export_census/", views.CensusExportView.as_view(), name="export_census"),
    path("export/<int:voting_id>/", views.export_census, name="export_census_of_voting"),
    path("import_census/", views.CensusImportView.as_view(), name="import_census"),
    path("census/", views.census, name="census"),
    path('create/', views.createCensus, name='census_create'),
    path('census_list/', views.censusList, name='census_list'),
    path('census_deleted/', views.deleteCensus, name='census_deleted')
]
