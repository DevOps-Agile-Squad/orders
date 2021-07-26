Feature: The orders service back-end
    As an E-Commerce Store Owner  
    I need a RESTful orders service
    So that I can manage customer orders 

Background: 
    Given the following orders
        | id         | customer_id | address         | status           | 
        | 1          | 1           | 101 king st     | Completed        |         
        | 2          | 2           | 102 king st     | Processing       |       
        | 3          | 3           | 103 king st     | Processing       |       

Scenario: The server is running 
    When I visit the "Home Page"
    Then I should see "Orders RESTful Service" in the title
    And I should not see "404 Not Found"








