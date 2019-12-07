import os
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv('MONGO_URI', 'mongodb://localhost')
mongo = PyMongo(app)


@app.route('/')
def main():
    return render_template("base.html")


@app.route('/new_request')
def new_request():
    return render_template("new_request.html")


@app.route('/create_records', methods=['POST'])
def create_records():
    customer = {}  # Create a new empty dictionary for customer data
    payout = {}  # Create a new empty dictionary for payout data
    for key, value in request.form.items():
        # If data is about customer we add it to the customer dict
        if key == "recipient_name" or key == "country":
            customer[key] = value
        # Otherwise we add it to the payout dict    
        else:
            payout[key] = value
    #If data doesn't contain the customer_id it means customer it's not in the database and we need to insert it         
    if request.form.get("customer_id") == "":
        #Insert document with customer information
        insert = mongo.db.customers.insert_one(customer)
        #And we set the customer_id in the payout record
        payout["customer_id"] = insert.inserted_id
    #Insert document with payout information
    mongo.db.payouts.insert_one(payout)
    return redirect(url_for('new_request'))
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
