# main.py

from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
import yaml
import re
import uvicorn

app = FastAPI()
customer_file = "customers.yaml"


# Define a base model for the PropertyAddress class
class PropertyAddress(BaseModel):
    street: str
    city: str
    postal_code: str
    state_code: str

    @validator("postal_code")
    def validate_postal_code(cls, postal_code):
        if not re.match(r'^\d{5}$', postal_code):
            raise ValueError("Postal Code must be 5 numeric digits")
        return postal_code


# Define a base model for the Customer class
class Customer(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    electricity_usage_kwh: Optional[int] = None
    old_roof: bool
    property_address: PropertyAddress


# Define a base model for the UpdateCustomer class. 
# This is needed since exclude_unset wasn't working as expected in the Patch operation.
class UpdateCustomer(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    old_roof: Optional[bool]
    property_address: Optional[PropertyAddress]


# Read from a yaml file
def read_yaml_file(yaml_file: str):
    try:
        with open(yaml_file, "r") as file:
            customers = yaml.safe_load(file) or []
    except FileNotFoundError:
        customers = []
    return customers


# Write changes to the YAML file
def write_yaml_file(yaml_file: str, customer_data):
    with open(yaml_file, "w") as file:
        yaml.safe_dump(customer_data, file)


# Retrieve customer data from the YAML file based on a customer_id
def fetch_customer(customer_id):
    customer_list = read_yaml_file(customer_file)
    for customer in customer_list["customers"]:
        if customer["id"] == customer_id:
            return customer
    raise HTTPException(status_code=404, detail="Customer not found")


# API endpoint that returns customer data based on a customer ID
@app.get("/customers/{customer_id}", summary="Get Customer Info by Customer ID")
async def get_customer_data(customer_id: str):
    """
    Get customer information based on customer ID.

    - **customer_id**: ID of the customer to retrieve.

    ### Example API call:
    ```bash
    curl -X GET "http://localhost:8000/customer/1"
    ```

    """
    customer_info = fetch_customer(customer_id)
    if customer_info:
        return customer_info


# API endpoint that allows editing of some aspects of a customer's data based on a customer ID
@app.patch("/customers/{customer_id}", summary="Update Customer Information")
async def update_customer_data(customer_id: str, customer: UpdateCustomer):
    """
    Update an existing customer in the system.

    - **customer_data**: Only updated fields are required. ID and electrical usage cannot be changed.

    ### Example API call:
    ```bash
    curl -X PATCH -H "Content-Type: application/json" -d '{
    "first_name": "James",
    "email": "jdoe@example.com",
    }' "http://localhost:8000/customer/1234"
    ```

    """
    customer_list = read_yaml_file(customer_file)
    customer_updated = False
    for existing_customer in customer_list["customers"]:
        if existing_customer["id"] == customer_id:
            existing_customer.update(customer.dict(exclude_unset=True))
            existing_customer["id"] = customer_id
            customer_updated = True
            break
    if customer_updated:
            write_yaml_file(customer_file, customer_list)
            return {"message": "Customer data updated successfully"}
    raise HTTPException(status_code=404, detail="Customer not found")


# API endpoint that allows for adding a new customer into the YAML file
@app.post("/customers/", summary="Create New Customer")
async def create_customer(customer: Customer):
    """
    Add a new customer to the system.

    - **customer_id**: New, unique customer ID based on the existing pattern.
    - **customer_data**: Required data for the new customer.

    ### Example API call:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{
    "id": 1234,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "property_address": {
        "street": "123 Main St",
        "city": "Cityville",
        "state": "State",
        "postal_code": "12345"
    }' "http://localhost:8000/customer/"
    ```

    """
    customer_list = read_yaml_file("customers.yaml")
    new_customer = customer.dict()
    # Check if an account already exists for the specified email address
    if any(cust["email"] == new_customer["email"] for cust in customer_list["customers"]):
        raise HTTPException(status_code=409, detail="Email address already taken")
    # Make sure the User ID is unique since it isn't automated here.
    if any(cust["id"] == new_customer["id"] for cust in customer_list["customers"]):
        raise HTTPException(status_code=410, detail="Customer ID is not unique")
    customer_list["customers"].append(new_customer)
    write_yaml_file(customer_file, customer_list)
    return new_customer