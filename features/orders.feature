Feature: The orders service back-end
    As an E-Commerce Store Owner  
    I need a RESTful orders service
    So that I can manage customer orders 

Background: 
    Given the following orders
        | customer_id    | address         | status           | 
        | 2002           | 101 king st     | Completed        |       
        | 2334           | 102 king st     | Processing       |       
        | 7442           | 103 king st     | Processing       | 

    Given the following items
        | order_id_index    | item_name       | quantity       | price       | 
        | 0                 | keyboard        | 1              | 35          |
        | 0                 | frisbee         | 2              | 10          |
        | 2                 | kite            | 1              | 20          |    

Scenario: The server is running 
    When I visit the "Home Page"
    Then I should see "Orders RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Delete an Order   
    When I visit the "Home Page"
    And I press the "List" button
    Then I should see the message "Success"
    And I should not see "2003" in the results
    When I set the "Customer_ID" to "2003"
    When I set the "Address" to "104"
    And I press the "Create" button
    Then I should see the message "Success"
    When I press the "List" button
    Then I should see the message "Success"
    And I should see "2003" in the results
    When I press the "Delete" button
    Then I should see the message "Order has been Deleted!"
    When I press the "List" button
    Then I should see the message "Success"
    And I should not see "2003" in the results

Scenario: Update a Pet
    When I visit the "Home Page"
    And I set the "Customer_ID" to "2002"
    And I press the "Search" button
    Then I should see "101 king st" in the "Address" field
    And I should see "Completed" in the "Status" dropdown
    When I change "Address" to "106 king st"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Order_Id" field
    And I press the "Clear" button
    And I paste the "Order_Id" field
    And I press the "Retrieve" button
    Then I should see "106 king st" in the "Address" field
    When I press the "Clear" button
    And I press the "List" button
    Then I should see "106 king st" in the results
    Then I should not see "101 king st" in the results
    





