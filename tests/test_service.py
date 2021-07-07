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
from werkzeug.exceptions import NotFound
from service import status  # HTTP Status Codes
from service.models import db, init_db, Item, CustomerOrder, Status
from service.routes import app
from .factories import CustomerOrderFactory

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
class TestCustomerOrderServer(unittest.TestCase):  # pylint: disable=too-many-public-methods
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

    def test_index(self):
        """Test the Home Page"""
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Orders Demo REST API Service")

    def test_get_orders_list(self):
        """Get a list of orders"""
        self._create_orders(5)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_order(self):
        """Get a single order"""
        # get the id of a order
        test_order = self._create_orders(1)[0]
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, test_order.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], test_order.customer_id)

    def test_get_order_not_found(self):
        """Get a order thats not found"""
        resp = self.app.get("{}/0".format(BASE_URL))
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
        self.assertEqual(new_order["customer_id"],
                         test_order.customer_id, "cus_id do not match")
        self.assertEqual(
            new_order["address"], test_order.address, "address do not match"
        )

        # Check that the location header was correct
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_order = resp.get_json()
        self.assertEqual(new_order["customer_id"],
                         test_order.customer_id, "cus_id do not match")
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
            "{0}/{1}/items".format(BASE_URL, new_order["id"]),
            json=Item(id=None, item_name='Egg', quantity=6,
                      price=1, order_id=new_order["id"]).serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_order_error(self):
        """Test that invalid content type are ignored."""
        resp = self.app.post(
            BASE_URL, data='Non JSON data type',
            content_type="application/x-www-form-urlencoded")
        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_order_no_data(self):
        """Create an order with missing data"""
        resp = self.app.post(BASE_URL, json={}, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_no_content_type(self):
        """Create an Order with no content type"""
        resp = self.app.post(BASE_URL)
        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

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
            "{0}/{1}".format(BASE_URL, new_order["id"]),
            json=new_order,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["address"], "new")

        test_order.id = 0
        resp = self.app.put(
            "{0}/{1}".format(BASE_URL, test_order.id),
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
        test_item = {"id": 2,
                     "order_id": test_order.id,
                     "quantity": 3,
                     "price": 2.99,
                     "item_name": "test item"}
        resp = self.app.post(
            f"{BASE_URL}/{test_order.id}/items",
            json=test_item,
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        returned_item = Item()
        returned_item.deserialize(resp.get_json())
        returned_item.id = resp.get_json()["item_id"]

        self.assertEqual(len(CustomerOrder.find(
            returned_item.order_id).items), 1)

        resp = self.app.delete(
            f"orders/{test_orders[1].id}/items/{returned_item.id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        resp = self.app.delete(f"{BASE_URL}/{returned_item.order_id}/items/{returned_item.id}",
                               content_type=CONTENT_TYPE_JSON)
        self.assertEqual(len(CustomerOrder.find(
            returned_item.order_id).items), 0)

        resp = self.app.delete(
            f"{BASE_URL}/0/items/13", content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_orders_by_customer_id(self):
        """Query Orders by Customer Id"""
        orders = self._create_orders(10)
        test_customer_id = orders[0].customer_id
        customer_id_orders = [
            order for order in orders if order.customer_id == test_customer_id]
        resp = self.app.get(
            BASE_URL, query_string="customer_id={}".format(test_customer_id)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(customer_id_orders))
        # check the data just to be sure
        for orders in data:
            self.assertEqual(orders["customer_id"], test_customer_id)

    def test_query_orders_by_item(self):
        """Query Orders by item name"""
        orders = self._create_orders(3)
        order_1 = orders[0]
        order_2 = orders[1]
        order_3 = orders[2]
        test_item_1 = {"id": 1, "order_id": order_1.id,
                       "quantity": 3, "price": 4, "item_name": "Foo"}
        test_item_2 = {"id": 2, "order_id": order_2.id,
                       "quantity": 3, "price": 4, "item_name": "Foo"}
        test_item_3 = {"id": 1, "order_id": order_1.id,
                       "quantity": 1, "price": 5, "item_name": "Bar"}
        test_item_4 = {"id": 1, "order_id": order_3.id,
                       "quantity": 2, "price": 5, "item_name": "Bar"}

        # add Foo to order_1
        resp = self.app.post(
            f"{BASE_URL}/{order_1.id}/items",
            json=test_item_1,
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # add Bar to order_1
        resp = self.app.post(
            f"{BASE_URL}/{order_1.id}/items",
            json=test_item_3,
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # add Foo to order_2
        resp = self.app.post(
            f"{BASE_URL}/{order_2.id}/items",
            json=test_item_2,
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # add Bar to order_3
        resp = self.app.post(
            f"{BASE_URL}/{order_3.id}/items",
            json=test_item_4,
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # test query Foo
        resp = self.app.get(
            BASE_URL, query_string="item={}".format(quote_plus("Foo"))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_cancel_order_not_found(self):
        """Cancelling order not exists"""
        resp = self.app.post(f"{BASE_URL}/1/cancel")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_order_not_allowed(self):
        """Cancelling order with invalid status (Completed/Returned)"""

        # test cancel completed order
        completed_order = CustomerOrderFactory()
        completed_order.status = Status.Completed  # change status to Completed
        resp = self.app.post(
            BASE_URL, json=completed_order.serialize(), content_type=CONTENT_TYPE_JSON
        )
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["status"], Status.Completed.name)
        logging.debug(completed_order)
        # try cancelling a completed order
        completed_order.id = data["id"]
        resp = self.app.post(f"{BASE_URL}/{completed_order.id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # try get the order back and check for status
        resp = self.app.get(f"{BASE_URL}/{completed_order.id}")
        data = resp.get_json()
        logging.debug(completed_order)
        self.assertEqual(data['status'], Status.Completed.name)

        # test cancel returned order
        returned_order = CustomerOrderFactory()
        returned_order.status = Status.Returned  # change status to Returned
        resp = self.app.post(
            BASE_URL, json=returned_order.serialize(), content_type=CONTENT_TYPE_JSON
        )
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["status"], Status.Returned.name)
        logging.debug(returned_order)
        # try cancelling a returned order
        returned_order.id = data["id"]
        resp = self.app.post(f"{BASE_URL}/{returned_order.id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # try get the order back and check for status
        resp = self.app.get(f"{BASE_URL}/{returned_order.id}")
        data = resp.get_json()
        logging.debug(returned_order)
        self.assertEqual(data['status'], Status.Returned.name)

    def test_cancel_order_already_cancelled(self):
        """Cancelling order that is already cancelled"""
        # test cancel returned order
        cancelled_order = CustomerOrderFactory()
        cancelled_order.status = Status.Cancelled  # change status to Cancelled
        resp = self.app.post(
            BASE_URL, json=cancelled_order.serialize(), content_type=CONTENT_TYPE_JSON
        )
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["status"], Status.Cancelled.name)
        logging.debug(cancelled_order)
        # try cancelling a cancelled order
        cancelled_order.id = data["id"]
        resp = self.app.post(f"{BASE_URL}/{cancelled_order.id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # try get the order back and check for status
        resp = self.app.get(f"{BASE_URL}/{cancelled_order.id}")
        data = resp.get_json()
        logging.debug(cancelled_order)
        self.assertEqual(data['status'], Status.Cancelled.name)

    def test_cancel_order(self):
        """Cancelling order"""
        # test cancel received order
        received_order = CustomerOrderFactory()
        received_order.status = Status.Received  # change status to Received
        resp = self.app.post(
            BASE_URL, json=received_order.serialize(), content_type=CONTENT_TYPE_JSON
        )
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["status"], Status.Received.name)
        logging.debug(received_order)
        # try cancelling a received order
        received_order.id = data["id"]
        resp = self.app.post(f"{BASE_URL}/{received_order.id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # try get the order back and check for status
        resp = self.app.get(f"{BASE_URL}/{received_order.id}")
        data = resp.get_json()
        logging.debug(received_order)
        self.assertEqual(data['status'], Status.Cancelled.name)

    def test_method_not_allowed(self):
        """Testing unsupported request type"""
        resp = self.app.post(f'{BASE_URL}/42')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

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
