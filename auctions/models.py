from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auction(models.Model):
    title = models.CharField(max_length=31)
    description = models.TextField(max_length=800)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_user")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField(blank=True)
    end_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="auction_category")
    comments = models.ManyToManyField('Comment', related_name="auction_comments", blank=True)
    bids = models.ManyToManyField('Bid', related_name="auction_bids", blank=True)
    top_bid = models.ForeignKey('Bid', on_delete=models.CASCADE, related_name="auction_top_bid", blank=True, null=True)
    active = models.BooleanField(default=True)

    def datepublished(self):
        return self.date.strftime('%B %d %Y')

    def __str__(self):
        return self.title
    
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_user")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bid_auction')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.amount}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user")
    text = models.CharField(max_length=200)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user}:/n{self.text}"

class Category(models.Model):
    name = models.CharField(max_length=31)

    def __str__(self):
        return f"{self.name}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_user")
    auction = models.ManyToManyField(Auction, related_name="watchlist_auctions")