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
Models for Pet Demo Service

All of the models are stored in this module

Models
------
Pet - A Pet used in the Pet Store

Attributes:
-----------
name (string) - the name of the pet
category (string) - the category the pet belongs to (i.e., dog, cat)
available (boolean) - True for pets that are available for adoption

"""
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialies the SQLAlchemy app"""
    CustomerOrder.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""

    pass


######################################################################
#  I T E M   M O D E L
######################################################################
class Item(db.Model):
    """
    Class that represents an Item
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('customer_order.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=True)  # If null quantity will be treated as 1.
    price = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.String(120), nullable=False) # e.g., ball, balloon, etc.

    def __eq__(self, other):
        return (self.id == other.id) or ((self.id is None or other.id is None) and
            (self.item_name == other.item_name) and
            (self.order_id == other.order_id) and
            (self.quantity == other.quantity) and
            (self.price == other.price))

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
                "Invalid Item: details of item contained"  "bad or no data"
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
    items = db.relationship('Item', backref='order', lazy=True)
    

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return f"Order {self.id} by Customer {self.customer_id} with address: {self.address}"

    def create(self):
        """
        Creates a CustomerOrder to the database
        """
        logger.info(f"Creating order {self.id}")
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a CustomerOrder to the database
        """
        logger.info(f"Updating order {self.id}")
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """Removes a Pet from the data store"""
        logger.info(f"Deleting order {self.id}")
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """Serializes a Pet into a dictionary"""
        order = {
            "id": self.id,
            "customer_id": self.customer_id,
            "address": self.address,
            "items": []
        }
        for item in self.items:
            order["items"].append(item.serialize())
        return order

    def deserialize(self, data):
        """
        Deserializes a Pet from a dictionary

        :param data: a dictionary of attributes
        :type data: dict

        :return: a reference to self
        :rtype: Pet

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
        except KeyError as error:
            raise DataValidationError("Invalid pet: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid pet: body of request contained bad or no data"
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
        """Returns all of the Pets in the database"""
        logger.info("Processing all Pets")
        return cls.query.all()

    @classmethod
    def find(cls, customer_order_id):
        """Finds a Pet by it's ID

        :param pet_id: the id of the Pet to find
        :type pet_id: int

        :return: an instance with the pet_id, or None if not found
        :rtype: Pet

        """
        logger.info("Processing lookup for id %s ...", customer_order_id)
        return cls.query.get(customer_order_id)

    @classmethod
    def find_or_404(cls, customer_order_id):
        """Find a CustomerOrder by it's id

        :param customer_order_id: the id of the CustomerOrder to find
        :type customer_order_id: int

        :return: an instance with the pet_id, or 404_NOT_FOUND if not found
        :rtype: Pet

        """
        logger.info("Processing lookup or 404 for id %s ...", customer_order_id)
        return cls.query.get_or_404(customer_order_id)

    def save(self):
        """
        Updates a order into the database
        """
        logger.info("Saving %s", self.id)
        db.session.commit()

    # @classmethod
    # def find_by_name(cls, name):
    #     """Returns all Pets with the given name

    #     :param name: the name of the Pets you want to match
    #     :type name: str

    #     :return: a collection of Pets with that name
    #     :rtype: list

    #     """
    #     logger.info("Processing name query for %s ...", name)
    #     return cls.query.filter(cls.name == name)

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
