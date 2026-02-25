from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect
from .models import User, Listing, Category, Bid, Comment

def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    for listing in active_listings:
        latest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
        listing.current_price = latest_bid.amount if latest_bid else listing.starting_bid
    return render(request, "auctions/index.html", {"listings": active_listings})

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        return render(request, "auctions/login.html", {"message": "Invalid username and/or password."})
    return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return redirect("index")

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {"message": "Passwords must match."})
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {"message": "Username already taken."})
        login(request, user)
        return redirect("index")
    return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST.get("title")
        desc = request.POST.get("description")
        price = request.POST.get("price")
        image = request.POST.get("image")
        category = Category.objects.get(id=request.POST.get("category"))
        Listing.objects.create(title=title, description=desc, starting_bid=price, image_url=image, category=category, owner=request.user)
        return redirect("index")
    return render(request, "auctions/create.html", {"categories": Category.objects.all()})

def listing_page(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    current_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
    price = current_bid.amount if current_bid else listing.starting_bid
    error = None

    if request.method == "POST":
        if "bid_amount" in request.POST:
            bid_val = float(request.POST.get("bid_amount"))
            if bid_val > price:
                Bid.objects.create(amount=bid_val, user=request.user, listing=listing)
                return redirect("listing", listing_id=listing.id)
            else:
                error = f"Your bid must be higher than ${price}"

        elif "comment" in request.POST:
            Comment.objects.create(
                text=request.POST.get("comment"), 
                user=request.user, 
                listing=listing
            )
            return redirect("listing", listing_id=listing.id)

        elif "close_auction" in request.POST:
            listing.is_active = False
            listing.save()
            return redirect("listing", listing_id=listing.id)

    return render(request, "auctions/listing.html", {
        "listing": listing, 
        "price": price, 
        "current_bid": current_bid,
        "error": error
    })

@login_required
def toggle_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.user in listing.watchlist.all():
        listing.watchlist.remove(request.user)
    else:
        listing.watchlist.add(request.user)
    return redirect("listing", listing_id=listing_id)

@login_required
def watchlist_page(request):
    items = request.user.watchlist_items.all()
    return render(request, "auctions/watchlist.html", {"listings": items})

def categories_list(request):
    return render(request, "auctions/categories.html", {"categories": Category.objects.all()})

def category_detail(request, category_id):
    category = Category.objects.get(id=category_id)
    listings = Listing.objects.filter(category=category, is_active=True)
    
    for listing in listings:
        latest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
        listing.current_price = latest_bid.amount if latest_bid else listing.starting_bid

    return render(request, "auctions/index.html", {
        "listings": listings,
        "category_name": category.name
    })