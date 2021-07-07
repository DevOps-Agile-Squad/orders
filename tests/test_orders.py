# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
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
Test cases for Order Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_orders.py:TestCustomerOrderModel

"""
import os
import logging
import unittest
from werkzeug.exceptions import NotFound
from service.models import CustomerOrder, DataValidationError, db, Item, Status
from service import app
from .factories import CustomerOrderFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)

TEST_ADDRESS = "random address"
TEST_ITEM = "Egg"

def MakeItem(id=1, item_name=TEST_ITEM, quantity=6, price=1, order_id=10):
    """Create and item for Order."""
    return Item(id=id, item_name=item_name, quantity=quantity,
        price=price, order_id=order_id)

######################################################################
#  O R D E R   M O D E L   T E S T   C A S E S
######################################################################
class TestCustomerOrderModel(unittest.TestCase):
    """Test Cases for Order Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        CustomerOrder.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_customer_order(self):
        """Create an order and assert that it exists"""
        order = CustomerOrder(customer_id=13, address=TEST_ADDRESS, items=[ MakeItem() ], status=Status.Received)
        self.assertTrue(order != None)
        self.assertEqual(order.id, None)
        self.assertEqual(order.customer_id, 13)
        self.assertEqual(order.address, TEST_ADDRESS)
        self.assertEqual(order.status, Status.Received)
        order = CustomerOrder(customer_id=15, address=TEST_ADDRESS, items=[ MakeItem() ], status=Status.Completed)
        self.assertEqual(order.customer_id, 15)
        self.assertEqual(order.status, Status.Completed)

    def test_add_a_customer_order(self):
        """Create an order and add it to the database"""
        orderss = CustomerOrder.all()
        self.assertEqual(orderss, [])
        order = CustomerOrder(customer_id=13, address=TEST_ADDRESS, items=[ MakeItem() ], status=Status.Received)
        self.assertTrue(order != None)
        self.assertEqual(order.id, None)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(order.id, 1)
        orders = CustomerOrder.all()
        self.assertEqual(len(orders), 1)

    def test_update_a_customer_order(self):
        """Update a CustomerOrder"""
        order = CustomerOrderFactory()
        logging.debug(order)
        order.create()
        logging.debug(order)
        self.assertEqual(order.id, 1)
        # Change it an save it
        order.address = "new"
        original_id = order.id
        order.status = Status.Processing
        order.update()
        self.assertEqual(order.id, original_id)
        self.assertEqual(order.address, "new")
        self.assertEqual(order.status, Status.Processing)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        orders = CustomerOrder.all()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].id, 1)
        self.assertEqual(orders[0].address, "new")
        self.assertEqual(orders[0].status, Status.Processing)

    def test_delete_a_customer_order(self):
        """Delete a customer order"""
        order = CustomerOrderFactory()
        order.create()
        self.assertEqual(len(CustomerOrder.all()), 1)
        # delete the order and make sure it isn't in the database
        order.delete()
        self.assertEqual(len(CustomerOrder.all()), 0)

    def test_serialize_deserialize_item(self):
        """Test serialization of an item."""
        test_item = Item()
        expected_item = MakeItem(id=1)
        test_item.deserialize(expected_item.serialize())
        self.assertEqual(expected_item, test_item)

    def test_deserialize_item_error(self):
        """Test serialization of an item."""
        test_item = Item()
        self.assertRaises(DataValidationError, test_item.deserialize, {"id": 1, "item_name": TEST_ITEM})
        self.assertRaises(DataValidationError, test_item.deserialize, "Not a dictionary")

    def test_serialize_a_customer_order(self):
        """Test serialization of a customer order"""
        order = CustomerOrderFactory()
        data = order.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], order.id)
        self.assertIn("customer_id", data)
        self.assertEqual(data["customer_id"], order.customer_id)
        self.assertIn("address", data)
        self.assertEqual(data["address"], order.address)
        self.assertIn("status", data)
        self.assertEqual(data["status"], order.status.name)

    def test_deserialize_a_customer_order(self):
        """Test deserialization of a customer order"""
        data = {
            "id": 1,
            "customer_id": 12,
            "address": TEST_ADDRESS,
            "items": [{
                "id": 1,
                "price": 1,
                "item_name": TEST_ITEM,
                "quantity": 6,
                "order_id": 10
            }],
            "status": "Completed",
        }
        order = CustomerOrder()
        order.deserialize(data)
        self.assertNotEqual(order, None)
        self.assertEqual(order.id, None)
        self.assertEqual(order.customer_id, 12)
        self.assertEqual(order.address, TEST_ADDRESS)
        self.assertListEqual(order.items, [MakeItem(id=None)])
        self.assertEqual(order.status, Status.Completed)

    def test_deserialize_missing_data(self):
        """Test deserialization of a customer order with missing data"""
        data = {"id": 1}
        order = CustomerOrder()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        data = "this is not a dictionary"
        order = CustomerOrder()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_find_customer_order(self):
        """Find an Order by ID"""
        orders = CustomerOrderFactory.create_batch(3)
        for order in orders:
            order.create()
        logging.debug(orders)
        # make sure they got saved
        self.assertEqual(len(order.all()), 3)
        # find the 2nd order in the list
        order = CustomerOrder.find(orders[1].id)
        self.assertIsNot(order, None)
        self.assertEqual(order.id, orders[1].id)
        self.assertEqual(order.customer_id, orders[1].customer_id)
        self.assertEqual(order.address, orders[1].address)

    def test_find_by_customer_id(self):
        """Find orders by Customer Id"""
        CustomerOrder(customer_id=1, address=TEST_ADDRESS, items=[MakeItem(id=None)]).create()
        CustomerOrder(customer_id=1, address=TEST_ADDRESS, items=[MakeItem(id=None)]).create()
        CustomerOrder(customer_id=2, address=TEST_ADDRESS, items=[MakeItem(id=None)]).create()
        orders = CustomerOrder.find_by_customer_id(1)
        order_list = [order for order in orders]
        self.assertEqual(len(order_list), 2)
        self.assertEqual(orders[0].customer_id, 1)
        self.assertEqual(orders[1].customer_id, 1)

    def test_find_by_including_item(self):
        """Find orders by Including Item"""
        CustomerOrder(customer_id=1, address=TEST_ADDRESS, items=[MakeItem()]).create()
        orders = CustomerOrder.find_by_including_item(TEST_ITEM)
        order_list = [order for order in orders]
        self.assertEqual(len(order_list), 1)
        self.assertEqual(orders[0].customer_id, 1)
        self.assertEqual(orders[0].address, TEST_ADDRESS)

    # def test_find_by_availability(self):
    #     """Find Pets by Availability"""
    #     Pet(name="fido", category="dog", available=True).create()
    #     Pet(name="kitty", category="cat", available=False).create()
    #     Pet(name="fifi", category="dog", available=True).create()
    #     pets = Pet.find_by_availability(False)
    #     pet_list = [pet for pet in pets]
    #     self.assertEqual(len(pet_list), 1)
    #     self.assertEqual(pets[0].name, "kitty")
    #     self.assertEqual(pets[0].category, "cat")
    #     pets = Pet.find_by_availability(True)
    #     pet_list = [pet for pet in pets]
    #     self.assertEqual(len(pet_list), 2)

    # def test_find_by_gender(self):
    #     """Find Pets by Gender"""
    #     Pet(name="fido", category="dog", available=True, gender=Gender.Male).create()
    #     Pet(
    #         name="kitty", category="cat", available=False, gender=Gender.Female
    #     ).create()
    #     Pet(name="fifi", category="dog", available=True, gender=Gender.Male).create()
    #     pets = Pet.find_by_gender(Gender.Female)
    #     pet_list = [pet for pet in pets]
    #     self.assertEqual(len(pet_list), 1)
    #     self.assertEqual(pets[0].name, "kitty")
    #     self.assertEqual(pets[0].category, "cat")
    #     pets = Pet.find_by_gender(Gender.Male)
    #     pet_list = [pet for pet in pets]
    #     self.assertEqual(len(pet_list), 2)

    # def test_find_or_404_found(self):
    #     """Find or return 404 found"""
    #     pets = PetFactory.create_batch(3)
    #     for pet in pets:
    #         pet.create()

    #     pet = Pet.find_or_404(pets[1].id)
    #     self.assertIsNot(pet, None)
    #     self.assertEqual(pet.id, pets[1].id)
    #     self.assertEqual(pet.name, pets[1].name)
    #     self.assertEqual(pet.available, pets[1].available)

    # def test_find_or_404_not_found(self):
    #     """Find or return 404 NOT found"""
    #     self.assertRaises(NotFound, Pet.find_or_404, 0)
