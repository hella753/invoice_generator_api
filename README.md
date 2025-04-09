# Invoice Generator API
This is a Django Rest Framework project that provides an API for
generating invoices in PDF format. This automates the process of creating invoices and allows 
users to manage their invoice templates efficiently. Authenticated users can create, 
update and delete the payer companies. They can generate invoices with the purpose text, 
amount (VAT calculated automatically 18%), language, template design, currency and the payer company.

[//]: # (![Logo]&#40;/logo.png&#41;)

## Table of Contents
- [Features](#features)
- [Endpoints](#endpoints)
  - [User Authentication](#user-authentication)
  - [Invoice Generation](#invoice-generation)
  - [Payers](#payers)
  - [Favorite Invoice Templates](#favorite-invoice-templates)
  - [Personal Account](#personal-account)
- [Database Schema](#database-schema)
- [Components](#components)
  - [Models](#models)
  - [Serializers](#serializers)
  - [Viewsets and Views](#viewsets-and-views)
  - [Permissions](#permissions)
  - [URLs](#urls)
- [Services](#services) 
  - [Email Sending](#email-sending)
  - [Invoice Service](#invoice-service)


## Features
- **User Authentication**: User registration, login, and authentication via JWT.
- **Invoice Generation**: Endpoints for generating invoices with various parameters like purpose text, amount, language, template design, currency and payer company.
- **Payers**: Endpoints for creating, updating, deleting and listing payer companies.
- **Favorite invoice templates**: Endpoints for creating, updating, deleting and listing favorite invoice templates.
- **Search**: Search functionality for invoices and payer companies.
- **Permissions & Security**: Custom permissions and exceptions for ensuring data privacy and security.
- **Email Sending**: Handles Message Sending to newly registered users and password reset links.
- **Multiple Language Support**: Supports multiple languages for invoice generation.


## Endpoints
### User Authentication

| Method | Endpoint                            | Description                                 |
|--------|-------------------------------------|---------------------------------------------|
| POST   | `/user/user`                        | Registers a new user                        |
| POST   | `/api/token/`                       | Obtain a JWT token                          |
| POST   | `/api/token/refresh/`               | Obtain a new access token                   |
| POST   | `/api/token/verify/`                | Verifies the token                          |
| POST   | `/api/token/blacklist/`             | Blacklist the refresh token                 |
| POST   | `/user/user/reset-password/`        | Resets the user password                    |
| POST   | `/user/user/forget-password/`       | Sends a reset password link to email        |
| POST   | `/user/verify-email/`               | Verifies the user's email address           |

### Invoice Generation
| Method | Endpoint                   | Description                                 |
|--------|----------------------------|---------------------------------------------|
| POST   | `/api/generate_invoice/`   | Generates an invoice PDF with given data    |

### Payers
| Method | Endpoint                            | Description                                 |
|--------|-------------------------------------|---------------------------------------------|
| POST   | `/api/payers/`                      | Creates a new payer company                 |
| GET    | `/api/payers/`                      | Lists all payer companies for the user      |
| GET    | `/api/payers/{payer_id}/`           | Retrieves a specific payer company          |
| PUT    | `/api/payers/{payer_id}/`           | Updates a specific payer company            |
| DELETE | `/api/payers/{payer_id}/`           | Deletes a specific payer company            |

### Favorite Invoice Templates
| Method | Endpoint                                  | Description                                       |
|--------|-------------------------------------------|---------------------------------------------------|
| POST   | `/api/favourites`                         | Creates a new favorite invoice template           |
| GET    | `/api/favourites`                         | Lists all favorite invoice templates              |
| GET    | `/api/favourites/{favourite_id}`          | Retrieves a specific favorite invoice template    |
| PUT    | `/api/favourites/{favourite_id}`          | Updates a specific favorite invoice template      |
| DELETE | `/api/favourites/{favourite_id}`          | Deletes a specific favorite invoice template      |

### Personal Account
| Method | Endpoint                          | Description                                 |
|--------|-----------------------------------|---------------------------------------------|
| GET    | `/user/user/{user_id}/`           | Retrieves the user information              |
| PUT    | `/user/user/{user_id}/`           | Updates the user information                |
| DELETE | `/user/user/{user_id}/`           | Deletes the user account                    |
| GET    | `/user/current_user/`             | Retrieves the current logged-in user info   |

## Database Schema
PostgreSQL is used as the database for this project. The database schema includes tables for users, invoices, payers, and favorite invoice templates.
![Database Schema](/database_schema.png)

## Components
### Models
The backend uses Django ORM to define models representing entities like `User`, `Invoice`, `Payer`, `Purpose`.

- **User**: Extended user model with custom fields and authentication methods.
- **Invoice**: Represents a favourite invoice the user saves.
- **Payer**: Represents a payer company with fields like name and contact information.
- **Purpose**: Represents the purpose of the invoice with fields like amount, invoice, vat and description.

### Serializers
Django Rest Framework serializers are used for converting model instances into JSON format and vice versa.
- **User app**: Contains serializers for User Creation, User Password Reset, User Verification.
- **API**: Contains serializers for Invoice Generation, Payer CRUD operations, Favorite Invoice Templates CRUD operations.

### ViewSets and Views
Django Rest Framework Views and ViewSets are used for handling CRUD operations for models.
- **UserViewSet**: Handles user registration, login, password reset, and email verification.
- **CurrentUserView**: Handles retrieving the current user information.
- **PayerViewSet**: Handles CRUD operations for payer companies.
- **BlacklistTokenView**: Handles blacklisting JWT tokens.
- **FavouritesViewSet**: Handles CRUD operations for favorite invoice templates.
- **GenerateInvoiceView**: Handles generating invoices in PDF format.

### Permissions
- **IsOwner**: Custom permission for checking if the user is the owner of the object.
- **IsCorrectUser**: Custom permission to only allow users to edit their own object.

### URLs
The URLs are routed through Django’s URL dispatcher.
- `api/`: Base URL for API.
- `user/`: Base URL for user authentication.
- `admin/`: Admin panel for managing the application.
- `/`: Swagger API documentation.

## Services
### Email Sending
- Send an email with a link to reset the password
- Verify the email address of the user during registration.

### Invoice Service
- Generate an invoice in PDF format with the given parameters.
- Calculates the VAT automatically based on the amount.
- Supports multiple languages for invoice generation.
- Generate the invoice number automatically based on the date.
