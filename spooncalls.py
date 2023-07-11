import requests
from flask import redirect, render_template, request, session
from functools import wraps

api_key = "06e49418a8694c87af4d4d0ef58d1efd"

def searchByIngredients(ingredients):
    # Search for recipes from specific ingredients

    # Contact API
    try:
        url = f"https://api.spoonacular.com/recipes/findByIngredients?apiKey={api_key}&ingredients={ingredients}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        results = response.json()
        return results
    except (KeyError, TypeError, ValueError):
        return None

def getRecipeURL(id):
    # Search for recipes from specific ingredients

    # Contact API
    try:
        url = f"https://api.spoonacular.com/recipes/{id}/information?apiKey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        results = response.json()
        return results
    except (KeyError, TypeError, ValueError):
        return None

def getPriceBreakdown(id):
    # Search for recipes from specific ingredients

    # Contact API
    try:
        url = f"https://api.spoonacular.com/recipes/{id}/priceBreakdownWidget.json?apiKey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        results = response.json()
        return results
    except (KeyError, TypeError, ValueError):
        return None