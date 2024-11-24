# BudgetBuddy Expense Tracker - Backend

## Setup and Installation

### 1. Setting up the Expense Service

Navigate to the `expense-service` directory:

```bash
cd expense-service
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment:

On macOS/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

Install required dependencies:

```bash
pip install flask pymongo python-dotenv flask-cors jwt bcrypt
```

Freeze the dependencies into a `requirements.txt` file:

```bash
pip freeze > requirements.txt
```

Start the application:

```bash
python app.py
```

### 2. Setting up the User Service

Navigate to the `user-service` directory:

```bash
cd user-service
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment:

On macOS/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

Install required dependencies:

```bash
pip install flask pymongo python-dotenv flask-cors jwt bcrypt
```

Freeze the dependencies into a `requirements.txt` file:

```bash
pip freeze > requirements.txt
```

Start the application:

```bash
python app.py
```

## API Endpoints

### User Service Endpoints

1. **POST /register - Register a regular user**

    URL: `http://localhost:5000/register`

    Body (JSON):
    ```json
    {
      "username": "testuser",
      "password": "testpassword"
    }
    ```

    Response:
    ```json
    {
      "message": "User registered successfully"
    }
    ```

2. **POST /login - Log in a regular user**

    URL: `http://localhost:5000/login`

    Body (JSON):
    ```json
    {
      "username": "testuser",
      "password": "testpassword"
    }
    ```

    Response:
    ```json
    {
      "message": "Login successful"
    }
    ```

3. **POST /admin/register - Register an admin user**

    URL: `http://localhost:5000/admin/register`

    Body (JSON):
    ```json
    {
      "username": "adminuser",
      "password": "adminpassword"
    }
    ```

    Response:
    ```json
    {
      "message": "Admin registered successfully"
    }
    ```

4. **POST /admin/login - Log in an admin user**

    URL: `http://localhost:5000/admin/login`

    Body (JSON):
    ```json
    {
      "username": "adminuser",
      "password": "adminpassword"
    }
    ```

    Response:
    ```json
    {
      "message": "Admin login successful"
    }
    ```

5. **POST /admin/user - Allows an admin to create a new user**

    URL: `http://localhost:5000/admin/user`

    Body (JSON):
    ```json
    {
      "username": "newuser",
      "password": "newpassword",
      "admin_username": "adminuser",
      "admin_password": "adminpassword"
    }
    ```

    Response:
    ```json
    {
      "message": "User created by admin"
    }
    ```

6. **GET /admin/user/<user_id> - Allows an admin to view a user's details**

    URL: `http://localhost:5000/admin/user/<user_id>`

    Headers:
    ```
    admin_username: adminuser
    admin_password: adminpassword
    ```

    Response:
    ```json
    {
      "username": "newuser",
      "role": "user"
    }
    ```

7. **PUT /admin/user/<user_id> - Allows an admin to update a user's information**

    URL: `http://localhost:5000/admin/user/<user_id>`

    Body (JSON):
    ```json
    {
      "username": "updateduser",
      "password": "updatedpassword",
      "admin_username": "adminuser",
      "admin_password": "adminpassword"
    }
    ```

    Response:
    ```json
    {
      "message": "User updated successfully"
    }
    ```

8. **DELETE /admin/user/<user_id> - Allows an admin to delete a user**

    URL: `http://localhost:5000/admin/user/<user_id>`

    Headers:
    ```
    admin_username: adminuser
    admin_password: adminpassword
    ```

    Response:
    ```json
    {
      "message": "User deleted successfully"
    }
    ```

### Expense Service Endpoints

1. **POST /expenses - Create a new expense**

    URL: `http://localhost:5002/expenses`

    Body (raw, JSON format):
    ```json
    {
      "description": "Lunch",
      "amount": 10,
      "category": "Food",
      "date": "2024-11-24"
    }
    ```

2. **GET /expenses - Get all expenses**

    URL: `http://localhost:5002/expenses`

3. **GET /expenses/<expense_id> - Get a specific expense by ID**

    URL: `http://localhost:5002/expenses/<expense_id>`

    Replace `<expense_id>` with a valid ObjectId.

4. **PUT /expenses/<expense_id> - Update an expense**

    URL: `http://localhost:5002/expenses/<expense_id>`

    Body (raw, JSON format):
    ```json
    {
      "description": "Dinner",
      "amount": 20,
      "category": "Food",
      "date": "2024-11-25"
    }
    ```

5. **DELETE /expenses/<expense_id> - Delete an expense**

    URL: `http://localhost:5002/expenses/<expense_id>`

## Postman Testing

### Environment Setup

In Postman, create an environment with the following variables:

- `admin_username`: `adminuser`
- `admin_password`: `adminpassword`

Use these variables in the Headers for the requests:

For GET, PUT, and DELETE requests to `/admin/user/<user_id>`, include the headers:
```
admin_username: {{admin_username}}
admin_password: {{admin_password}}
```

## Frontend

The frontend for the BudgetBuddy Expense Tracker can be found in the [frontend repository](https://github.com/abhixsh/BudgetBuddy).
