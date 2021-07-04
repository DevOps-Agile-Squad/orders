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

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    
    def test_create_order(self):
        """Test that order is created."""
        def set_order_id(order):
            order.order_id = 1  # order_id is assigned by SQLAlchemy in real function.
        db.session.add = MagicMock(return_value=None, side_effect=set_order_id)
        db.session.commit = MagicMock(return_value=None)
        resp = self.app.post('/orders', json={
            "customer_id": 15,
            "address_line1": "123 Lost Road Apt 420",
            "city": "Jersey City",
            "state": "NJ",
            "zip_code": 12345})
        db.session.commit.assert_called()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    
    def test_create_order_error(self):
        """Test that invalid content type are ignored."""
        resp = self.app.post(
            '/orders', data='Non JSON data type',
            content_type="application/x-www-form-urlencoded")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

