from crypt import methods
import os
import datetime
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, Request, Response, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import errorMsg, login_required, cur, avr, validate_password, dist, vol

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filters from helpers.py
app.jinja_env.filters["avr"] = avr
app.jinja_env.filters["cur"] = cur
app.jinja_env.filters["dist"] = dist
# app.jinja_env.filters["dt"] = dt
app.jinja_env.filters["vol"] = vol

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# database replaced from local
# db = SQL("sqlite:///refueltracker.db")
# to heroku
uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")
db = SQL(uri)

# ***** CONFIGURING ENDS HERE *****

# X todo: retrieve username as value (not placeholder) on change-username.html page
# X todo: set char limit for names (vehicle, license plate, username)
# X todo: set limit for odometer, volume, unit price
# X todo: show local time on edit
# todo: print should show table borders
# X todo: set default units to EUR and lt
# todo: refuels table, change distance -> odometer

# ! add minlength and maxlength to password fields on html pages.
# ! changing vehicle name doesn't affect old transactions
# ! check if vehicle name exist - use strip so that user can't name his cars 'smart' and 'smart '
# ? chart date filter
# ? total distance traveled stat on vehicles page


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show last entries, let user add/delete/edit new entry"""

    user_id = session["user_id"]

    # retrieve username and unit settings
    try:
        user_db = db.execute(
            "SELECT * FROM users WHERE id=?", user_id)
    except:
        return errorMsg("Couldn't retrieve data from server. Please refresh the page.")

    user = user_db[0]

    username = user["username"]
    currency_symbol = user["currency"][-1]
    distance_unit = user["distance_unit"]
    volume_unit = user["volume_unit"]

    # set default value of date input to now
    # returns "2022-12-11 22:47:56"
    # date_db = db.execute("SELECT CURRENT_TIMESTAMP(0)")
    # print(f"########{date_db[0]}")
    # print(f"########{date_db[0]['current_timestamp']}")
    # date_now = date_db[0]["current_timestamp"]

    # select vehicles to show in dropdown menu
    vehicles = db.execute(
        "SELECT * FROM vehicles WHERE user_id=?", user_id)

    # length of distinct vehicles' array, this will help 2 things:
    # in order to hide/show tables in case no vehicle exist
    # if there's more than 1 vehicle, show one more column (vehicle name) on table
    vehicles_len = len(db.execute(
        "SELECT DISTINCT vehicle_id FROM refuels WHERE user_id=?", user_id))

    # retrieve last 3 entries from refuels table
    latest_refuels = db.execute(
        "SELECT refuels.id, refuels.date, refuels.distance, refuels.volume, "
        "refuels.price, refuels.total_price, refuels.user_id, "
        "refuels.vehicle_id, vehicles.name AS vehicle_name "
        "FROM refuels "
        "JOIN vehicles ON refuels.vehicle_id = vehicles.id "
        "WHERE refuels.user_id=? "
        "ORDER BY refuels.date DESC LIMIT 3;", user_id)

    # length of refuels to show/hide tables (most recent entries & statistics table)
    ref_len = len(latest_refuels)

    # query for total distance traveled & total liters & total expenses
    # * FIXED: instead of GROUP BY vehicle_id -> temporarily vehicle_name
    statistics_db = db.execute(
        "SELECT (MAX(distance) - MIN(distance)) AS distance, "
        "SUM(volume) AS liters, SUM (total_price) AS expenses, "
        "vehicles.name AS vehicle_name "
        "FROM refuels "
        "JOIN vehicles ON refuels.vehicle_id = vehicles.id "
        "WHERE refuels.user_id=? "
        "GROUP BY vehicles.id", user_id)

    # stats' table should show when one vehicle has at least 2 transactions
    onShow = False
    for stat in statistics_db:
        if stat["distance"] > 0:
            onShow = True
            break

    # abbreviations for chart
    # months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    #           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # query label (show day-month-year) and value (total fuel expense) to show on chart
    # ? PostgreSQL version
    chart_db = db.execute(
        "SELECT SUM(total_price) AS total_price, "
        "date_trunc('month', date::timestamptz) AS mon "
        "FROM refuels WHERE user_id=? "
        "AND date::timestamptz < (SELECT NOW() + INTERVAL '1 day') "
        "AND date::timestamptz > (SELECT date_trunc('month', NOW() - INTERVAL '2 month')) "
        "GROUP BY mon", user_id)
    # ? SQLite version
    # chart_db = db.execute("SELECT SUM(total_price) AS total_price, date FROM refuels WHERE user_id=? AND date < (SELECT date('now', 'localtime', '+1 day')) AND date > (SELECT date('now', 'localtime', '-2 month', 'start of month')) GROUP BY strftime('%m', date)", user_id)

    # print(f"###$$$$%%% {chart_db[0]['mon'].strftime('%Y-%m-%d')} ###$$$%%%")
    # print(f"###$$$$%%% {chart_db[0]['mon'].strftime('%m-%Y')} ###$$$$%%")
    # labels = [months[int(x["mon"].strftime('%Y-%m-%d')[5:7]) - 1]
    #           for x in chart_db]

    labels = [x["mon"].strftime('%m-%Y') for x in chart_db]
    values = [x["total_price"] for x in chart_db]

    # * GET carries request parameter appended in URL string (req from client to server in HTTP)
    # user reached route via GET, as by clicking a link or via redirect()
    if request.method == "GET":
        return render_template("index.html", vehicles=vehicles, refuels=latest_refuels, ref_len=ref_len, veh_len=vehicles_len, labels=labels, values=values, symbol=currency_symbol, distance_unit=distance_unit, volume_unit=volume_unit, stats=statistics_db, show=onShow, username=username)

    # * POST carries request parameter in message body
    # user reached route via POST, as by submitting a form via POST
    elif request.method == "POST":

        try:
            date = request.form.get("datetime")
        except:
            return errorMsg("An error has been occured during the process of assigning a value to date!")

        vehicle_names = [vehicle['name'] for vehicle in vehicles]

        selected_vehicle = request.form.get("vehicle")
        # validation
        if not selected_vehicle or not selected_vehicle in vehicle_names:
            return errorMsg("Invalid vehicle!")

        # ? if user has more than one car, list should also show vehicle_name field
        selected_vehicle_db = db.execute(
            "SELECT * FROM vehicles WHERE user_id=? AND name = ?", user_id, selected_vehicle)
        sel_vehicle_id = selected_vehicle_db[0]['id']
        # * vehicle_name removed from refuel table
        # sel_vehicle_name = selected_vehicle_db[0]['name']

        # current total distance traveled that can be read on the odometer (int type)
        distance = request.form.get("distance")

        # ensure distance exist, and it's bigger than zero, if so convert the value into integer
        if not distance or not int(distance) > 0 or not int(distance) < 10000000:
            return errorMsg("Invalid odometer reading! Value must be between 0 and 10000000")
        else:
            distance = int(distance)

        # volume of refuel (float type)
        volume = request.form.get("volume")

        # ensure volume exist, and it's bigger than zero, if so convert the value into float
        if not volume or not float(volume) > 0 or not float(volume) < 10000:
            return errorMsg("Invalid volume! Value must be between 0 and 10000")
        else:
            volume = float(request.form.get("volume"))

        # unit price of refuel (float type)
        unit_price = request.form.get("price")

        # ensure price exist, and it's greater than zero, if so convert the value into float
        if not unit_price or not float(unit_price) > 0 or not float(unit_price) < 10000000:
            return errorMsg("Invalid unit price! Value must be between 0 and 10000000")
        else:
            unit_price = float(unit_price)

        # calculate total price
        total_price = unit_price * volume

        # insert new entry into database
        # * vehicle_name removed from refuel table
        try:
            db.execute("INSERT INTO refuels (date, distance, volume, price, total_price, user_id, vehicle_id) VALUES(?,?,?,?,?,?,?)",
                       date, distance, volume, unit_price, total_price, user_id, sel_vehicle_id)
        except:
            return errorMsg("Ooops! An error has been occured :(")

        # select updated database after a new entry
        refuels_upd_db = db.execute(
            "SELECT refuels.id, refuels.date, refuels.distance, "
            "refuels.volume, refuels.price, refuels.total_price, "
            "refuels.user_id, refuels.vehicle_id, vehicles.name AS vehicle_name "
            "FROM refuels "
            "JOIN vehicles ON refuels.vehicle_id = vehicles.id "
            "WHERE refuels.user_id=? "
            "ORDER BY refuels.date DESC LIMIT 3;", user_id)

        # length of updated refuels rows
        ref_len_upd = len(refuels_upd_db)

        # length of updated vehicles rows
        vehicles_len = len(db.execute(
            "SELECT DISTINCT vehicle_id FROM refuels WHERE user_id=?", user_id))

        # query updated statistics
        # * FIXED instead of GROUP BY vehicle_id -> temporarily vehicle_name
        statistics_db_upd = db.execute(
            "SELECT (MAX(distance) - MIN(distance)) AS distance, "
            "SUM(volume) AS liters, SUM (total_price) AS expenses, "
            "vehicles.name AS vehicle_name "
            "FROM refuels "
            "JOIN vehicles ON refuels.vehicle_id = vehicles.id "
            "WHERE refuels.user_id=? "
            "GROUP BY vehicles.id", user_id)

        onShow_upd = False
        for stat in statistics_db_upd:
            if stat["distance"] > 0:
                onShow_upd = True
                break

        # retrieve updated refuels to show on chart
        chart_db_upd = db.execute(
            "SELECT SUM(total_price) AS total_price, "
            "date_trunc('month', date::timestamptz) AS mon "
            "FROM refuels "
            "WHERE user_id=? AND date::timestamptz < (SELECT NOW() + INTERVAL '1 day') "
            "AND date::timestamptz > (SELECT date_trunc('month', NOW() - INTERVAL '2 month')) "
            "GROUP BY mon", user_id)

        # updated chart's labes & values
        # labels_upd = [
        #     months[int(x["mon"].strftime('%Y-%m-%d')[5:7]) - 1] for x in chart_db_upd]
        labels_upd = [x["mon"].strftime('%m-%Y') for x in chart_db_upd]
        values_upd = [x["total_price"] for x in chart_db_upd]

        return render_template("index.html", vehicles=vehicles, refuels=refuels_upd_db, ref_len=ref_len_upd, veh_len=vehicles_len, labels=labels_upd, values=values_upd, symbol=currency_symbol, distance_unit=distance_unit, volume_unit=volume_unit, stats=statistics_db_upd, show=onShow_upd, username=username)

    # user reached route via PUT, DELETE
    else:
        return errorMsg("You're NOT authorized!")


@ app.route("/account")
@ login_required
def account():
    """Shows account settings"""
    return render_template("account.html")


@ app.route("/change-units", methods=["GET", "POST"])
@ login_required
def changeCur():
    """Show currency settings"""
    user_id = session["user_id"]

    # available currency list
    currencies = ['USD - $', 'EUR - €', 'GBP - £',
                  'KRW - ₩', 'KZT - ₸', 'TRY - ₺']
    # symbols = [x[-1] for x in currencies]

    # user's unit settings
    user_units_db = db.execute(
        "SELECT currency, distance_unit, volume_unit FROM users WHERE id=?", user_id)

    user_currency = user_units_db[0]["currency"]
    user_distance_unit = user_units_db[0]["distance_unit"]
    user_volume_unit = user_units_db[0]["volume_unit"]

    other_currencies = []
    for currency in currencies:
        if not currency == user_currency:
            other_currencies.append(currency)
        else:
            continue

    # user reached route via GET
    if request.method == "GET":
        return render_template("change-units.html", currencies=other_currencies, user_currency=user_currency, user_distance_unit=user_distance_unit, user_volume_unit=user_volume_unit)

    # user reached route via POST
    elif request.method == "POST":

        # new currency setting submitted by user
        selected_currency = request.form.get("currency")

        # ensure currency exist
        if not selected_currency:
            return errorMsg("Invalid currency!")

        # new distance unit (kilometer/mile) submitted by user
        selected_distance_unit = request.form.get("distance")

        # ensure valid distance unit submitted
        if not selected_distance_unit:
            return errorMsg("Invalid distance unit")

        # new volume unit (lt/gal) submitted by user
        selected_volume_unit = request.form.get("volume")

        # ensure valid volume unit submitted by user
        if not selected_distance_unit:
            return errorMsg("Invalid distance unit")

        # update new setting in database
        try:
            db.execute("UPDATE users SET currency=?, distance_unit=?, volume_unit=? WHERE id=?",
                       selected_currency, selected_distance_unit, selected_volume_unit, user_id)
        except:
            return errorMsg("Ooops! An error has been occured :(")

        # flash user with message
        flash(
            f"Unit settings has been updated to '{selected_currency}' | '{selected_distance_unit}' | '{selected_volume_unit}'")

        # send user back to home page
        return redirect("/")

    else:
        return errorMsg("You're not authorized for this action!")


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def changePassword():
    """Show password settings"""
    user_id = session["user_id"]

    # user reached via GET
    if request.method == "GET":
        return render_template("change-password.html")

    # user reached via POST
    elif request.method == "POST":

        # query existing hashed password
        password_db = db.execute(
            "SELECT hash FROM users WHERE id=?", user_id)
        old_hash = password_db[0]["hash"]

        # old password submitted by user
        old_password = request.form.get("old-password")
        # ensure old password exists
        if not old_password:
            return errorMsg("Must provide old password!")

        # new password submitted by user
        new_password = request.form.get("password")
        # ensure new password exists
        if not new_password:
            return errorMsg("Must provide new password!")

        # if password doesn't meet requirements, return error
        # validate_password() function returns False if password invalid (check helpers.py for detail)
        isPassOK, message = validate_password(new_password)
        # check if password meets requirements
        if not isPassOK:
            return errorMsg(message)

        # confirmation of the new password
        confirmation = request.form.get("confirmation")
        # ensure confirmation exists
        if not confirmation:
            return errorMsg("Must confirm new password!")

        # ensure new password exists
        if not new_password == confirmation:
            return errorMsg("Please confirm you password")

        # old pass should match pass from db
        if not check_password_hash(old_hash, old_password):
            return errorMsg("Invalid old password!")

        new_hash = generate_password_hash(new_password)

        # update users password in database
        try:
            db.execute("UPDATE users SET hash=? WHERE id=?",
                       new_hash, user_id)
        except:
            return errorMsg("Ooops! An error has been occured :(")

        # flash with a message
        flash("Password has been updated!")

        # send user back to homepage
        return redirect("/")

    # user reached route via PUT or DELETE
    else:
        return errorMsg("You're not authorized for this action!")


@app.route("/change-username", methods=["GET", "POST"])
@login_required
def changeUsername():
    """Changes username"""
    user_id = session["user_id"]
    try:
        username_db = db.execute(
            "SELECT username FROM users WHERE id=?", user_id)
        old_name = username_db[0]["username"]
    except:
        return errorMsg("Ooops! An error has been occured during the retrieve of user information from database :(")

    if request.method == "GET":
        return render_template("change-username.html", old_username=old_name)

    elif request.method == "POST":

        old_username = request.form.get("old-username")
        if not old_username or not len(old_username) < 256:
            return errorMsg("Invalid old username! Value must be between 0 and 256 characters.")

        new_username = request.form.get("username")
        if not new_username or not len(new_username) < 256:
            return errorMsg("Invalid new username! Value must be between 0 and 256 characters.")

        # check for potential errors
        for char in new_username:
            if char == ' ':
                return errorMsg("Space character in username is not allowed!")

        confirmation = request.form.get("confirmation")
        if not confirmation:
            return errorMsg("Must confirm new username!")

        if not new_username == confirmation:
            return errorMsg("Please confirm you username")

        # old username should match current username from db
        if not old_name == old_username:
            return errorMsg("Invalid username!")

        # username has to be unique
        usernames_db = db.execute("SELECT username FROM users")
        for username in usernames_db:
            if new_username == username["username"]:
                return errorMsg("This username is already exist :(")

        try:
            db.execute("UPDATE users SET username=? WHERE id=?",
                       new_username, user_id)
        except:
            return errorMsg("Ooops! An error has been occured :(")

        flash("Your username has been updated!")

        return redirect("/")

    else:
        return errorMsg("You're not authorized for this action!")


@app.route("/delete-refuel/<int:id>", methods=["POST"])
@login_required
def deleteRefuel(id):
    """Deletes refuel after confirmation"""

    if request.method == "POST":
        refuel_delete_id = db.execute(
            "SELECT * FROM refuels WHERE user_id=? AND id=?", session["user_id"], id)

        if not refuel_delete_id:
            return errorMsg("Transaction ID can not be found!")

        try:
            # * db.execute("DELETE") returns the number of rows deleted
            db.execute("DELETE FROM refuels WHERE id=?", id)
        except:
            return errorMsg("Ooops! An error has been occured while deleting from refuels table :(")

        flash("Transaction has been deleted!")

        return redirect("/")

    else:
        return errorMsg("This method is not allowed!")


@app.route("/delete-vehicle/<int:id>", methods=["POST"])
@login_required
def deleteVehicle(id):
    """Deletes vehicle after confirmation"""
    if request.method == "POST":

        vehicle_delete_db = db.execute(
            "SELECT * FROM vehicles WHERE user_id=? AND id=?", session["user_id"], id)

        if not vehicle_delete_db:
            return errorMsg("Not found!")

        vehicle = vehicle_delete_db[0]['name']

        # if vehicle has refuel transaction(s), remove those
        rows = db.execute("SELECT * FROM refuels WHERE vehicle_id=?", id)
        if len(rows) > 0:
            try:
                db.execute("DELETE FROM refuels WHERE vehicle_id=?", id)
            except:
                return errorMsg("Ooops! An error has been occured while deleting from refuels table :( ")

        try:
            db.execute("DELETE FROM vehicles WHERE id=?", id)
        except:
            return errorMsg("Ooops! An error has been occured while deleting from vehicles table :(")

        flash(f"{vehicle} has been deleted!")

        return redirect('/')

    else:
        return errorMsg("You are not authorized for this action!")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    """Edits an entry with a certain id"""
    user_id = session["user_id"]

    # retrieve user's refuel row from database
    # * vehicle_name removed from refuel table
    refuel_db = db.execute(
        "SELECT refuels.id, refuels.date, refuels.distance, "
        "refuels.volume, refuels.price, refuels.total_price, refuels.user_id, "
        "refuels.vehicle_id, vehicles.name AS vehicle_name "
        "FROM refuels "
        "JOIN vehicles ON refuels.vehicle_id = vehicles.id "
        "WHERE refuels.user_id=? AND refuels.id=?", user_id, id)
    # ensure refuel submitted was valid
    if not refuel_db:
        return errorMsg("Not found!")

    # set default value of date input to now
    # date_db = db.execute("SELECT TIMESTAMP WITH TIME ZONE 'NOW'")
    # date = date_db[0]["TIMESTAMP WITH TIME ZONE 'NOW'"]

    # show old date as placeholder
    date = refuel_db[0]["date"]
    # convert datetime.datetime object to string
    date = str(date)
    # print(f"OOOOOOOOOOOOO {date} OOOOOOOOOOOOO")
    # print(f"OOOOOOOOOOOOO {str(date)} OOOOOOOOOOOOO")
    # 2022-12-14T16:16:12.117Z

    # retrieve user's vehicles' names
    users_vehicles_db = db.execute(
        "SELECT name FROM vehicles WHERE user_id=?", user_id)

    # amount of vehicles owned by user
    vehicle_len = len(users_vehicles_db)

    # create a list that excludes the vehicle from transaction that needs to be edited
    vehicles_list = []
    for vehicle in users_vehicles_db:
        if vehicle['name'] == refuel_db[0]["vehicle_name"]:
            continue
        else:
            vehicles_list.append(vehicle['name'])

    if request.method == "GET":
        return render_template("edit.html", refuel=refuel_db[0], date=date, id=id, vehicles=vehicles_list, veh_len=vehicle_len)

    elif request.method == "POST":

        # date submitted by user
        date = request.form.get("datetime")

        # date validation
        try:
            date = request.form.get("datetime")
        except:
            return errorMsg("An error has been occured during the process of assigning a value to date!")

        distance = request.form.get("distance")
        # distance validation
        if not distance or not int(distance) > 0 or not int(distance) < 10000000:
            return errorMsg("Invalid odometer reading! Value must be between 0 and 10000000.")
        else:
            distance = int(distance)

        volume = request.form.get("volume")

        # volume validation
        if not volume or not float(volume) > 0 or not float(volume) < 10000:
            return errorMsg("Invalid volume! Value must be between 0 and 10000.")
        else:
            volume = float(volume)

        price = request.form.get("price")

        # unit price validation
        if not price or not float(price) > 0 or not float(price) < 10000000:
            return errorMsg("Invalid unit price! Value must be between 0 and 10000000.")
        else:
            price = float(price)

        # calculate total price
        total_price = volume * price

        if vehicle_len >= 2:
            vehicle_name = request.form.get("vehicle")
            # vehicle name validation
            if not vehicle_name:
                return errorMsg("Must provide vehicle!")

            # retrieve new vehicle's id from database
            else:
                vehicle_id_db = db.execute(
                    "SELECT id FROM vehicles WHERE user_id=? AND name=?", user_id, vehicle_name)
                vehicle_id = vehicle_id_db[0]["id"]
            # update database with edited refuel transaction
            # * vehicle_name removed from refuel table
            try:
                db.execute("UPDATE refuels SET date=?, distance=?, volume=?, price=?, total_price=?, vehicle_id=? WHERE id=?",
                           date, distance, volume, price, total_price, vehicle_id, id)
            except:
                return errorMsg("Ooops! An error has been occured :(")

        else:
            # update database with edited refuel transaction
            # * vehicle_name removed from refuel table
            try:
                db.execute("UPDATE refuels SET date=?, distance=?, volume=?, price=?, total_price=? WHERE id=?",
                           date, distance, volume, price, total_price, id)
            except:
                return errorMsg("Ooops! An error has been occured :(")

        flash("Entry has been updated succesfully!")

        return redirect("/")

    else:
        return errorMsg("Method not allowed!")


@app.route("/edit-vehicle/<int:id>", methods=["GET", "POST"])
@login_required
def editVehicle(id):
    """Edits vehicle name or plate number"""
    user_id = session["user_id"]
    # query for vehicle to be edited
    vehicle_db = db.execute(
        "SELECT name, license_plate FROM vehicles WHERE user_id=? AND id=?", user_id, id)

    # user musn't reach ids that aren't his/her, by changing the URL manually
    if not vehicle_db:
        return errorMsg("Not found!")

    # current name of the vehicle, user might keep the name, this is used in name check below
    current_vehicle_name = vehicle_db[0]['name']

    # every vehicle from user, used in name check below
    user_vehicles_db = db.execute(
        "SELECT * FROM vehicles WHERE user_id=?", user_id)

    if request.method == "GET":
        return render_template("edit-vehicle.html", vehicle=vehicle_db, id=id)

    elif request.method == "POST":

        vehicle_name = request.form.get("vehicle_name")
        # name validation
        if not vehicle_name:
            return errorMsg("Must provide name for a vehicle")

        # ? ncortex
        if vehicle_name.startswith(" "):
            return errorMsg("Vehicle name can not start with space character(s)")
        if vehicle_name.endswith(" "):
            return errorMsg("Vehicle name can not end with space character(s)")

        # ! check if this works fine
        # check if vehicle name already exist for the same user EXCEPT FOR FORMER VEHICLE NAME
        if len(user_vehicles_db) > 1:
            for i in range(len(user_vehicles_db)):
                if user_vehicles_db[i]["name"] == vehicle_name:
                    if current_vehicle_name == vehicle_name:
                        break
                    else:
                        return errorMsg("Vehicle's name must be unique!")

        # license plate number submitted by user
        license_plate = request.form.get("plate")
        if not license_plate:
            license_plate = ''
        # ? ncortex
        if license_plate.startswith(" "):
            return errorMsg("Vehicle name can not start with space character(s)")
        if license_plate.endswith(" "):
            return errorMsg("Vehicle name can not end with space character(s)")

        # update database
        try:
            db.execute("UPDATE vehicles SET name=?, license_plate=? WHERE user_id=? AND id=?",
                       vehicle_name, license_plate, user_id, id)
            # * vehicle_name removed from refuel table
            # db.execute(
            #     "UPDATE refuels SET vehicle_name=? WHERE vehicle_id=?", vehicle_name, id)
        except:
            return errorMsg("Ooops! An error has been occured :(")

        flash("Vehicle's information has been updated!")

        return redirect("/")

    else:
        return errorMsg("You are not authorized for this action!")


@app.route("/history")
@login_required
def history():
    """Shows the history of refuel transactions"""
    user_id = session["user_id"]

    # query user's unit settings
    try:
        user_db = db.execute(
            "SELECT * FROM users WHERE id=?", user_id)
    except RuntimeError:
        return errorMsg("Could not receieve data from server. Please refresh the page.")

    user = user_db[0]

    currency_symbol = user["currency"][-1]
    distance_unit = user["distance_unit"]
    volume_unit = user["volume_unit"]

    # query all transactions
    refuels_db = db.execute(
        "SELECT refuels.id, refuels.date, refuels.distance, "
        "refuels.volume, refuels.price, refuels.total_price, refuels.user_id, "
        "refuels.vehicle_id, vehicles.name AS vehicle_name "
        "FROM refuels "
        "JOIN vehicles ON refuels.vehicle_id = vehicles.id "
        "WHERE refuels.user_id=? "
        "ORDER BY refuels.date DESC", user_id)

    # length of transactions
    ref_len = len(refuels_db)

    # retrieve grand total of total price column
    sum_expense_db = db.execute(
        "SELECT SUM(total_price) AS grand_total FROM refuels WHERE user_id=?", user_id)

    # grand total
    sum_expense = sum_expense_db[0]["grand_total"]

    # abbr. of months for chart
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # sum (group) each month's transactions for more concise/clean chart

    # PostgreSQL version (shows last 12 months)
    chart_db = db.execute(
        "SELECT SUM(total_price) AS total_price, "
        "date_trunc('month', date::timestamptz) AS mon "
        "FROM refuels "
        "WHERE user_id=? "
        "AND date::timestamptz < (SELECT NOW() + INTERVAL '1 day') "
        "AND date::timestamptz > (SELECT date_trunc('month', NOW() - INTERVAL '11 month')) "
        "GROUP BY mon", user_id)

    # SQLite version (shows current year only)
    # chart_db = db.execute("SELECT SUM(total_price) AS total_price, date FROM refuels WHERE user_id=? AND date < (SELECT date('now', 'localtime', '+1 year', 'start of year')) AND date > (SELECT date('now', 'localtime', 'start of year', '-1 day')) GROUP BY strftime('%m', date)", session["user_id"])

    # pick month part from the string to show as label of the chart
    # labels = [months[int(x["mon"].strftime('%Y-%m-%d')[5:7]) - 1]
    #           for x in chart_db]
    labels = [x["mon"].strftime('%m-%Y') for x in chart_db]

    # total expense for that specific month
    values = [x["total_price"] for x in chart_db]

    # length of refuel transactions
    vehicles_len = len(db.execute(
        "SELECT DISTINCT vehicle_id FROM refuels WHERE user_id=?", user_id))

    if request.method == "GET":
        return render_template("history.html", refuels=refuels_db, ref_len=ref_len, veh_len=vehicles_len, labels=labels, values=values, symbol=currency_symbol, distance_unit=distance_unit, volume_unit=volume_unit, total_expenses=sum_expense)
    else:
        return errorMsg("You're not authorized for this action!")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return errorMsg("Type a valid username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return errorMsg("Type a valid password")

        # Query database for username
        users_db = db.execute("SELECT * FROM users WHERE username = ?",
                              request.form.get("username"))

        # Ensure username exists and password is correct
        if not len(users_db) == 1 or not check_password_hash(users_db[0]["hash"], request.form.get("password")):
            return errorMsg("Invalid username/password")

        # Remember which user has logged in
        session["user_id"] = users_db[0]["id"]

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
    return redirect("/login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Sign user up"""
    # if user visits by clicking a link/redirect
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":

        # variables submitted by user
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # check for potential errors
        if not username or not len(username) < 256:
            return errorMsg("Invalid username! Value must be between 0 and 256 characters.")
        for char in username:
            if char == ' ':
                return errorMsg("Space character in username is not allowed!")

        if not password or not len(password) < 256:
            return errorMsg("Invalid password! Value must be between 0 and 256 characters.")
        if not confirmation:
            return errorMsg("Please confirm your password")
        if not password == confirmation:
            return errorMsg("Passwords do NOT match!")

        # if password doesn't meet requirements, return error
        # validate_password() function returns False if password invalid (check helpers.py for detail)
        isPassOK, message = validate_password(password)
        if not isPassOK:
            return errorMsg(message)

        # if username already exist
        # retrieve users from database
        users_db = db.execute("SELECT * FROM users")

        # ensure username does not exist
        for user in users_db:
            if user["username"] == username:
                return errorMsg("Username is already taken")

        # hash password
        hash = generate_password_hash(password)

        # add register date to table
        register_date_db = db.execute("SELECT NOW()")
        register_date = register_date_db[0]["now"]

        # INSERT INTO db new user's information
        try:
            new_user_id = db.execute(
                "INSERT INTO users (username, hash, register_date) VALUES(?, ?, ?)", username, hash, register_date)
        except:
            return errorMsg("Ooops! An error has been occured!")

        # Log the user in
        session["user_id"] = new_user_id

        # Flash user with welcoming message!
        flash(f"Welcome, {username}!")

        # send user to the homepage
        return redirect("/")

    # if user somehow send request via "DELETE"/"PUT" methods
    else:
        return errorMsg("This method is not allowed!")


@app.route("/vehicles", methods=["GET", "POST"])
@login_required
def vehicles():
    """Show all vehicles owned by user"""
    user_id = session["user_id"]

    # query user's unit settings
    try:
        user_db = db.execute("SELECT * FROM users WHERE id=?", user_id)
    except:
        return errorMsg("Could not retrieve data from server. Please refresh the page.")

    user = user_db[0]

    currency_symbol = user["currency"][-1]
    distance_unit = user["distance_unit"]
    volume_unit = user["volume_unit"]

    # retrieve total volume of refuels, total cost of refuels from vehicles table
    vehicles_db = db.execute(
        "SELECT vehicles.id, vehicles.name, vehicles.license_plate, "
        "SUM(volume) AS liters, SUM(total_price) AS expenses "
        "FROM vehicles "
        "LEFT JOIN refuels ON vehicles.id = refuels.vehicle_id "
        "WHERE vehicles.user_id=? "
        "GROUP BY vehicles.id "
        "ORDER BY vehicles.id", user_id)
    # vehicles_db = db.execute("SELECT *, SUM(volume) AS liters, SUM(total_price) AS expenses FROM vehicles LEFT JOIN refuels ON vehicles.id = refuels.vehicle_id WHERE vehicles.user_id=? GROUP BY vehicles.id ORDER BY vehicles.id", session["user_id"])

    # length of vehicles list
    veh_length = len(vehicles_db)

    # query user's currency
    # currency_db = db.execute(
    #     "SELECT currency FROM users WHERE id=?", session["user_id"])

    if request.method == "GET":
        return render_template("vehicles.html", vehicles=vehicles_db, veh_len=veh_length, symbol=currency_symbol, distance_unit=distance_unit, volume_unit=volume_unit)

    elif request.method == "POST":

        vehicle_name = request.form.get("vehicle_name")
        # name validation
        if not vehicle_name:
            return errorMsg("Must provide name for a vehicle")

        # ? ncortex
        if vehicle_name.startswith(" "):
            return errorMsg("Vehicle name can not start with space character(s)")
        if vehicle_name.endswith(" "):
            return errorMsg("Vehicle name can not end with space character(s)")

        # ! check if this works fine
        # check if vehicle name already exist for the same user
        if len(vehicles_db) > 1:
            for i in range(len(vehicles_db)):
                if vehicles_db[i]["name"] == vehicle_name:
                    return errorMsg("Vehicle's name must be unique!")

        # license plate number submitted by user
        license_plate = request.form.get("plate")
        if not license_plate:
            license_plate = ''
        # ? ncortex
        if license_plate.startswith(" "):
            return errorMsg("Vehicle name can not start with space character(s)")
        if license_plate.endswith(" "):
            return errorMsg("Vehicle name can not end with space character(s)")

        # retrieve current local date & time
        date_db = db.execute("SELECT NOW()")
        date = date_db[0]["now"]

        # add new vehicle to the vehicles table
        try:
            db.execute("INSERT INTO vehicles (name, license_plate, date, user_id) VALUES(?, ?, ?, ?)",
                       vehicle_name, license_plate, date, user_id)
        except:
            return errorMsg("Ooops! An error has been occured :(")

        # select updated version of data
        vehicles_db_uptd = db.execute(
            "SELECT vehicles.id, vehicles.name, vehicles.license_plate, "
            "SUM(volume) AS liters, SUM(total_price) AS expenses "
            "FROM vehicles "
            "LEFT JOIN refuels ON vehicles.id = refuels.vehicle_id "
            "WHERE vehicles.user_id=? "
            "GROUP BY vehicles.id "
            "ORDER BY vehicles.id", user_id)
        # vehicles_db_uptd = db.execute("SELECT *, SUM(volume) AS liters, SUM(total_price) AS expenses FROM vehicles LEFT JOIN refuels ON vehicles.id = refuels.vehicle_id WHERE vehicles.user_id=? GROUP BY vehicles.id ORDER BY vehicles.id", session["user_id"])

        # length of updated list
        veh_len_upd = len(vehicles_db_uptd)

        return render_template("vehicles.html", vehicles=vehicles_db_uptd, veh_len=veh_len_upd)

    else:
        return errorMsg("Sorry, you're not authorized!")
