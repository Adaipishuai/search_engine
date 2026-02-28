from django.urls import path
from . import views
app_name = 'search_index'
urlpatterns = [
    path('', views.index, name='index'),
    path('simple_search/', views.simple_search, name='simple_search'),
    path('advanced_search/', views.advanced_search, name='advanced_search'),
    path('book_detail/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book_recommend/', views.book_recommend, name='book_recommend'),
]