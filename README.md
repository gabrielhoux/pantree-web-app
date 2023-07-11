# PANTREE
#### Video Demo:  https://youtu.be/lWi2JO4JrYo
#### Description:

Pantree is a web app that allows you to search for recipes from ingredients you may have in your... pantry.
I've developped this app using Flask, SQLite, Bulma, and two APIs called Edamam and Spoonacular.
A lot fo features I simply carried over from the CS50 Finance project. Why? I'm quite interested in Web Programming and feel comfortable using Python frameworks. I thought it better to keep training myself in Flask for this final project. I then aim to take CS50W and am excited to learn more.

There are three different Python files at the core of this project: app.py, containing the app's main features; helpers.py, inspired by the same file from CS50 Finance, providing helpful features for login requirements, error rendering and an API call for Edamam to look up recipes from ingredients; and spooncalls.py, which contains all the Spoonacular API calls required to look up recipes form ingredients, get their cost, their cooking time info, and their URL.

To use Pantree, you must first register an account. From register.html, the user must enter a username and a password. That password must contain at least 12 characters, including at least one lowercase letter, one uppercase, one number and one special character. Then, that password must be entered a second time in a field below for confirmation.
If any field is left empty, or is the password does not meet the requirements or does not match the password confirmation, an error page will be rendered for the user.
If the user's username already exists in the SQLite database I set up for the app, an error page will be rendered as well.

Once registered, the user will be prompted to log in on login.html. Again, the login function is quite simple and was carried over from CS50 Finance.

Once logged in, the user is sent to index.html, the Search Recipes page. Here, the user may enter one or more ingredients. CHECKBOX. The search feature relies on API calls, made using the ingredients entered by the user.

The two APIs involved in this web app are from Edamam and Spoonacular.
Edamam provides a quick search from ingredients and is quite accurate, but does not provide any cost related information.
Spoonacular is much slower, as it requires multiple API calls to get all the info that is really broken down into different parts.
Spoonacular is the more relevant API for the nature of my project, but since they make it more difficult not to pay them for their service by limiting requests, which is fair but not quite student-friendly, I chose to keep Edamam around for "lighter" searches.
To switch between the two options, I've devised a simple checkbox prompting the user whether they to x.

Whether Edamam or Spoonacular was called, which the search function figures out from the checkbox in the html form, the found.html page is rendered, listing all found recipes and some of the info made available by the API for each of those recipes. For Edamam, only the number of ingredients is prompted. With Spoonacular, the user also gets the cost of each serving and the total cooking time.

From there, the user may read on any found recipe by clicking on the "View recipe" button, which sends the user to the relevant URL. They may also save the recipe in their collection with the "Save recipe" button, which calls the save function from app.py. A form containing each of the recipe details is attached to the save button. The recipe details can then be saved to the SQL database in the savedRecipes table, along with the user's ID.

Any recipe the user has saved will be present in the Saved Recipes page, saved.html. Again, the user may visit the recipe page by clicking on the "View recipe" button, and delete the recipe from the collection, if they so wish, by clicking on "Delete recipe". The button calls on the delete function from app.py, which simply finds the relevant recipe from the database using its ID and deletes the entry.

This is it for the features!

Other than that, I've used the Bulma framework for the web app's CSS and HTML features, such as the navbar.

