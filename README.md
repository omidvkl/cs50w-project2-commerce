# Project: Commerce (CS50 Web)

## Overview
This is an e-commerce auction site where users can create auction listings, place bids, comment on listings, and add items to a "watchlist."

## Distinctiveness and Complexity
This project utilizes four Django models to manage a complex relational database. It handles user authentication, data validation (for bidding), and dynamic UI updates based on the state of the auction (active vs. closed).

## Models
- **User**: Standard Django user model for authentication.
- **Category**: Stores different categories for the listings (e.g., Home, Electronics).
- **Listing**: The core model for auction items, including title, description, starting bid, and image URL.
- **Bid**: Stores all bids made by users, linked to specific listings.
- **Comment**: Allows authenticated users to leave feedback on listings.

## How to Run
1. Install Django: `pip install django`
2. Run migrations: `python manage.py migrate`
3. Start the server: `python manage.py runserver`