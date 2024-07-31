from http import HTTPStatus

INSERT_ACCESS_DB = [
    """INSERT INTO public.user_role (id, user_id, role_id, created_at)
    VALUES ('11111111-1111-1111-1111-111111111111',
            '8afd98c5-a349-4904-b5a8-403e61517999',
            '11111111-1111-1111-1111-111111111111',
            '2024-04-26 17:26:11.42932')
""",
    """INSERT INTO public.user_role (id, user_id, role_id, created_at)
    VALUES ('22222222-2222-2222-2222-222222222222',
            '8afd98c5-a349-4904-b5a8-403e61517999',
            '22222222-2222-2222-2222-222222222222',
            '2024-04-26 17:26:11.42932')
""",
]
GET_ACCESS_LIST = [
    {
        "user_login": "login",
        "roles": ["auth_admin", "subscriber"],
        "status": HTTPStatus.OK,
    },
    {"user_login": "superuser", "roles": [], "status": HTTPStatus.OK},
    {"user_login": "1", "status": HTTPStatus.UNPROCESSABLE_ENTITY},
    {"user_login": "\\1\\``///", "status": HTTPStatus.UNPROCESSABLE_ENTITY},
    {
        "user_login": "supermegalongpath" * 100,
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
    },
    {"user_login": "12345", "status": HTTPStatus.NOT_FOUND},
]

CHECK_ACCESS = [
    {
        "user_login": "login",
        "role_title": "auth_admin",
        "result": True,
        "status": HTTPStatus.OK,
    },
    {
        "user_login": "superuser",
        "role_title": "auth_admin",
        "result": False,
        "status": HTTPStatus.OK,
    },
    {
        "user_login": "login",
        "role_title": "qwerty",
        "status": HTTPStatus.NOT_FOUND,
    },
    {
        "user_login": "qwerty",
        "role_title": "auth_admin",
        "status": HTTPStatus.NOT_FOUND,
    },
    {
        "user_login": "1",
        "role_title": "auth_admin",
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
    },
    {
        "user_login": "3495u293" * 100,
        "role_title": "1234566789",
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
    },
    {
        "user_login": "123",
        "role_title": "",
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
    },
]
ASSIGN_ACCESS = [
    {
        "body": {"user_login": "login", "role_title": "auth_admin"},
        "result": {
            "user_id": "8afd98c5-a349-4904-b5a8-403e61517999",
            "role_id": "11111111-1111-1111-1111-111111111111",
        },
        "status": HTTPStatus.CREATED,
    },
    {
        "body": {"user_login": "qwerty", "role_title": "auth_admin"},
        "status": HTTPStatus.NOT_FOUND,
    },
    {
        "body": {"user_login": "login", "role_title": "qwerty"},
        "status": HTTPStatus.NOT_FOUND,
    },
    {
        "body": {"user_login": 123, "role_title": 123},
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
    },
    {
        "body": {"user_login": "login"},
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
    },
    {
        "body": {
            "user_login": "913487511304857138745691384756239847",
            "role_title": "a a a",
        },
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
    },
]
REMOVE_ACCESS = [
    {
        "body": {"user_login": "login", "role_title": "auth_admin"},
        "result": {
            "user_id": "8afd98c5-a349-4904-b5a8-403e61517999",
            "role_id": "11111111-1111-1111-1111-111111111111",
        },
        "status": HTTPStatus.OK,
    },
    {
        "body": {"user_login": "qwerty", "role_title": "auth_admin"},
        "status": HTTPStatus.NOT_FOUND,
    },
    {
        "body": {"user_login": "login", "role_title": "qwerty"},
        "status": HTTPStatus.NOT_FOUND,
    },
    {
        "body": {"user_login": 123, "role_title": 123},
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
    },
    {
        "body": {"user_login": "login"},
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
    },
    {
        "body": {
            "user_login": "913487511304857138745691384756239847",
            "role_title": "a a a",
        },
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
    },
]
