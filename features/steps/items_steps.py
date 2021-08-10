import json
import requests
from behave import *
from compare import expect, ensure


@given(u'the following items')
def step_impl(context):
    """ create new items """
    headers = {'Content-Type': 'application/json'}
    for row in context.table:
        order_id = context.order_ids[int(row["order_id_index"])]
        create_url = context.base_url + "/orders/{}/items".format(order_id)
        data = {
            "order_id": order_id,
            "item_name": row['item_name'],
            "quantity": int(row['quantity']),
            "price": float(row["price"])
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
    context.order_ids = list()
