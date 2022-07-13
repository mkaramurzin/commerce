from django.contrib import admin

from auctions.views import register

from . models import Auction, User, Category, Watchlist

# Register your models here.
admin.site.register(Auction)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Watchlist)