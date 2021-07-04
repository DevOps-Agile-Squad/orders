"""
Models for OrderModel.

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from abc import ABCMeta, abstractmethod

logger = logging.getLogger('flask.app')

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class OrderBase(object):
    """Base class for Order Model."""
    app = None

    @property
    @abstractmethod
    def id(self):
        """Primary Key/Id field for Order base."""
        pass

    @id.setter
    @abstractmethod
    def id(self, value):
        """Setter for Key/Id field for Order base."""
        pass

    def create(self):
        """Creates a new row in the database."""
        logger.info('Creating Order')
        self.id = None # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a Account to the database
        """
        logger.info("Saving %s", self.id)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a order by it's id """
        logger.info('Processing lookup or 404 for id %s ...', by_id)
        return cls.query.get_or_404(by_id)

######################################################################
#  I T E M   M O D E L
######################################################################
class Item(db.Model, OrderBase):
    """
    Class that represents an Item
    """

    # Table Schema
    item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('customer_order.order_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=True)  # If null quantity will be treated as 1.
    price = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.String(120), nullable=False) # e.g., ball, balloon, etc.

    @property
    def id(self):
        return self.item_id
    
    @id.setter
    def id(self, value):
        self.item_id = value

    def __str__(self):
        return '{item_id: %s, order_id: %d, item_name: %s}' % (
            str(self.item_id), self.order_id, self.item_name)
    
    def __eq__(self, other):
        return (self.id == other.id) or ((self.id is None or other.id is None) and
            (self.item_name == other.item_name) and
            (self.order_id == other.order_id) and
            (self.quantity == other.quantity) and
            (self.price == other.price))

    def serialize(self):
        """ Serializes a Address into a dictionary """
        return {
            "item_id": self.item_id,
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


#############################################################
# C U S T O M E R    O R D E R    M O D E L
#############################################################
class CustomerOrder(db.Model, OrderBase):
    """
    Class that stores orders for customer.
    """
    app = None

    # Table Schema
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    address_line1 = db.Column(db.String(256), nullable=False)
    address_line2 = db.Column(db.String(256), nullable=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip_code = db.Column(db.Integer, nullable=False)
    items = db.relationship('Item', backref='order', lazy=True)
    
    @property
    def id(self):
        return self.order_id

    @id.setter
    def id(self, value):
        self.order_id = value

    def __str__(self):
        return '{order_id: %s, customer_id: %d}' % (
            str(self.order_id), self.customer_id)

    def __eq__(self, other):
        return ((self.id == other.id or self.id is None or other.id is None) and
            (self.customer_id == other.customer_id) and
            (self.address_line1 == other.address_line1) and
            (self.address_line2 == other.address_line2) and
            (self.city == other.city) and
            (self.state == other.state) and
            (self.zip_code == other.zip_code) and
            (self.items == other.items))

    def serialize(self):
        """ Serializes customer to order mapping. """
        order = {
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'items': []
        }
        for item in self.items:
            order['items'].append(item.serialize())
        return order

    
    def deserialize(self, data):
        """
        Deserializes customer to order mappings.

        Args:
            data (dict): resource data as dictionary.
        
        Returns:
            Object of type CustomerOrder.
        """
        try:
            self.customer_id = data['customer_id']
            self.address_line1 = data['address_line1']
            # Address line 2 is optional.
            if 'address_line2' in data:
                self.address_line2 = data['address_line2']
            self.city = data['city']
            self.state = data['state']
            self.zip_code = data['zip_code']
            self.items = []
            for item_str in data.get('items', []):
                item = Item()
                item.deserialize(item_str)
                self.items.append(item)
        except KeyError as error:
            raise DataValidationError(
                'Invalid CustomerOrder: missing ' + str(error))
        except TypeError as error:
            raise DataValidationError(
                'Invalid CustomerOrder: bad data type.')
        return self