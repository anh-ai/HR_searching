from faker import Faker
from pymongo import MongoClient

fake = Faker()

client = MongoClient('localhost', 27017)
db = client['HR']
collection = db['employee']

NData = 10  # 10**6
for _ in range(NData):
    employee = {
        'EmployeeID': fake.uuid4(),
        'FirstName': fake.first_name(),
        'LastName': fake.last_name(),
        'DateOfBirth': fake.date_of_birth(minimum_age=18, maximum_age=65).isoformat(),
        'Gender': fake.random_element(elements=('Male', 'Female')),
        'Email': fake.email(),
        'Phone': fake.phone_number(),
        'Address': fake.address(),
        'Education': fake.random_element(elements=('High School', 'Bachelor', 'Master', 'PhD')),
        'WorkExperience': fake.random_int(min=0, max=20),
        'DesiredField': fake.job(),
        'CareerObjective': fake.text(),
        'ExpectedSalary': fake.random_int(min=20000, max=100000),
        'Skills': fake.text(),
        'Status': fake.random_element(elements=('Active', 'Not started', 'Terminated')),
        'Locations': fake.random_element(elements=('Location A', 'Location B', 'Location C')),
        'Companies': fake.company(),
        'Departments': fake.random_element(elements=('HR', 'Finance', 'IT', 'Marketing')),
        'Positions': fake.random_element(elements=('Manager', 'Engineer', 'Analyst', 'Specialist'))
    }
    collection.insert_one(employee)
