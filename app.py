
from cs50 import SQL
from flask import Flask
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import string
from datetime import datetime

from flask import redirect, render_template, request, session
from helpers import lookup, nope, login_required, usd
from spooncalls import searchByIngredients, getRecipeURL, getPriceBreakdown

# Configure application
app = Flask(__name__)
port = 8000

# Custom filter
app.jinja_env.filters["usd"] = usd

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///pantree.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return nope("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return nope("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return nope("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Remember username
        session["user"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # initialize username
        if not request.form.get("username"):
            return nope("must provide username", 400)
        username = request.form.get("username")

        # check if username is available in database, render apology if not
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) > 0:
            return nope("username is not available", 400)

        # initialize password and password confirmation
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not request.form.get("password"):
            return nope("must provide password", 400)
        if not request.form.get("confirmation"):
            return nope("must re-enter password", 400)

        # render apology if inputs don't match or either is blank
        if confirmation != password:
            return nope("passwords do not match", 400)

        # Require user’s password to have some number of letters, numbers, and/or symbols
        passwordCheck = 0
        if len(password) < 12:
            passwordCheck += 1
        for char in password:
            if char.isupper():
                passwordCheck += 1
            if char.islower():
                passwordCheck += 1
            if char.isdigit():
                passwordCheck += 1
            if char in string.punctuation:
                passwordCheck += 1

        if passwordCheck < 5:
            return nope("password does not meet requirements", 400)

        # generate hash for user's password
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        # add user into database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # Redirect user to home page
        return redirect("/")

    # GET
    else:
        return render_template("register.html")


@app.route("/saved")
def saved():

    # Initialize list of saved recipes
    savedRecipes = []

    # Get all saved recipes from database with user ID
    recipeEntries = db.execute("SELECT * FROM savedRecipes WHERE user_id = ?",
                        session["user_id"])

    # Iterate through entries
    for entry in recipeEntries:

        # Set up dict with recipe info
        recipe = {
            "title": entry["recipe_title"],
            "image": entry["recipe_image"],
            "ingredients": entry["ingredients_count"],
            "url": entry["recipe_url"],
            "id": entry["recipe_id"],
            "datetime": entry["datetime"],
            "cost": entry["servingCost"],
            "time": entry["cookingTime"]
        }

        # Append to list of saved recipes
        savedRecipes.append(recipe)

    # Sort list from by datetime
    savedRecipes.sort(key=lambda k: k["datetime"], reverse=True)

    # Render results page
    return render_template("saved.html", savedRecipes=savedRecipes)


@app.route("/save", methods=["POST"])
def save():

    # Get data from button
    url = request.form.get("url")
    image = request.form.get("image")
    ingredients = request.form.get("ingredients")
    title = request.form.get("title")

    # Get data specific to Edamam/Spoonacular
    if request.form.get("cost"):
        source = 0
        cost = request.form.get("cost")
        time = request.form.get("time")
        id = request.form.get("id")
    else:
        source = 1
        uri = request.form.get("uri")
        id = uri.replace("http://www.edamam.com/ontologies/edamam.owl#recipe_", "")

    # Check that recipe was not already saved by user
    rows = db.execute("SELECT * FROM savedRecipes WHERE user_id = ? AND recipe_id = ?", session["user_id"], id)
    if len(rows) > 0:
        return nope("you already saved this recipe", 400)

    # Get time of save
    saveTime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Insert into database along with user ID
    if source == 0:
        db.execute("INSERT INTO savedRecipes (user_id, recipe_id, datetime, recipe_title, recipe_image, ingredients_count, recipe_url, servingCost, cookingTime) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                session["user_id"], id, saveTime, title, image, ingredients, url, cost, time)
    else:
        db.execute("INSERT INTO savedRecipes (user_id, recipe_id, datetime, recipe_title, recipe_image, ingredients_count, recipe_url) VALUES(?, ?, ?, ?, ?, ?, ?)",
                session["user_id"], id, saveTime, title, image, ingredients, url)

    # Redirect to saved recipes
    return redirect("/saved")


@app.route("/delete", methods=["POST"])
def delete():

    # Get recipe ID from form
    id = request.form.get("deleteRecipe")

    # Insert into database along with user ID
    db.execute("DELETE FROM savedRecipes WHERE user_id = ? AND recipe_id = ?", session["user_id"], id)

    # Redirect to saved recipes
    return redirect("/saved")


@app.route("/", methods=["GET", "POST"])
@login_required
def search():

    # POST
    if request.method == "POST":

        # Get ingredient.s
        ingredients = request.form.get("ingredients")
        if not ingredients:
            return nope("Invalid ingredients", 400)

        # Search through Edamam or Spoonacular depending on user input

        # SPOONACULAR
        if request.form.get("spoon"):

            source = "spoon"

            # Format user input
            ingredients = ingredients.replace(" ", "+")

            # Look up recipes from API
            response = searchByIngredients(ingredients)

            # Set up list of found recipes
            recipes = []

            # Iterate through response
            for hit in response:

                # Call API again for more details
                recipePriceBreakdown = getPriceBreakdown(hit["id"])
                recipeInfo = getRecipeURL(hit["id"])

                # Set up dict for each repice details
                recipe = {
                    "title": hit["title"],
                    "image": hit["image"],
                    "id": hit["id"],
                    "servingCost": recipePriceBreakdown["totalCostPerServing"],
                    "url": recipeInfo["sourceUrl"],
                    "ingredients": len(recipeInfo["extendedIngredients"]),
                    "time": recipeInfo["readyInMinutes"],
                }

                # Append recipe
                recipes.append(recipe)

            # If user has input a max cost per serving, filter out any recipe going over that cost
            if request.form.get("maxCost"):
                maxCost = float(request.form.get("maxCost"))
                filtered = [recipe for recipe in recipes if (float(recipe["servingCost"]) / 100) <= maxCost]
                recipes = filtered

            # Sort list of found recipes by cost per serving
            recipes.sort(key=lambda x: x["servingCost"])

            # Render results page
            return render_template("found.html", recipes=recipes, source=source)

        # EDAMAM
        else:

            source = "edamam"

            # Format user input
            ingredients = ingredients.replace(", ", "%2C%20")

            # Look up recipes
            response = lookup(ingredients)

            # Set up list of found recipes
            recipes = [recipe["recipe"] for recipe in response["hits"]]

            # Sort list of found recipes by number of ingredients
            recipes.sort(key=lambda x: len(x["ingredients"]))

            # Render results page
            return render_template("found.html", recipes=recipes, source=source)

    # GET
    else:
        return render_template("index.html")


if __name__ == '__main__':
    app.run(port=port)