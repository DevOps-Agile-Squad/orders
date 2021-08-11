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
          doc='/apidocs',  # default also could use doc='/apidocs/'
          )

# Define the Order model so that the docs reflect what can be sent
create_model = api.model('Order', {
    'customer_id': fields.Integer(required=True,
                                  description='The customer id the order is associated with'),
    'address': fields.String(required=True,
                             description='The delivery address'),
    'status': fields.String(required=True,
                            description='The current status of the order', enum=['Received', 'Processing', 'Completed', 'Cancelled', 'Returned'])
})

order_model = api.inherit(
    'OrderModel',
    create_model,
    {
        'id': fields.Integer(readOnly=True,
                             description='The unique id assigned internally by service'),
        'items': fields.List(cls_or_instance=fields.Raw,
                             description='collection of all items assigned to an order')
    }
)

# Define the Item model so that the docs reflect what can be sent
create_item_model = api.model('Item', {
    'order_id': fields.Integer(required=True,
                               description='The order id the item is associated with'),
    'quantity': fields.Integer(required=True,
                              description='The quantity of the item'),
    'price': fields.Float(required=True,
                              description='The price of the item'),
    'item_name': fields.String(required=True,
                               description='The name of the item')
})

item_model = api.inherit(
    'ItemModel',
    create_item_model,
    {
        'item_id': fields.Integer(readOnly=True,
                                  description='The unique id assigned internally by service'),
    }
)

# query string arguments (used as filters in List function)
order_args = reqparse.RequestParser()
order_args.add_argument('customer_id', type=int, location='args',
                        required=False, help='List Orders by customer_id')
order_args.add_argument('item', type=str, location='args',
                        required=False, help='List Orders by item')


######################################################################
# Special Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST


######################################################################
#  PATH: /orders/{id}
######################################################################
@api.route('/orders/<int:order_id>')
@api.param('order_id', 'The Order identifier')
class OrderResource(Resource):
    #     """
    #     OrderResource class
    #     Allows the manipulation of a single Order
    #     GET /order{id} - Returns a Order with the id
    #     PUT /order{id} - Update a Order with the id
    #     DELETE /order{id} -  Deletes a Order with the id
    #     """

    # ------------------------------------------------------------------
    # RETRIEVE AN ORDER
    # ------------------------------------------------------------------
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
            abort(status.HTTP_404_NOT_FOUND,
                  "Order with id '{}' was not found.".format(order_id))

        app.logger.info("Returning order: %s", order_id)
        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING ORDER
    # ------------------------------------------------------------------
    @api.doc('update_orders')
    @api.response(404, 'Order not found')
    @api.response(400, 'The posted Order data was not valid')
    @api.expect(order_model, validate=True)
    @api.marshal_with(order_model)
    def put(self, order_id):
        """
        Update an Order

        This endpoint will update an Order based the body that is posted
        """
        app.logger.info("Request to Update an order with id [%s]", order_id)
        order = CustomerOrder.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  "Order with id '{}' was not found.".format(order_id))
        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        order.deserialize(data)
        order.id = order_id
        order.update()
        app.logger.info("Order with ID [%s] updated.", order.id)
        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A ORDER
    # ------------------------------------------------------------------
    @api.doc('delete_orders')
    @api.response(204, 'Order deleted')
    def delete(self, order_id):
        """
        Delete a Order
        This endpoint will delete a Order based the id specified in the path
        """
        app.logger.info('Request to Delete a order with id [%s]', order_id)
        order = CustomerOrder.find(order_id)
        if order:
            order.delete()
            app.logger.info('Order with id [%s] was deleted', order_id)

        return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders
######################################################################
@api.route('/orders', strict_slashes=False)
class OrderCollection(Resource):
    """ Handles all interactions with collections of Orders """

    # ------------------------------------------------------------------
    # LIST ALL Orders
    # ------------------------------------------------------------------
    @api.doc('list_orders')
    @api.expect(order_args, validate=True)
    @api.marshal_list_with(order_model)
    def get(self):
        """Returns all of the orders"""
        app.logger.info("Request for order list")
        orders = []
        args = order_args.parse_args()
        if args['customer_id']:
            app.logger.info('Filtering by customer id: %s',
                            args['customer_id'])
            orders = CustomerOrder.find_by_customer_id(args['customer_id'])
        elif args['item']:
            app.logger.info('Filtering by item: %s', args['item'])
            orders = CustomerOrder.find_by_including_item(args['item'])
        else:
            app.logger.info('Returning unfiltered list.')
            orders = CustomerOrder.all()

        results = [order.serialize() for order in orders]
        app.logger.info("Returning %d orders", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW Order
    # ------------------------------------------------------------------
    @api.doc('create_orders')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model, validate=True)
    @api.marshal_with(order_model, code=201)
    def post(self):
        """
        Creates a Order
        This endpoint will create a Order based the data in the body that is posted
        """
        app.logger.info("Request to create a customer order")
        check_content_type("application/json")
        order = CustomerOrder()
        order.deserialize(api.payload)
        order.create()
        message = order.serialize()
        location_url = api.url_for(
            OrderResource, order_id=order.id, _external=True)

        app.logger.info("Order with ID [%s] created.", order.id)
        return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /orders/{id}/cancel
######################################################################
@api.route('/orders/<int:order_id>/cancel')
@api.param('order_id', 'The Order identifier')
class CancelResource(Resource):
    """ Cancel actions on a Order """
    @api.doc('cancel_orders')
    @api.response(404, 'Order not found')
    @api.response(409, 'The Order is not available for cancellation')
    def put(self, order_id):
        """
        Cancelling an order
        This endpoint will cancel an order based on order_id and notify other services
        """
        app.logger.info(f"Request to cancel order with id {order_id}")
        order = CustomerOrder.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  "Order with id '{}' was not found.".format(order_id))

        if order.status == Status.Completed or order.status == Status.Returned:
            abort(status.HTTP_409_CONFLICT,
                  f"Order with id {order_id} is [{order.status.name}], request refused.")

        order.id = order_id
        order.status = Status.Cancelled
        order.save()
        app.logger.info("Notify Shipping to cancel shipment...")
        app.logger.info("Notify Billing to refund payment...")
        app.logger.info(f"Order with id {order_id} cancelled successfully.")
        return order.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /orders/{order_id}/items/{item_id}
######################################################################
@api.route('/orders/<int:order_id>/items/<int:item_id>')
@api.param('item_id', 'The Item identifier')
@api.param('order_id', 'The Order identifier')
class ItemResource(Resource):
    #     """
    #     ItemResource class
    #     Allows the manipulation of a single Item
    #     GET /item{id} - Returns a Item with the id
    #     """

    # ------------------------------------------------------------------
    # RETRIEVE A ITEM
    # ------------------------------------------------------------------
    @api.doc('get_items')
    @api.response(404, 'Order not found')
    @api.marshal_with(item_model)
    def get(self, item_id, order_id):
        """
        Retrieve a single item in an order
        This endpoint will return an item based on its id and its order's id
        """
        app.logger.info(
            f"Request for item with id {item_id} in order {order_id}")
        order = CustomerOrder.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Order with id {order_id} was not found")

        item = Item.find(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Item with id {item_id} was not found in order {order_id}")

        app.logger.info(f"Returning item: {item_id}")
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A ITEM
    # ------------------------------------------------------------------
    @api.doc('delete_items')
    @api.response(204, 'Item deleted')
    @api.response(404, 'Item not found')
    def delete(self, item_id, order_id):
        """
        Delete a Item
        This endpoint will delete a Item based the id specified in the path
        """
        app.logger.info(f"Request to delete item with id {item_id}")
        order = CustomerOrder.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Order with id {order_id} is not found")
        item = Item.find(item_id)

        if item:
            if int(item.order_id) != int(order_id):
                abort(status.HTTP_404_NOT_FOUND,
                      f"Item with id {item.order_id} is not in order with id {order_id}")
            item.delete()
        app.logger.info(f"item with id {item_id} delete complete")
        return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders/{order_id}/items
######################################################################
@api.route('/orders/<int:order_id>/items', strict_slashes=False)
@api.param('order_id', 'The Order identifier')
class ItemCollection(Resource):
    """ Handles all interactions with collections of Items """

    # ------------------------------------------------------------------
    # ADD A NEW ITEM
    # ------------------------------------------------------------------
    @api.doc('create_item')
    @api.expect(create_item_model, validate=True)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'Item created successfully')
    @api.marshal_with(item_model, code=201)
    def post(self, order_id):
        """Adds item to an order."""
        app.logger.info("Request to add an item to an order")
        check_content_type("application/json")
        customer_order = CustomerOrder.find_or_404(order_id)
        item = Item()
        item.deserialize(api.payload)
        customer_order.items.append(item)
        customer_order.save()
        message = item.serialize()
        location_url = api.url_for(
            ItemResource, order_id=order_id, item_id=message['item_id'], _external=True)

        app.logger.info(f"Item with ID {message['item_id']} is created")
        return message, status.HTTP_201_CREATED, {"Location": location_url}


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


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
