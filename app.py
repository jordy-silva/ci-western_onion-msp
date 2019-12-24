import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv('MONGO_URI', 'mongodb://localhost')
mongo = PyMongo(app)
app.secret_key = 'qJunUwiYfq2tQsCBaJJ3dg3'


@app.route('/show_all')
def show_all():
    try:
        return render_template("queue.html", customers=list(mongo.db.customers.find()), payouts=list(mongo.db.payouts.find()))
    except:
        return render_template("error.html")


@app.route('/new_request')
def new_request():
    try:
        return render_template("payout.html", customer="", payout="", reasons=mongo.db.reasons.find(), countries=mongo.db.countries.find())
    except:
        flash('Unable to load reasons or countries')
        return render_template("payout.html", customer="", payout="", reasons="", countries="")


@app.route('/add_payout/<customer_id>')
def add_payout(customer_id):
    try:
        return render_template("payout.html", action="add", customer=mongo.db.customers.find_one({"_id": ObjectId(customer_id)}), payout="", reasons=mongo.db.reasons.find())
    except:
        flash('Unable to load data')
        return redirect(url_for('show_all'))


@app.route('/edit_payout/<customer_id>/<payout_id>')
def edit_payout(customer_id, payout_id):
    try:
        return render_template("payout.html", action="edit", customer=mongo.db.customers.find_one({"_id": ObjectId(customer_id)}), payout=mongo.db.payouts.find_one({"_id": ObjectId(payout_id)}), reasons=mongo.db.reasons.find(), countries=mongo.db.countries.find())
    except:
        flash('Unable to load data')
        return redirect(url_for('show_all'))


@app.route('/create_records', methods=['POST'])
def create_records():
    customer = {}  # Create a new empty dictionary for customer data
    payout = {}  # Create a new empty dictionary for payout data
    for key, value in request.form.items():
        # If data is about customer we add it to the customer dict
        if key == "recipient_name" or key == "country":
            customer[key] = value
        if key == "customer_id":
            if value:
                payout[key] = ObjectId(value)
        # Otherwise we add it to the payout dict
        else:
            payout[key] = value
    # If data doesn't contain the customer_id it means customer it's not in the database and we need to insert it
    if request.form.get("customer_id") == "":
        # Insert document with customer information
        try:
            insert = mongo.db.customers.insert_one(customer)
            flash('Recipient added to cancel queue')
            # And we add the customer_id in the payout dictionary
            payout["customer_id"] = insert.inserted_id
        except:
            flash('Could NOT add recipient')
    # Insert document with payout information
    try:
        mongo.db.payouts.insert_one(payout)
        flash('Payout added to cancel queue')
    except:
        flash('Could NOT add payout')
    return redirect(url_for('show_all'))


@app.route('/update_records', methods=['POST'])
def update_records():
    customer = {}  # Create a new empty dictionary for customer data
    payout = {}  # Create a new empty dictionary for payout data
    for key, value in request.form.items():
        # If data is about customer we add it to the customer dict
        if key == "recipient_name" or key == "country":
            customer[key] = value
        # Otherwise it is added to the payout dict
        else:
            # Unless it's the _id's which will be used to define the document to oupdate
            if key != "customer_id" and key != "payout_id":
                payout[key] = value
    # Update both customer and payout document
    try:
        mongo.db.customers.update_one(
            {"_id": ObjectId(request.form['customer_id'])}, {"$set": customer})
        flash('Recipient updated')
    except:
        flash('Could NOT update recipient')
    try:
        mongo.db.payouts.update_one(
            {"_id": ObjectId(request.form['payout_id'])}, {"$set": payout})
        flash('Payout updated')
    except:
        flash('Could NOT update payout')
    return redirect(url_for('show_all'))


@app.route('/delete_payout/<customer_id>/<payout_id>')
def delete_payout(customer_id, payout_id):
    try:
        # Deletion of the payout
        mongo.db.payouts.remove({'_id': ObjectId(payout_id)})
        flash('Payout deleted')
        # If there are no more payouts related to that customer, also delete the customer
        if not mongo.db.payouts.find_one({"customer_id": ObjectId(customer_id)}):
            mongo.db.customers.remove({'_id': ObjectId(customer_id)})
            flash('Recipient deleted')
    except:
        flash('Could NOT delete')
    finally:
        return redirect(url_for('show_all'))

@app.route('/delete_all', methods=['POST'])
def delete_all():
    flash('Email Sent')
    try:
        # Deletion of all payouts
        mongo.db.payouts.delete_many({})
        flash('ALL payouts deleted')
        # Deletion of all customers
        mongo.db.customers.delete_many({})
        flash('ALL customers deleted')
    except:
        flash('Could NOT delete')
    finally:
        return redirect(url_for('show_all'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=False)
