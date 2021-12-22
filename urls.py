from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('input/', views.input, name='input'),
    path('article/', views.article_list, name='article_list'), 
    # path('article/search/', views.get_queryset, name='get_queryset'), 
    path('search_form/', views.search_form, name='search_form'), 
    path('search_city_form/',views.search_city_form,name='search_city_form'),
    path('search_city/',views.search_city,name='search_city'),
    path('search_city_q/',views.search_city_q,name='search_city_q'),
    path('search/', views.search, name='search'), 
    path('count/', views.count, name='count'), 
    path('count_q/', views.count_q, name='count_q'), 
    path('search_cate/', views.search_cate, name='search_cate'), 
    path('zip_upload/',views.zip_upload),
    path('zip_exact/',views.zip_exact),
    path('manage/',views.manage),
]