ROLE_DATA = {
    "create": {
        "role_name": "manager",
        "color": "#FF5733",
        "is_admin": True,
        "is_editable": True,
        "is_default": False,
        "is_active": False
    },
    "update": {
        "role_name": "senior_manager",
        "color": "#33FF57",
        "is_admin": True,
        "is_editable": True,
        "is_default": False,
        "is_active": False
    }
}

# test_data.py

USER_DATA = {
    "superuser": {
        "first_name": "Super",
        "last_name": "Admin",
        "email": "super@example.com",
        "phone": "+254700000001",
    },
    "register": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+254712345678",
    },
    "update": {
        "first_name": "John Updated",
        "last_name": "Doe Updated",
        "email": "john.updated@example.com",
        "phone": "+254787654321",
    },
    "login": {
        "email": "john.doe@example.com",
        "password": "NewSecurePassword123!"
    }
}

USER_PASSWORD_DATA = {
    "set_password": {
        "uidb64": "sample-uidb64",
        "token": "sample-token",
        "new_password": "NewSecurePassword123!"
    }
}


ROLE_PERMISSION_DATA = {
    "create": {
        "role_id": 1,
        "can_create": True,
        "can_read": True,
        "can_update": False,
        "can_delete": False,
        "can_manage": False,
        "can_create_account": True,
        "can_dispatch_driver": False
    },
    "update": {
        "role_id": 1,
        "can_create": False,
        "can_read": True,
        "can_update": True,
        "can_delete": True,
        "can_manage": True,
        "can_create_account": False,
        "can_dispatch_driver": True
    }
}
