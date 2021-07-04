"""
My Service

Describe what your service does here

Source: https://github.com/nyu-devops/project-template/blob/master/service/routes.py
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
# from service.models import YourResourceModel, DataValidationError

# Import Flask application
from . import app
from service.model import CustomerOrder, Item, OrderBase

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )

@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    return make_response(jsonify(CustomerOrder.find_or_404(order_id), status.HTTP_200_OK))

######################################################################
# CREATE NEW ITEM
######################################################################

# curl --header "Content-Type: application/json" \
#   --request POST \
#   --data '{"order_id": 1, "price": 1, "quantity": 6, "item_name": "Egg"}' \
#   http://localhost:5000/orders/1/items

@app.route("/orders/<int:order_id>/items", methods=["POST"])
def add_item(order_id):
    """Adds item to an order."""
    app.logger.info("Request to add an item to an order")
    check_content_type("application/json")
    customer_order = CustomerOrder.find_or_404(order_id)
    item = Item()
    item.deserialize(request.get_json())
    customer_order.items.append(item)
    customer_order.save()
    message = item.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED)

######################################################################
# CREATE NEW ORDER (EMPTY)
######################################################################

# curl --header "Content-Type: application/json" \
#   --request POST \
#   --data '{"customer_id": 5, "address_line1": "123 1st Road", "city": "Jersey City", "state": "NJ", "zip_code": 12345, "items": []}' \
#   http://localhost:5000/orders

@app.route("/orders", methods=["POST"])
def create_order():
    """ Creates an order. """
    app.logger.info("Creating order")
    check_content_type("application/json")
    customer_order = CustomerOrder()
    customer_order.deserialize(request.get_json())
    customer_order.create()
    message = customer_order.serialize()
    location_url = url_for(
        "get_order", order_id=customer_order.order_id, _external=True)
    response = make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url})
    response.headers["Content-Type"] = "application/json"
    return response

def check_content_type(content_type):
    """ Checks that the media type is correct. """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))

def init_db():
    """ Initializes Database. """
    global app
    OrderBase.init_db(app)