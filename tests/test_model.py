"""
Test cases for YourResourceModel Model

Source: https://github.com/nyu-devops/project-template/blob/master/tests/test_models.py
"""
import logging
import unittest
import os
from service.model import OrderBase, DataValidationError, db, CustomerOrder
from unittest.mock import MagicMock

######################################################################
#  ORDER MODEL   TEST   CASES
######################################################################
class TestOrderModel(unittest.TestCase):
    """ Test Cases for YourResourceModel Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        pass

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        pass

    def tearDown(self):
        """ This runs after each test """
        pass

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
    #  T E S T   C A S E S
    ######################################################################

    def test_serialize(self):
        """ Test serialization of CustomerOrder. """
        test_order = self.MakeOrder()
        self.assertDictEqual(test_order.serialize(), { 
            'order_id': 1,
            'customer_id': 2,
            'address_line1': '123 Some Street',
            'address_line2': 'Apt 1',
            'city': 'Jersey City',
            'state': 'NJ',
            'zip_code': 12345})
        self.assertEqual(str(test_order), '{order_id: %d, customer_id: %d}' % (1, 2))
    
    def test_deserialize(self):
        expected_order = self.MakeOrder()
        test_order = CustomerOrder()
        # Test that deserialize can deserialize serialized order.
        test_order.deserialize(expected_order.serialize())
        self.assertEqual(str(test_order), '{order_id: None, customer_id: %d}' % (2))
        self.assertEqual(expected_order, test_order)
    
    def test_deserialize_error(self):
        expected_order = self.MakeOrder()
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
        test_order = self.MakeOrder()
        test_order.create()
        db.session.add.assert_called_with(test_order)
        db.session.commit.assert_called()



