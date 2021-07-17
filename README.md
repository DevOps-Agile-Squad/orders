# Orders

[![Build Status](https://travis-ci.com/DevOps-Agile-Squad/orders.svg?branch=main)](https://travis-ci.com/DevOps-Agile-Squad/orders)
[![codecov](https://codecov.io/gh/DevOps-Agile-Squad/orders/branch/main/graph/badge.svg?token=vAH0NcHpnM)](https://codecov.io/gh/DevOps-Agile-Squad/orders)

The orders resource is a collection of order items where each item represents a product, its quantity, and its price. Since this is really a collection of order items, we will implement a subordinate REST API to place order items into the order collection (e.g., /orders/{id}/ items). We will also associate the order with a customer through its customer id.

Order API

- /orders : This is the API to create an empty order. This will create an order for customer. The order has following fields:
  customer_id, address_line1, address_line2, city, state, zip_code.

- /orders/{id}/items : This is the API to create an item inside an order. Items have following field:
  quantity, price, item_name

## Installation

Simply clone this repository for now.

## Usage

Use the provided `Vagrantfile` to start a virtual machine, and start the server using the `Procfile`

```bash
vagrant up
vagrant ssh
cd /vagrant/
source .env
honcho start
```

The server should be visible on your local machine at `http://0.0.0.0:5000`

## Endpoints

- `GET /orders` - returns a list of all of the orders. Takes `customer_id` and `item` for queries.
- `GET /orders/<int:order_id>` - returns an order with the id of `order_id` or throws a `NotFound` exception if it doesn't exist
- `POST /orders` - adds an order and returns the added order
- `PUT /orders/<int:order_id>` - update the order with id of `order_id` or throws a `NotFound` exception if it doesn't exist
- `POST /orders/<int:order_id>/items` - adds an item to the order with id of `order_id` and return the added item or `404` if the order doesn't exist
- `DELETE /orders/<int:order_id>` - deletes the order with id of `order_id` if it exists and returns a `204` regardless of whether an actually deletion was performed
- `DELETE /orders/<int:order_id>/items/<int:item_id>` - deletes the item with id of `item_id` in the order with id of `order_id`. It returns a `404` if either the order or the item doesn't exist.
- `POST /orders/<int:order_id>/cancel` - cancels the order with id of `order_id`. Returns `200` for successful cancelling, returns `404` for orders not exist, returns `400` if the order in status `Completed/Returned`.

## Testing

To run unit tests with coverage: run `nosetests` after logging into the VM and navigating to `/vagrant/`

## Contributing

Please assign yourself a user story from the top of "Sprint Backlog" and move it the "In Progress" column. Once you finish implementing the story on the local feature branch, push the branch and start a Pull Request. Please make sure there are no pending change requests and at least one person has approved the PR before merging. Please always use the "Squash and Merge" option

## License

[MIT](https://choosealicense.com/licenses/mit/)
