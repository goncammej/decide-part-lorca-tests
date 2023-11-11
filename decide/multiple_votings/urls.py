from django.urls   import path
from django.views.generic import TemplateView
from multiple_votings.views import home, signup,multiple_votings,signout,signin,list_votings

urlpatterns = [ 
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('multiple_votings/',multiple_votings, name='multiple_votings'),
    path('logout/',signout,name='logout'),
    path('signin/',signin,name='signin'),
    path('list_votings/',list_votings,name='list_votings')
]







