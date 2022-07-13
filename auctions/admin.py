from django.contrib import admin

from auctions.views import register

from . models import Auction, User, Category, Bid, Comment

# Register your models here.
admin.site.register(Auction)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(Comment)