# Orders

The orders resource is a collection of order items where each item represents a product, its quantity, and its price. Since this is really a collection of order items, we will implement a subordinate REST API to place order items into the order collection (e.g., /orders/{id}/ items). We will also associate the order with a customer through its customer id.

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

## Contributing
Please assign yourself a user story from the top of "Sprint Backlog" and move it the "In Progress" column. Once you finish implementing the story on the local feature branch, push the branch and start a Pull Request. Please make sure there are no pending change requests and at least one person has approved the PR before merging. Please always use the "Squash and Merge" option

## License
[MIT](https://choosealicense.com/licenses/mit/)