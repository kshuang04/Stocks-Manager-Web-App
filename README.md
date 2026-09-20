# Stocks Manager Web App
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3BABC3?style=for-the-badge&logo=flask&logoColor=white)

## About
This is my implementation of the Finance app for Harvard CS50x's PS9. This web app was made using Flask. The content provided prior to my implemenation include the `/static` folder, `helpers.py`, `layout.html`, `login.html`, and the following routes in `app.py`:
* /login
* /logout

## Description
This web app allows users to trade stocks (with fake money). Here's a list of the actions users can take:
* Register new users (each new user starts with a cash balance of $10,000)
* View portfolio, which is a summary of the user's owned stocks, the stocks' current value, how much cash the user possesses, and the user's total balance (shares and cash combined)
* Look up current price if shares for a specific stock (quote)
* Buy shares
* Sell shares
* View transaction history
* Reset password

The following is a list of some of the features of the app:
* Handles user input validation and appropriately redirects users to an error page with a description of what went wrong and why
  * For example, if the user does not have enough cash to purchase their wanted number of shares of a stock, the transaction will not go through and the user is redirected to the error page stating that the user does not have enough balance
* Flask flashes throughout the app to give user feedback as they interact with the app
  * For example, when a new user registers for the first time, a welcome flash is displayed after registration, but for existing users, after logging in, they are greeted with a welcome back flash. Flashes also occur after users successfully buy and sell stocks

## Dependencies
All dependencies for this web app are listed in `requirements.txt`.\
To download the dependencies, run the following:
```
$ pip install -r requirements.txt
```

## How to run
This app runs locally on your machine. Run the following command to start the app:
```
$ flask run
```
