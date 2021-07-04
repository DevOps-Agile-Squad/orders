"""
Test cases for YourResourceModel Model

Source: https://github.com/nyu-devops/project-template/blob/master/tests/test_models.py
"""
import logging
import unittest
import os
from service.model import OrderBase, DataValidationError, db, CustomerOrder, Item
from unittest.mock import MagicMock
from service import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

def MakeItem(item_id=1, item_name='Egg', quantity=6, price=1, order_id=10):
    """Create and item for Order."""
    return Item(item_id=item_id, item_name=item_name, quantity=quantity,
        price=price, order_id=order_id)

def MakeOrder(order_id=1, customer_id=2, address_line1='123 Some Street',
                address_line2='Apt 1', city='Jersey City', state='NJ',
                zip_code=12345, items=[]):
    """Creates a CustomerOrder object."""
    return CustomerOrder(order_id=order_id,
        customer_id=customer_id,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        zip_code=zip_code,
        items=items)
        
######################################################################
#  I T E M   M O D E L    T E S T
######################################################################
class TestItemModel(unittest.TestCase):

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_serialize(self):
        test_item = MakeItem()
        self.assertDictEqual(test_item.serialize(), { 
            'order_id': 10,
            'item_id': 1,
            'quantity': 6,
            'price': 1,
            'item_name': 'Egg',})
        self.assertEqual(str(test_item),
            '{item_id: %d, order_id: %d, item_name: %s}' % (1, 10, 'Egg'))       

    def test_deserialize(self):
        expected_item = MakeItem()
        test_item = Item()
        # Test that deserialize can deserialize serialized order.
        test_item.deserialize(expected_item.serialize())
        self.assertEqual(str(test_item),
            '{item_id: None, order_id: %d, item_name: %s}' % (10, 'Egg'))  
        self.assertEqual(expected_item, test_item)

    def test_deserialize_error(self):
        expected_item = MakeItem()
        expected_item.quantity = None
        expected_item.id = None
        test_item = Item()
        data = expected_item.serialize()
        # Test that quantity is not required.
        test_item.deserialize(data)
        self.assertEqual(expected_item, test_item)

        # Test that required keys must be present for deserialize to succeed.
        test_item = Item()
        del data['order_id']
        with self.assertRaises(DataValidationError) as context:
            test_item.deserialize(data)

        # Test that dictionary type is passed as data
        with self.assertRaises(DataValidationError) as context:
            test_item.deserialize("some invalid serialized string")


    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        OrderBase.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    def MakeOrder(self):
        """Creates a CustomerOrder object."""
        customer_order = CustomerOrder()
        customer_order.order_id = 1
        customer_order.customer_id = 2
        customer_order.address_line1 = '123 Some Street'
        customer_order.address_line2 = 'Apt 1'
        customer_order.city = 'Jersey City'
        customer_order.state = 'NJ'
        customer_order.zip_code = 12345
        return customer_order


######################################################################
#  C U S T O M E R    O R D E R    M O D E L    T E S T
######################################################################
class TestCustomerOrderModel(unittest.TestCase):
    """ Test Cases for YourResourceModel Model """
    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        OrderBase.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_serialize(self):
        """ Test serialization of CustomerOrder. """
        test_order = MakeOrder()
        self.assertDictEqual(test_order.serialize(), { 
            'order_id': 1,
            'customer_id': 2,
            'address_line1': '123 Some Street',
            'address_line2': 'Apt 1',
            'city': 'Jersey City',
            'state': 'NJ',
            'zip_code': 12345,
            'items': []})
        self.assertEqual(str(test_order), '{order_id: %d, customer_id: %d}' % (1, 2))

        # Test serialize with items.
        test_order = MakeOrder(items=[MakeItem()])
        self.assertDictEqual(test_order.serialize(), { 
            'order_id': 1,
            'customer_id': 2,
            'address_line1': '123 Some Street',
            'address_line2': 'Apt 1',
            'city': 'Jersey City',
            'state': 'NJ',
            'zip_code': 12345,
            'items': [{ 
                'order_id': 10,
                'item_id': 1,
                'quantity': 6,
                'price': 1,
                'item_name': 'Egg'}]})
    
    def test_deserialize(self):
        expected_order = MakeOrder()
        test_order = CustomerOrder()
        # Test that deserialize can deserialize serialized order.
        test_order.deserialize(expected_order.serialize())
        self.assertEqual(str(test_order), '{order_id: None, customer_id: %d}' % (2))
        self.assertEqual(expected_order, test_order)

        # Test deserialize for Order containing items.
        expected_order = MakeOrder(items=[MakeItem()])
        test_order = CustomerOrder()
        test_order.deserialize(expected_order.serialize())
        self.assertEqual(expected_order, test_order)
    
    def test_deserialize_error(self):
        expected_order = MakeOrder()
        expected_order.address_line2 = None
        test_order = CustomerOrder()
        data = expected_order.serialize()
        # Test that address_line2 is optional.
        test_order.deserialize(data)
        self.assertEqual(expected_order, test_order)

        # Test that required keys must be present for deserialize to succeed.
        test_order = CustomerOrder()
        del data['customer_id']
        with self.assertRaises(DataValidationError) as context:
            test_order.deserialize(data)

        # Test that dictionary type is passed as data
        with self.assertRaises(DataValidationError) as context:
            test_order.deserialize("some invalid serialized string")

    def test_create(self):
        db.session.add = MagicMock(return_value=None)
        db.session.commit = MagicMock(return_value=None)
        test_order = MakeOrder()
        test_order.create()
        db.session.add.assert_called_with(test_order)
        db.session.commit.assert_called()

    def test_save(self):
        db.session.commit = MagicMock(return_value=None)
        test_order = MakeOrder(items=[MakeItem()])
        test_order.save()
        db.session.commit.assert_called()



