from django.conf.urls import  url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [

url(r'^$', views.index,name='index'),
url(r'^(?P<album_id>[0-9]+)/$',views.details,name='details'),
url(r'^video/$', views.videoCreate.as_view(),name='upload'),
url(r'^albumlist/$',views.AlbumList.as_view()),
url(r'^register/$',views.UserFormView.as_view()),
url(r'^videostream/$',views.index1),
url(r'^videostream1/$',views.index2),

]
urlpatterns=format_suffix_patterns(urlpatterns)