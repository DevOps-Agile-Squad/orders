Feature: The orders service back-end
    As an E-Commerce Store Owner  
    I need a RESTful orders service
    So that I can manage customer orders 

Background: 
    Given the following orders
        | customer_id | address         | status           | 
        | 1           | 101 king st     | Completed        |         
        | 2           | 102 king st     | Processing       |       
        | 3           | 103 king st     | Processing       |   

    Given the following items
        | order_id_index    | item_name       | quantity       | price       | 
        | 0                 | keyboard        | 1              | 35          |
        | 0                 | frisbee         | 2              | 10          |
        | 2                 | kite            | 1              | 20          |    

Scenario: The server is running 
    When I visit the "Home Page"
    Then I should see "Orders RESTful Service" in the title
    And I should not see "404 Not Found"
