from operator import inv
import re
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import Bid, Category, Comment, User, Watchlist, Auction

class AuctionForm(forms.ModelForm):
    
    class Meta:
        model = Auction
        fields = ('title', 'description', 'image', 'price', 'start_date', 'end_date', 'category')

def index(request):
    list = Auction.objects.all().order_by('start_date').reverse()
    auctions = []

    for item in list:
        if(item.start_date < timezone.now() and item.active and item.end_date > timezone.now()):
            auctions.append(item)

    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "time": timezone.now()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            Watchlist.objects.create(user=user)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create(request):
    
    # verify user is logged in
    if request.user.id is None:
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'GET':
        return render(request, "auctions/create.html", {
            "form": AuctionForm(),
            "time": timezone.now
        })
    else:
        form = AuctionForm(request.POST)
        
        if form.is_valid():
            new_Auction = Auction.objects.create(
                user = request.user,
                title = form.cleaned_data['title'],
                description = form.cleaned_data['description'],
                image = form.cleaned_data['image'],
                price = form.cleaned_data['price'],
                start_date = form.cleaned_data['start_date'],
                end_date = form.cleaned_data['end_date'],
                category = form.cleaned_data['category'],
            )
        if new_Auction.end_date < timezone.now():
            invalid = Auction.objects.get(title=new_Auction.title)
            invalid.delete()
            return render(request, "auctions/error.html", {
                "message": "Auction expiration date must be in the future"
            })
        if new_Auction.start_date < timezone.now():
            invalid = Auction.objects.get(title=new_Auction.title)
            invalid.delete()
            return render(request, "auctions/error.html", {
                "message": "Auction start cannot be set to past date / time"
            })
    return HttpResponseRedirect(reverse('index'))

def watchlist(request):

    # verify user is logged in
    if request.user.id is None:
        return HttpResponseRedirect(reverse('login'))

    return render(request, "auctions/watchlist.html", {
        "list": Watchlist.objects.get(user=request.user),
        "time": timezone.now
    })

def auction(request, auction):
    auction = Auction.objects.get(id=auction)

    if(auction.end_date < timezone.now()):
        auction.active = False

    if request.user.is_authenticated:
        watchlist = Watchlist.objects.get(user=request.user)
    else:
        watchlist = None

    if request.method == "GET":
        if auction.top_bid:
            return render(request, "auctions/auction.html", {
                "auction": auction,
                "bid_count": auction.bids.count(),
                "min_bid": auction.top_bid.amount + 1,
                "time": timezone.now,
                "users": User.objects.all(),
                "watchlist": watchlist
            })
        else:
            return render(request, "auctions/auction.html", {
                "auction": auction,
                "bid_count": auction.bids.count(),
                "min_bid": auction.price,
                "time": timezone.now,
                "users": User.objects.all(),
                "watchlist": watchlist
            })
    
    if request.method == "POST":
        new_bid = request.POST.get("bid", False)
        new_comment = request.POST.get("comment", False)
        watchlist_add = request.POST.get("atw", False)
        watchlist_remove = request.POST.get("rfw", False)
        end_auction = request.POST.get("end_auction", False)

        if new_bid:
            bid = Bid.objects.create(user=request.user, auction=auction, amount=new_bid)
            auction.bids.add(bid)
            auction.top_bid = bid
            auction.save()
            return render(request, "auctions/message.html", {
                "time": timezone.now,
                "message": "Bid successfully placed"
            })
        if new_comment:
            comment = Comment.objects.create(user=request.user, text=new_comment)
            auction.comments.add(comment)
            auction.save()

        if watchlist_add:
            watchlist.auction.add(auction)
        if watchlist_remove:
            watchlist.auction.remove(auction)
        
        if end_auction:
            auction.active = False
            auction.save()

        return HttpResponseRedirect(reverse('auction', args=[auction.id]))
        

def category_search(request):
    return render(request, "auctions/category_search.html", {
        "categories": Category.objects.all()
    })

def category(request, name):
    choice = Category.objects.get(name=name)

    return render(request, "auctions/category.html", {
        "auctions": Auction.objects.filter(category=choice).order_by('start_date').reverse()
    })