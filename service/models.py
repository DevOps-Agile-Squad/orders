# Copyright 2016, 2021 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Models for orders Service

All of the models are stored in this module

Models
------
CustomerOrder - An order object containing all the items in a customer order.

    Attributes:
    -----------
    customer_id (integer) - the id of the customer
    address (string) - the shipping address of the order
    items (relationship) - collections of items that are inside the order
    status (enum) - the status of the order (received, processing, cancelled, etc.)

Item - An item object represents the product in an order.

    Attributes:
    -----------
    order_id (fk integer) - the order number that the item is associated with
    quantity (integer) - the quantity of this item in the order
    price (integer) - the price of the product
    item_name (integer) - the name of the product
"""
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app") # pylint: disable=invalid-name

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy() # pylint: disable=invalid-name


def init_db(app):
    """Initialies the SQLAlchemy app"""
    CustomerOrder.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Status(Enum):
    """Enumeration of valid Order Status"""

    Received = 0
    Processing = 1
    Completed = 2
    Cancelled = 3
    Returned = 4


######################################################################
#  I T E M   M O D E L
######################################################################
class Item(db.Model):
    """
    Class that represents an Item
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey(
        'customer_order.id'), nullable=False)
    # If null quantity will be treated as 1.
    quantity = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Integer, nullable=False)
    # e.g., ball, balloon, etc.
    item_name = db.Column(db.String(120), nullable=False)

    def __eq__(self, other):
        return (self.id == other.id) or ((self.id is None or other.id is None) and
                                         (self.item_name == other.item_name) and
                                         (self.order_id == other.order_id) and
                                         (self.quantity == other.quantity) and
                                         (self.price == other.price))

    @classmethod
    def find(cls, item_id):
        """Finds an item by its ID

        :param item_id: the id of the order to find
        :type item_id: int

        :return: an instance with the item_id, or None if not found
        :rtype: order

        """
        logger.info("Processing lookup for id %s ...", item_id)
        return cls.query.get(item_id)

    def delete(self):
        """Removes an item from the data store"""
        logger.info("Deleting order %s", self.id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Address into a dictionary """
        return {
            "item_id": self.id,
            "order_id": self.order_id,
            "quantity": self.quantity,
            "price": self.price,
            "item_name": self.item_name,
        }

    def deserialize(self, data):
        """
        Deserializes a Item from a dictionary
        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.order_id = data["order_id"]
            self.quantity = data["quantity"]
            self.price = data["price"]
            self.item_name = data["item_name"]
        except KeyError as error:
            raise DataValidationError("Invalid Item: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: details of item contained bad or no data"
            )
        return self


class CustomerOrder(db.Model):
    """
    Class that represents a CustomerOrder

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    app = None

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(256), nullable=False)
    items = db.relationship('Item', backref='order',
                            lazy=True, cascade="all, delete")
    status = db.Column(
        db.Enum(Status), nullable=False, server_default=(Status.Received.name)
    )

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return f"Order [{self.id}] by Customer [{self.customer_id}] with address: {self.address}. \
                Status: [{self.status.name}]"

    def create(self):
        """
        Creates a CustomerOrder to the database
        """
        logger.info("Creating order %s", self.id)
        # id must be none to generate next primary key
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a CustomerOrder to the database
        """
        logger.info("Updating order %s", self.id)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """Removes a order from the data store"""
        logger.info("Deleting order %s", self.id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """Serializes a order into a dictionary"""
        order = {
            "id": self.id,
            "customer_id": self.customer_id,
            "address": self.address,
            "items": [],
            "status": self.status.name,  # convert enum to string
        }
        for item in self.items:
            order["items"].append(item.serialize())
        return order

    def deserialize(self, data):
        """
        Deserializes a order from a dictionary

        :param data: a dictionary of attributes
        :type data: dict

        :return: a reference to self
        :rtype: order

        """
        try:
            self.customer_id = data["customer_id"]
            self.address = data["address"]
            self.items = []
            if 'items' in data and data['items']:
                for item_str in data.get('items'):
                    item = Item()
                    item.deserialize(item_str)
                    self.items.append(item)
            # create enum from string
            self.status = getattr(Status, data["status"])
        except KeyError as error:
            raise DataValidationError(
                "Invalid order: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid order: body of request contained bad or no data"
            )
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app):
        """Initializes the database session

        :param app: the Flask app
        :type data: Flask

        """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the orders in the database"""
        logger.info("Processing all orders")
        return cls.query.all()

    @classmethod
    def find(cls, customer_order_id):
        """Finds a order by it's ID

        :param order_id: the id of the order to find
        :type order_id: int

        :return: an instance with the order_id, or None if not found
        :rtype: order

        """
        logger.info("Processing lookup for id %s ...", customer_order_id)
        return cls.query.get(customer_order_id)

    @classmethod
    def find_or_404(cls, customer_order_id):
        """Find a CustomerOrder by it's id

        :param customer_order_id: the id of the CustomerOrder to find
        :type customer_order_id: int

        :return: an instance with the order_id, or 404_NOT_FOUND if not found
        :rtype: order

        """
        logger.info("Processing lookup or 404 for id %s ...",
                    customer_order_id)
        return cls.query.get_or_404(customer_order_id)

    def save(self):
        """
        Updates a order into the database
        """
        logger.info("Saving %s", self.id)
        db.session.commit()

    @classmethod
    def find_by_customer_id(cls, customer_id):
        """Returns all orders with the given customer_id

        :param customer_id: the id of the customer you want to match
        :type customer_id: integer

        :return: a collection of orders with that customer
        :rtype: list

        """
        logger.info("Processing customer_id query for %s ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id)

    @classmethod
    def find_by_including_item(cls, item_name):
        """Returns all orders with the given item name

        :param item_name: the name of the item you want to match
        :type name: str

        :return: a collection of coders with that item inside
        :rtype: list

        """
        logger.info("Processing including item query for %s ...", item_name)
        return cls.query.filter(cls.items.any(Item.item_name == item_name))

    # @classmethod
    # def find_by_category(cls, category):
    #     """Returns all of the Pets in a category

    #     :param category: the category of the Pets you want to match
    #     :type category: str

    #     :return: a collection of Pets in that category
    #     :rtype: list

    #     """
    #     logger.info("Processing category query for %s ...", category)
    #     return cls.query.filter(cls.category == category)

    # @classmethod
    # def find_by_availability(cls, available=True):
    #     """Returns all Pets by their availability

    #     :param available: True for pets that are available
    #     :type available: str

    #     :return: a collection of Pets that are available
    #     :rtype: list

    #     """
    #     logger.info("Processing available query for %s ...", available)
    #     return cls.query.filter(cls.available == available)

    # @classmethod
    # def find_by_gender(cls, gender=Gender.Unknown):
    #     """Returns all Pets by their Gender

    #     :param gender: values are ['Male', 'Female', 'Unknown']
    #     :type available: enum

    #     :return: a collection of Pets that are available
    #     :rtype: list

    #     """
    #     logger.info("Processing gender query for %s ...", gender.name)
    #     return cls.query.filter(cls.gender == gender)
