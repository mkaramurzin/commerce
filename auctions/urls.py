from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("auction/<str:auction>", views.auction, name="auction"),
    path("category", views.category_search, name="category_search"),
    path("category/<str:name>", views.category, name="category")
]
