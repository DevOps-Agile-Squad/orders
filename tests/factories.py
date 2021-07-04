import factory
from faker import Faker
from factory.fuzzy import FuzzyChoice
from service.model import CustomerOrder

faker = Faker()

class OrderFactory(factory.Factory): 
    class Meta:
        model = CustomerOrder
    
    order_id = factory.Sequence(lambda n:n)
    customer_id = factory.Sequence(lambda n:n)
    address_line1 = faker.street_address()
    address_line2 = "Nonee"
    city = faker.city()
    state = faker.country_code()
    zip_code = factory.Sequence(lambda n:n)
