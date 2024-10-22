# Spotter Django Project

## Overview

This is a Django-based web application for managing a library system. It includes functionality for interacting with an API, importing books, and handling errors.

## Project Structure

- **library/**: The core Django app handling the library system logic.
- **library_api/**: API endpoints for interacting with the library system.
- **manage.py**: Django's management script for executing commands like migrations, running the server, etc.
- **requirements.txt**: A file containing the list of dependencies for the project.
- **.env**: Contains environment variables required for the project (make sure to keep sensitive information secure).
- **Library API - Django.postman_collection.json**: A Postman collection for testing API endpoints.
- **import_books_errors.log**: Log file for any errors encountered during book imports.
- **structure.txt**: Documentation about the structure of the project.

## Installation

### Prerequisites

Ensure you have the following installed on your system:

- Python 3.x
- Django
- PostgreSQL or SQLite (for the database)
- pip (Python package manager)

### Installation Steps

1. Clone the repository:

    ```bash
    git clone <repository-url>
    ```

2. Navigate to the project directory:

    ```bash
    cd spotter-Django-main
    ```

3. Create a virtual environment and activate it:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Set up the `.env` file:

   Ensure you have a `.env` file in the root directory with the necessary environment variables such as database credentials, secret keys, etc.

6. Apply database migrations:

    ```bash
    python manage.py migrate
    ```

7. Start the development server:

    ```bash
    python manage.py runserver
    ```

8. Test the API endpoints using the provided Postman collection (`Library API - Django.postman_collection.json`).

## Usage

- To add, update, or delete books, access the Django admin panel.
- API endpoints can be tested using tools like Postman.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is personal project developed for evaluation.
