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
POST /orders/{id}/items - adds an item to the order
DELETE /orders/{id} - deletes a order record in the database
DELETE /orders/{order_id}/items/{item_id}> - deletes the item in the order
POST /orders/{id}/cancel - cancels the order (change status to Cancelled)
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_restx import Api, Resource, fields, reqparse, inputs
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import CustomerOrder, Item, DataValidationError, Status

# Import Flask application
from . import app
from . import status  # HTTP Status Codes

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Order Demo REST API Service',
          description='This is an Orders service api',
          default='orders',
          default_label='Order service operations',
          doc='/apidocs', # default also could use doc='/apidocs/'
         )


# Define the model so that the docs reflect what can be sent
create_model = api.model('Order', {
    'customer_id': fields.Integer(required=True,
                          description='The customer id the order is associated with'),
    'address': fields.String(required=True,
                              description='The delivery address'),
    'status': fields.String(required=True,
                                description='The current status of the order', enum=['Received', 'Processing', 'Completed', 'Cancelled', 'Returned'])
})

# class that inherits from fields.Raw so that it can be used in fields.List() 
class OrderItem(fields.Raw):
    def format(self, value):
        return {'id': value.id,
                'order_id': value.order_id,
                'quantity': value.quantity,
                'price': value.price,
                'item_name': value.item_name}

order_model = api.inherit(
    'OrderModel', 
    create_model,
    {
        'id': fields.String(readOnly=True,
                            description='The unique id assigned internally by service'),
        'items': fields.List(cls_or_instance=OrderItem,
                                description='collection of all items assigned to an order')
    }
)

# query string arguments (used as filters in List function)
# order_args = reqparse.RequestParser()
# order_args.add_argument('customer_id', type=int, required=False, help='List Orders by customer_id')
# order_args.add_argument('item', type=str, required=False, help='List Orders by item')

######################################################################
#  PATH: /orders/{id}
######################################################################
@api.route('/orders/<order_id>')
@api.param('order_id', 'The Order identifier')
class OrderResource(Resource):
    """
    OrderResource class
    Allows the manipulation of a single Order
    GET /order{id} - Returns a Order with the id
    PUT /order{id} - Update a Order with the id
    DELETE /order{id} -  Deletes a Order with the id
    """

    #------------------------------------------------------------------
    # RETRIEVE AN ORDER
    #------------------------------------------------------------------
    @api.doc('get_orders')
    @api.response(404, 'Order not found')
    @api.marshal_with(order_model)
    def get(self, order_id):
        """
        Retrieve a single Order
        This endpoint will return an Order based on it's id
        """
        app.logger.info("Request for order with id: %s", order_id)
        order = CustomerOrder.find(order_id)
        if not order:
            raise NotFound("Order with id '{}' was not found.".format(order_id))

        app.logger.info("Returning order: %s", order_id)
        return order.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE A EXISTING ORDER
    #------------------------------------------------------------------
    # @api.doc('update_orders')
    # @api.response(404, 'Order not found')
    # @api.response(400, 'The posted Order data was not valid')
    # @api.expect(order_model)
    # @api.marshal_with(order_model)
    # def put(self, order_id):
    #     """
    #     Update a Order 
    #     This endpoint will update a Order based the body that is posted
    #     """
    #     pass

    #------------------------------------------------------------------
    # DELETE A ORDER
    #------------------------------------------------------------------
    # @api.doc('delete_orders')
    # @api.response(204, 'Order deleted')
    # def delete(self, order_id):
    #     """
    #     Delete a Order
    #     This endpoint will delete a Order based the id specified in the path
    #     """
    #     pass

######################################################################
#  PATH: /orders
######################################################################
@api.route('/orders', strict_slashes=False)
class OrderCollection(Resource):
    """ Handles all interactions with collections of Orders """
#     #------------------------------------------------------------------
#     # LIST ALL Orders
#     #------------------------------------------------------------------
#     @api.doc('list_orders')
#     @api.expect(order_args, validate=True)
#     @api.marshal_list_with(order_model)
#     def get(self):
#         """ Returns all of the Orders """
#         pass


    #------------------------------------------------------------------
    # ADD A NEW Order
    #------------------------------------------------------------------
    @api.doc('create_orders')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    @api.marshal_with(order_model, code=201)
    def post(self):
        """
        Creates a Order
        This endpoint will create a Order based the data in the body that is posted
        """
        app.logger.info("Request to create a customer order")
        check_content_type("application/json")
        order = CustomerOrder()
        order.deserialize(request.get_json())
        order.create()
        message = order.serialize()
        location_url = api.url_for(OrderResource, order_id=order.id, _external=True)

        app.logger.info("Order with ID [%s] created.", order.id)
        return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /orders/{id}/cancel
######################################################################
# @api.route('/orders/<order_id>/cancel')
# @api.param('order_id', 'The Order identifier')
# class CancelResource(Resource):
#     """ Cancel actions on a Order """
#     @api.doc('cancel_orders')
#     @api.response(404, 'Order not found')
#     @api.response(409, 'The Order is not available for cancellation')
#     def put(self, order_id):
#         """
#         Cancel a Order
#         This endpoint will cancel a Order 
#         """
#         pass


######################################################################
# ALL TRADITIONAL ROUTES (NOT YET REFACTORED) ARE BELOW 
######################################################################

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
# GET AN ITEM BY ORDER ID AND ITEM ID
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def get_item(order_id, item_id):
    """
    Retrieve a single item in an order
    This endpoint will return an item based on its id and its order's id
    """
    app.logger.info(f"Request for item with id {item_id} in order {order_id}")
    order = CustomerOrder.find(order_id)
    if not order: 
        raise NotFound(f"Order with id {order_id} was not found")
    
    item = Item.find(item_id)
    if not item: 
        raise NotFound(f"Item with id {item_id} was not found in order {order_id}")
    
    app.logger.info(f"Returning item: {item_id}")
    return make_response(jsonify(item.serialize()), status.HTTP_200_OK)


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
    location_url = url_for("get_item", order_id=order_id, item_id=message['item_id'], _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED, {"Location": location_url})


######################################################################
# ADD A NEW order
######################################################################
# @app.route("/orders", methods=["POST"])
# def create_order():
#     """
#     Creates a order
#     This endpoint will create a order based the data in the body that is posted
#     """
#     app.logger.info("Request to create a customer order")
#     check_content_type("application/json")
#     order = CustomerOrder()
#     order.deserialize(request.get_json())
#     order.create()
#     message = order.serialize()
#     location_url = url_for("get_order", order_id=order.id, _external=True)

#     app.logger.info("Order with ID [%s] created.", order.id)
#     return make_response(
#         jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
#     )


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
    app.logger.info(f"Order id is {order.id}")
    order.update()

    app.logger.info("Order with ID [%s] updated.", order.id)
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE AN ORDER
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


######################################################################
# DELETE AN ITEM
######################################################################
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
            return make_response(f"Item with id {item.order_id} is not in order with id {order_id}",
                                 status.HTTP_404_NOT_FOUND)
        item.delete()
    app.logger.info(f"item with id {item_id} delete complete")
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# CANCELLING AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/cancel", methods=["POST"])
def cancel_orders(order_id):
    """
    Cancelling an order

    This endpoint will cancel an order based on order_id and notify other services
    """
    app.logger.info(f"Request to cancel order with id {order_id}")
    order = CustomerOrder.find(order_id)
    if not order:
        return make_response(f"Order with id {order_id} is not found", status.HTTP_404_NOT_FOUND)

    if order.status == Status.Completed or order.status == Status.Returned:
        return make_response(f"Order with id {order_id} is [{order.status.name}], request refused.",
                             status.HTTP_400_BAD_REQUEST)

    if order.status == Status.Cancelled:
        return make_response(f"Order with id {order_id} is already cancelled.", status.HTTP_200_OK)

    order.id = order_id
    order.status = Status.Cancelled
    order.save()
    app.logger.info("Notify Shipping to cancel shipment...")
    app.logger.info("Notify Billing to refund payment...")
    app.logger.info(f"Order with id {order_id} cancelled successfully.")
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


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
