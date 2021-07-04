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
Pet API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convinient to use this:
    nosetests --stop tests/test_service.py:TestPetServer
"""

import os
import logging
import unittest

# from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus
from service import status  # HTTP Status Codes
from service.models import db, init_db
from service.routes import app
from .factories import CustomerOrderFactory

# Disable all but ciritcal errors during normal test run
# uncomment for debugging failing tests
logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/orders"
CONTENT_TYPE_JSON = "application/json"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestPetServer(unittest.TestCase):
    """Pet Server Tests"""

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

    # def test_get_pet_list(self):
    #     """Get a list of Pets"""
    #     self._create_pets(5)
    #     resp = self.app.get(BASE_URL)
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     data = resp.get_json()
    #     self.assertEqual(len(data), 5)

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


    # def test_create_pet_no_data(self):
    #     """Create a Pet with missing data"""
    #     resp = self.app.post(BASE_URL, json={}, content_type=CONTENT_TYPE_JSON)
    #     self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_pet_no_content_type(self):
    #     """Create a Pet with no content type"""
    #     resp = self.app.post(BASE_URL)
    #     self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # def test_update_pet(self):
    #     """Update an existing Pet"""
    #     # create a pet to update
    #     test_pet = PetFactory()
    #     resp = self.app.post(
    #         BASE_URL, json=test_pet.serialize(), content_type=CONTENT_TYPE_JSON
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    #     # update the pet
    #     new_pet = resp.get_json()
    #     logging.debug(new_pet)
    #     new_pet["category"] = "unknown"
    #     resp = self.app.put(
    #         "/pets/{}".format(new_pet["id"]),
    #         json=new_pet,
    #         content_type=CONTENT_TYPE_JSON,
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     updated_pet = resp.get_json()
    #     self.assertEqual(updated_pet["category"], "unknown")

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

    # def test_query_pet_list_by_category(self):
    #     """Query Pets by Category"""
    #     pets = self._create_pets(10)
    #     test_category = pets[0].category
    #     category_pets = [pet for pet in pets if pet.category == test_category]
    #     resp = self.app.get(
    #         BASE_URL, query_string="category={}".format(quote_plus(test_category))
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     data = resp.get_json()
    #     self.assertEqual(len(data), len(category_pets))
    #     # check the data just to be sure
    #     for pet in data:
    #         self.assertEqual(pet["category"], test_category)

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
