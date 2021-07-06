# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
order Store Service

Paths:
------
GET /orders - Returns a list all of the orders
GET /orders/{id} - Returns the order with a given id number
POST /orders - creates a new order record in the database
PUT /orders/{id} - updates a order record in the database
DELETE /orders/{id} - deletes a order record in the database
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import CustomerOrder, Item, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
# @app.route("/")
# def index():
#     """Root URL response"""
#     app.logger.info("Request for Root URL")
#     return (
#         jsonify(
#             name="Orders Demo REST API Service",
#             version="1.0",
#             paths=url_for("list_orders", _external=True),
#         ),
#         status.HTTP_200_OK,
#     )


######################################################################
# LIST ALL CUSTOMER ORDERS
######################################################################
@app.route("/orders", methods=["GET"])
def list_orders():
    """Returns all of the orders"""
    app.logger.info("Request for order list")
    orders = []
    customer_id = request.args.get("customer_id")
    item = request.args.get("item")
    if customer_id:
        orders = CustomerOrder.find_by_customer_id(customer_id)
    elif item:
        orders = CustomerOrder.find_by_including_item(item)
    else:
        orders = CustomerOrder.all()

    results = [order.serialize() for order in orders]
    app.logger.info("Returning %d orders", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A CUSTOMER ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """
    Retrieve a single order
    This endpoint will return a customer_order based on it's id
    """
    app.logger.info("Request for order with id: %s", order_id)
    order = CustomerOrder.find(order_id)
    if not order:
        raise NotFound("Order with id '{}' was not found.".format(order_id))

    app.logger.info("Returning order: %s", order_id)
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)

######################################################################
# ADD ITEM TO A CUSTOMER ORDER
######################################################################
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
# ADD A NEW order
######################################################################
@app.route("/orders", methods=["POST"])
def create_order():
    """
    Creates a order
    This endpoint will create a order based the data in the body that is posted
    """
    app.logger.info("Request to create a customer order")
    check_content_type("application/json")
    order = CustomerOrder()
    order.deserialize(request.get_json())
    order.create()
    message = order.serialize()
    location_url = url_for("get_order", order_id=order.id, _external=True)

    app.logger.info("Order with ID [%s] created.", order.id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# UPDATE AN EXISTING ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_orders(order_id):
    """
    Update a CustomerOrder

    This endpoint will update a CustomerOrder based the body that is posted
    """
    app.logger.info("Request to update order with id: %s", order_id)
    check_content_type("application/json")
    order = CustomerOrder.find(order_id)
    if not order:
        raise NotFound("Order with id '{}' was not found.".format(order_id))
    order.deserialize(request.get_json())
    order.id = order_id
    order.update()

    app.logger.info("Order with ID [%s] updated.", order.id)
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE A ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_orders(order_id):
    """
    Delete a order

    This endpoint will delete a order based the id specified in the path
    """
    app.logger.info("Request to delete order with id: %s", order_id)
    order = CustomerOrder.find(order_id)
    if order:
        order.delete()

    app.logger.info("order with ID [%s] delete complete.", order_id)
    return make_response("", status.HTTP_204_NO_CONTENT)

@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(order_id, item_id):
    """
    Delete an item

    This endpoint will delete an item based on id specified in the path
    """
    app.logger.info(f"Request to delete item with id {item_id}")
    order = CustomerOrder.find(order_id)
    if order is None: 
        return make_response(f"Order with id {order_id} is not found", status.HTTP_404_NOT_FOUND)
    item = Item.find(item_id)
    
    if item is not None:
        if item.order_id != order_id:
            return make_response(f"Item with id {item.order_id} is not in order with id {order_id}", status.HTTP_404_NOT_FOUND)
        item.delete()
    app.logger.info(f"item with id {item_id} delete complete")
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )
