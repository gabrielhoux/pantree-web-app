import requests
from flask import redirect, render_template, request, session
from functools import wraps

app_key = "51086659bd347b27f902c642c3aecf6e"
app_id = "47d41702"

def nope(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("nope.html", top=code, bottom=escape(message)), code

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


def lookup(ingredients):
    # Search for recipes from specific ingredients

    # Contact API
    try:
        url = f"https://api.edamam.com/api/recipes/v2?type=public&q={ingredients}&app_id={app_id}&app_key={app_key}"
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


def usd(value):
    """Format value as USD."""
    value /= 100
    return f"${value:,.2f}"
