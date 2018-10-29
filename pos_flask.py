import os
import pymongo
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for

pos_system     = pymongo.MongoClient("mongodb://127.0.0.1:27017")
customer_order = pymongo.MongoClient("mongodb://127.0.0.1:27017")

db = pos_system["mydatabase"]

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Input new item for admin
@app.route('/admin')
def admin():
    return render_template('admin.html')

# Put data into mongodb
@app.route('/input', methods=["POST"])
def add():
    pr_id = request.form['pr_id']
    food  = request.form['food']
    price = request.form['price']
    db.pos_system.insert({"Product_ID": pr_id, "Food": food, "Price": price})
    return redirect(url_for('cashier'))

# Show available item
@app.route('/cashier', methods=["GET"])
def cashier():
    pos = db.pos_system.find()
    return render_template('cashier.html', pos=pos)

# Input customer order from admin data
@app.route('/order_customer')
def o_c():
    find_name = db.customer_order.find().sort("customer_name", 1)
    name_found_dict = {}
    name_list = []
    for find_name_item in find_name:
        customer_name = find_name_item["customer_name"]
        if not customer_name in name_found_dict:
            name_list.append ( customer_name )
            name_found_dict[customer_name] = customer_name
        # end if
    #end for
    return render_template('order_customer.html', find_name=name_list)

@app.route('/order', methods=["POST"])
def order():
    if request.method=="POST":
        pr_id = request.form['pr_id']
        customer_name = request.form['customer_name']
        cari = db.pos_system.find_one({"Product_ID":pr_id})
        del cari["_id"]
        cari ['customer_name']= customer_name
        db.customer_order.insert(cari)
        return redirect("customer?cname="+customer_name)
    else:
        return "ERROR"

@app.route('/customer', methods=["GET"])
def order_result():
    cname = request.args.get("cname")
    ors = db.customer_order.find({"customer_name":cname})
    return render_template(
        'final_order.html',
        ors=ors,
        cname=cname
    )

if __name__ == '__main__':
    app.run(debug=True)
