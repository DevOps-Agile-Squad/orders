"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m

Source: https://github.com/nyu-devops/project-template/blob/master/tests/test_routes.py
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from flask_api import status  # HTTP Status Codes
from service.model import db, OrderBase 
from service.routes import app
from unittest.mock import MagicMock
from .factories import OrderFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/orders"
CONTENT_TYPE_JSON = "application/json"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
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
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()
    
    def _create_orders(self, count):
        """Factory method to create pets in bulk"""
        orders = []
        for _ in range(count):
            test_order = OrderFactory()
            resp = self.app.post(
                BASE_URL, json=test_order.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test pet"
            )
            new_order = resp.get_json()
            logging.debug(f"old id is {test_order.order_id}")
            logging.debug(f"new id is {new_order['order_id']}")
            test_order.order_id = new_order["order_id"]
            orders.append(test_order)
        return orders

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        """Test that the order is created"""
        test_order = OrderFactory()
        logging.debug(test_order.serialize())
        resp = self.app.post(BASE_URL, json=test_order.serialize(), content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, 201)


    def test_delete(self):
        test_order = self._create_orders(1)[0]

        resp = self.app.delete(
            f"/{BASE_URL}/{test_order.order_id}", content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
    
    # def test_create_order1(self):
    #     """Test that order is created."""
    #     def set_order_id(order):
    #         order.order_id = 1  # order_id is assigned by SQLAlchemy in real function.
    #     db.session.add = MagicMock(return_value=None, side_effect=set_order_id)
    #     db.session.commit = MagicMock(return_value=None)
    #     resp = self.app.post('/orders', json={
    #         "customer_id": 15,
    #         "address_line1": "123 Lost Road Apt 420",
    #         "city": "Jersey City",
    #         "state": "NJ",
    #         "zip_code": 12345})
    #     db.session.commit.assert_called()
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    
    def test_create_order_error(self):
        """Test that invalid content type are ignored."""
        resp = self.app.post(
            '/orders', data='Non JSON data type',
            content_type="application/x-www-form-urlencoded")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

