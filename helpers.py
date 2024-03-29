# import os
# import requests
# import urllib.parse
from datetime import datetime

from flask import redirect, render_template, request, session
from functools import wraps


def avr(value):
    """Format value as 2 decimal"""
    return f"{value:.2f}"


def cur(value, currency):
    """Format value as any currency"""
    try:
        if currency in ['€', '₺']:
            return f"{value:,.2f} {currency}"
        else:
            return f"{currency} {value:,.2f}"
    except:
        return f"TBD"


def errorMsg(message):
    """Render an error page with an error message"""
    return render_template("error-message.html", message=message)


def dist(value, unit):
    """Format distance value as kilometer or mile"""
    return f"{value:,} {unit}".replace(",", " ")


def get_currency_symbol(currency):
    return currency[-1]


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def vol(value, unit):
    """Format volume value as liter/gallon"""
    try:
        return f"{value:,.2f} {unit}"
    except:
        return f"TBD"


def validate_password(password):
    """Validates password"""

    special_chars = ['!', '@', '#', '$', '%',
                     '&', '*', '_', '=', '+', '-', '.']

    # check for pass length
    if not len(password) >= 8 or not len(password) <= 20:
        print("Password length must be between 8 and 20!")
        message = "Password length must be between 8 and 20!"
        result = False
        return result, message

    # check if digit exist
    if not any(char.isdigit() for char in password):
        message = "Password must contain at least one number!"
        result = False
        return result, message

    # check if uppercase exist
    if not any(char.isupper() for char in password):
        message = "Password must contain at least one uppercase character!"
        result = False
        return result, message

    # check if lowercase exist
    if not any(char.islower() for char in password):
        message = "Password must contain at least one lowercase character!"
        result = False
        return result, message

    # check if special char exist
    if not any(char in special_chars for char in password):
        message = "Password should contain at least one of these '!, @, #, $, %, &, *, +, .' special characters!"
        result = False
        return result, message

    return True, ''


# def dt(value):
#     """Format value as date."""
#     # 2022-12-14T16:16:12.117Z   when db date type was TEXT
#     # 2022-12-14 16:16:12.117+00 when db date type is TIMESTAMP WITH TIME ZONE
#     value = str(value)
#     year = int(value[0:4])
#     month = int(value[5:7])
#     day = int(value[8:10])
#     d = datetime(year, month, day)
#     return f"{d.strftime('%d. %b %Y')}"
