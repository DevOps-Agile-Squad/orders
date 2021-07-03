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
from service.model import db
from service.routes import app
from unittest.mock import MagicMock

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

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
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        pass

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

