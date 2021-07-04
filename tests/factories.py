# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from service.models import CustomerOrder


class CustomerOrderFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:
        model = CustomerOrder

    id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)
    address = factory.Faker("address")
    # address_line2 = factory.Faker("address")
    # city = factory.Faker("city")
    # state = factory.Faker("state")
    # zip_code = factory.Faker("zipcode")
    # status = FuzzyChoice(choices=["pending", "completed", "canceled"])