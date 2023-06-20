# Requirements:
- Python 3.11
- Pip3
- Pip Packages:
    - uvicorn
    - fastapi
    - pydantic
    - email-validator
    - yaml

# Description:

This API was built and tested using Python, FastAPI, and Uvicorn. It maintains a customer list as a yaml file and has endpoints to return customer data based on a customer ID, to update customer data based on a customer ID, and to add a new customer.

# Instantiating the API

Run `uvicorn main:app --reload`

# Testing the endpoints

Take note of the URL passed back by Uvicorn in your terminal. It should be something like `http://127.0.0.1:8000`. Navigate to this address and add `/docs` to load Swagger UI. From here you can select an endpoint, view documentation, and "Try it out" to make calls against each endpoint and view responses. Sample API calls are included for each endpoint doc.
