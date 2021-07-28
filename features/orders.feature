Feature: The orders service back-end
    As an E-Commerce Store Owner
    I need a RESTful orders service
    So that I can manage customer orders

    Background:
        Given the following orders
            | id | customer_id | address     | status     |
            | 1  | 1           | 101 king st | Completed  |
            | 2  | 2           | 102 king st | Processing |
            | 3  | 3           | 103 king st | Processing |

        Given the following items
            | order_id_index | item_name | quantity | price |
            | 0              | keyboard  | 1        | 35    |
            | 0              | frisbee   | 2        | 10    |
            | 2              | kite      | 1        | 20    |

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Orders RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Create a new Order
        When I visit the "Home Page"
        And I set the "Customer_ID" to "4869"
        And I set the "Address" to "221B Baker Street"
        And I select "Processing" in the "Status" dropdown
        And I press the "Create" button
        Then I should see the message "Success"
        When I copy the "Order_ID" field
        And I press the "Clear" button
        Then the "Order_ID" field should be empty
        And the "Customer_ID" field should be empty
        And the "Address" field should be empty
        When I paste the "Order_ID" field
        And I press the "Retrieve" button
        Then I should see "4869" in the "Customer_ID" field
        And I should see "221B Baker Street" in the "Address" field
        And I should see "Processing" in the "Status" dropdown







