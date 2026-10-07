from django.urls import path
from . import views

urlpatterns = [
    path('', views.map1, name="home-page"),
    path('generate_map', views.maps_detail),
    path('node_details_save',views.node_details_save, name = "node_detail_save"),
    path('shortest_dist',views.shortest_dist, name="shortest_dist"),
    path('agvreq',views.agvreq, name = "agvreq"),
    path('agvstat',views.agvstat, name="agvstat"),
    path('regagv',views.regagv, name="regagv")
]