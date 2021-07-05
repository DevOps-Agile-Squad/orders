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
Orders API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_service.py:TestCustomerOrderServer
"""

import os
import logging
import unittest

# from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus
from service import status  # HTTP Status Codes
from service.models import db, init_db, Item, CustomerOrder
from service.routes import app
from .factories import CustomerOrderFactory
from werkzeug.exceptions import NotFound

# Disable all but ciritcal errors during normal test run
# uncomment for debugging failing tests
# logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/orders"
CONTENT_TYPE_JSON = "application/json"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestCustomerOrderServer(unittest.TestCase):
    """Orders Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_orders(self, count):
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            test_order = CustomerOrderFactory()
            resp = self.app.post(
                BASE_URL, json=test_order.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test order"
            )
            new_order = resp.get_json()
            test_order.id = new_order["id"]
            orders.append(test_order)
        return orders

    # def test_index(self):
    #     """Test the Home Page"""
    #     resp = self.app.get("/")
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     data = resp.get_json()
    #     self.assertEqual(data["name"], "Order Demo REST API Service")

    def test_get_orders_list(self):
        """Get a list of orders"""
        self._create_orders(5)
        resp = self.app.get("/orders")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_order(self):
        """Get a single order"""
        # get the id of a order
        test_order = self._create_orders(1)[0]
        resp = self.app.get(
            "/orders/{}".format(test_order.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], test_order.customer_id)

    def test_get_order_not_found(self):
        """Get a order thats not found"""
        resp = self.app.get("/orderss/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order(self):
        """Create a new order"""
        test_order = CustomerOrderFactory()
        logging.debug(test_order)
        resp = self.app.post(
            BASE_URL, json=test_order.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_order = resp.get_json()
        self.assertEqual(new_order["customer_id"], test_order.customer_id, "cus_id do not match")
        self.assertEqual(
            new_order["address"], test_order.address, "address do not match"
        )

        # Check that the location header was correct
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_order = resp.get_json()
        self.assertEqual(new_order["customer_id"], test_order.customer_id, "cus_id do not match")
        self.assertEqual(
            new_order["address"], test_order.address, "address do not match"
        )

    def test_add_item(self):
        """Create a new item"""
        test_order = CustomerOrderFactory()
        logging.debug(test_order)
        resp = self.app.post(
            BASE_URL, json=test_order.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_order = resp.get_json()

        resp = self.app.post(
            "/orders/{}/items".format(new_order["id"]),
            json=Item(id=None, item_name='Egg', quantity=6,
                      price=1, order_id=new_order["id"]).serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_order_error(self):
        """Test that invalid content type are ignored."""
        resp = self.app.post(
            '/orders', data='Non JSON data type',
            content_type="application/x-www-form-urlencoded")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # def test_create_pet_no_data(self):
    #     """Create a Pet with missing data"""
    #     resp = self.app.post(BASE_URL, json={}, content_type=CONTENT_TYPE_JSON)
    #     self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_pet_no_content_type(self):
    #     """Create a Pet with no content type"""
    #     resp = self.app.post(BASE_URL)
    #     self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_order(self):
        """Update an existing CustomerOrder"""
        # create an order to update
        test_order = CustomerOrderFactory()
        resp = self.app.post(
            BASE_URL, json=test_order.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the order
        new_order = resp.get_json()
        logging.debug(new_order)
        new_order["address"] = "new"
        resp = self.app.put(
            "/orders/{}".format(new_order["id"]),
            json=new_order,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["address"], "new")

        test_order.id = 0
        resp = self.app.put(
            "/orders/{}".format(test_order.id),
            json=test_order.serialize(),
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertRaises(NotFound)



    def test_delete_order(self):
        """Delete a order"""
        test_order = self._create_orders(1)[0]
        resp = self.app.delete(
            "{0}/{1}".format(BASE_URL, test_order.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, test_order.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_item(self):
        """Delete an item"""
        test_orders = self._create_orders(2)
        test_order = test_orders[0]
        test_item = {"id": 2, "order_id": test_order.id, "quantity": 3, "price": 2.99, "item_name": "test item"}
        resp = self.app.post(
            f"/orders/{test_order.id}/items", 
            json=test_item,
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        returned_item = Item()
        returned_item.deserialize(resp.get_json())
        returned_item.id = resp.get_json()["item_id"]

        self.assertEqual(len(CustomerOrder.find(returned_item.order_id).items), 1)

        resp = self.app.delete(f"orders/{test_orders[1].id}/items/{returned_item.id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        
        resp = self.app.delete(f"/orders/{returned_item.order_id}/items/{returned_item.id}", content_type=CONTENT_TYPE_JSON)
        self.assertEqual(len(CustomerOrder.find(returned_item.order_id).items), 0)

        resp = self.app.delete("/orders/0/items/13", content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        
    # def test_query_orders_by_customer_id(self):
    #     """Query Orders by Customer Id"""
    #     orders = self._create_orders(10)
    #     test_customer_id = orders[0].customer_id
    #     customer_id_orders = [order for order in orders if order.customer_id == test_customer_id]
    #     resp = self.app.get(
    #         BASE_URL, query_string="customer_id={}".format(quote_plus(test_customer_id))
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     data = resp.get_json()
    #     self.assertEqual(len(data), len(customer_id_orders))
    #     check the data just to be sure
    #     for orders in data:
    #        self.assertEqual(orders["customer_id"], test_customer_id)

    # @patch('service.routes.Pet.find_by_name')
    # def test_bad_request(self, bad_request_mock):
    #     """ Test a Bad Request error from Find By Name """
    #     bad_request_mock.side_effect = DataValidationError()
    #     resp = self.app.get(BASE_URL, query_string='name=fido')
    #     self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # @patch('service.routes.Pet.find_by_name')
    # def test_mock_search_data(self, pet_find_mock):
    #     """ Test showing how to mock data """
    #     pet_find_mock.return_value = [MagicMock(serialize=lambda: {'name': 'fido'})]
    #     resp = self.app.get(BASE_URL, query_string='name=fido')
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
