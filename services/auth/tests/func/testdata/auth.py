
TOKENS = [
    {
        "type": "access_token",
        "payload_fields": ["sub", "device_id", "roles", "exp"],
    },
    {"type": "refresh_token", "payload_fields": ["sub", "device_id", "exp"]},
]

GET_REFRESH_TOKEN_REQUEST = """
    SELECT * FROM public.user
        JOIN public.refresh_token AS token
        ON token.user_id=public.user.id
        WHERE public.user.login='superuser'
"""

INSERT_SUPERUSER_DEVICE_REQUEST = """
    INSERT INTO "device" (
        id,
        user_id,
        user_agent,
        created_at,
        modified_at
        )
    VALUES (
        '8afd98c5-a349-4904-b5a8-403e61517999',
        '11111111-1111-1111-1111-111111111111',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        '2024-04-26 17:26:11.42932',
        '2024-04-26 17:26:11.42932'
    );
"""

INSERT_SUPERUSER_REFRESH_TOKEN_REQUEST = """
    INSERT INTO "refresh_token" (
        id,
        user_id,
        device_id,
        refresh_token,
        created_at
        )
    VALUES (
        '8afd98c5-a349-4904-b5a8-403e61517999',
        '11111111-1111-1111-1111-111111111111',
        '8afd98c5-a349-4904-b5a8-403e61517999',
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJzdXBlcnVzZXIiLCJkZXZpY2VfaWQiOiIwZTE4MmExNC0zYzY1LTRhMTYtODVmZi1kZGE4NzUzZThlZTkiLCJleHAiOiIxNzE4NzQ5MTcyLjYwNzE5NiJ9.fcf0e57044ac356e3a5a0610f9b8021770229a886f96af5c214461ffa1ec4908',
        '2024-04-26 17:26:11.42932'
    );
"""
