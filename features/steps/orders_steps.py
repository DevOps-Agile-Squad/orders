import json
import requests
from behave import *
from compare import expect, ensure

"""
Order Steps
Steps file for Order.feature
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""


@given(u'the following orders')
def step_impl(context):
    """ Delete all Orders and load new ones """
    context.order_ids = list()
    headers = {'Content-Type': 'application/json'}
    # list all of the orders and delete them one by one
    context.resp = requests.get(context.base_url + '/orders', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for order in context.resp.json():
        context.resp = requests.delete(
            context.base_url + '/orders/' + str(order["id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)

    # load the database with new orders
    create_url = context.base_url + '/orders'
    for row in context.table:
        data = {
            "customer_id": int(row['customer_id']),
            "address": row['address'],
            "status": row['status'],
            "items": list()
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        context.order_ids.append(context.resp.json()["id"])
        expect(context.resp.status_code).to_equal(201)
