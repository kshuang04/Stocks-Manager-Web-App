# Stocks Manager Web App
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3BABC3?style=for-the-badge&logo=flask&logoColor=white)

## About
This is my implementation of the Finance app for Harvard CS50x's PS9. This web app was made using Flask. The content provided prior to my implemenation include the `/static` folder, `helpers.py`, `layout.html`, `login.html`, and the following routes in `app.py`:
* /login
* /logout

## Description
This web app allows users to trade stocks (with fake money). This app allows for multiple users which are created through registration and each user starts wih a cash balance of $10,000. User can look up the current price of shares for a specific stock (quote), buy shares, and sell shares. The user can also view their transaction history as well as view their portfolio which gives a summary of their owned stocks and their current value, how much cash the user possesses, and the total balance (shares and cash combined). The app also handles user input validation and appropriately redirects users to an error page if something goes wrong and gives the user a description of the problem. There is also implementation of Flask's flashes throughout the app to give user feedback as they interact with the app. For example, when a new user registers for the first time, a welcome flash is displayed after logging in, but for existing users logging in, they get a welcome back flash. Appropriate flashes also occur when users buy and sell stocks. Additionally, users are able to reset their password.

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
