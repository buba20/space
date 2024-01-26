from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str

class Person(BaseModel):
    name: str
    age: int
    addresses: List[Address]
    hobbies: List[str]

# Przykładowy słownik z zagnieżdżonymi typami i listami
data = {
    'name': 'John Doe',
    'age': 30,
    'addresses': [{'street': '123 Main St', 'city': 'Example City'}, {'street': '456 Side St', 'city': 'Another City'}],
    'hobbies': ['reading', 'gardening']
}

# Deserializacja słownika do klasy
person_instance = Person(**data)

# Wyświetlenie rezultatu
print(person_instance.addresses[1].street)
