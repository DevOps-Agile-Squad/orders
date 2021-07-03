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

from werkzeug.exceptions import NotFound

# Import Flask application
from . import app
from service.model import CustomerOrder, OrderBase

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

######################################################################
# CREATE NEW ORDER (EMPTY)
######################################################################

# curl --header "Content-Type: application/json" \
#   --request POST \
#   --data '{"id":1,customer_id:2}' \
#   http://localhost:5000/orders

@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """
    Retrieve a single order

    This endpoint will return an order based on its id
    """
    app.logger.info(f"requrest for order with {order_id}")
    maybe_order = CustomerOrder.find(order_id)
    if not maybe_order:
        raise NotFound(f"Order with id {order_id} was not found")
    app.logger.info(f"Returning order {order_id}")
    return make_response(jsonify(maybe_order.serialize(), status.HTTP_200_OK))

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