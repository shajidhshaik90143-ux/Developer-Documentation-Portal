from .database import get_documents, create_document, create_api, create_snippet

def seed_demo():
    if get_documents():
        return

    docs = [
        {
            "title": "Getting Started with REST APIs",
            "slug": "getting-started-rest-apis",
            "summary": "Learn the fundamentals of REST APIs, HTTP methods, status codes, and JSON.",
            "category": "API",
            "tags": "rest,api,http,json",
            "author": "Documentation Team",
            "status": "Published",
            "difficulty": "Beginner",
            "content": """# Getting Started with REST APIs

REST APIs expose resources through standard HTTP operations.

## HTTP Methods

| Method | Purpose |
|---|---|
| GET | Read resources |
| POST | Create resources |
| PUT | Replace resources |
| PATCH | Partially update resources |
| DELETE | Remove resources |

## Example

```python
import requests

response = requests.get("https://api.example.com/users")
response.raise_for_status()
users = response.json()
print(users)
```

## Status Codes

- `200` — successful request
- `201` — resource created
- `400` — invalid request
- `401` — authentication required
- `404` — resource not found
- `500` — server error

## Best Practices

1. Use nouns for resource paths.
2. Return meaningful HTTP status codes.
3. Validate request data.
4. Document authentication requirements.
5. Keep response schemas stable.
"""
        },
        {
            "title": "Python Virtual Environments",
            "slug": "python-virtual-environments",
            "summary": "Create isolated Python environments for clean and reproducible projects.",
            "category": "Python",
            "tags": "python,venv,setup,packages",
            "author": "Documentation Team",
            "status": "Published",
            "difficulty": "Beginner",
            "content": """# Python Virtual Environments

Virtual environments isolate project dependencies.

## Create

```bash
python -m venv .venv
```

## Activate on Windows

```powershell
.venv\\Scripts\\activate
```

## Activate on macOS/Linux

```bash
source .venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Export dependencies

```bash
pip freeze > requirements.txt
```
"""
        },
        {
            "title": "JWT Authentication Guide",
            "slug": "jwt-authentication-guide",
            "summary": "Understand JSON Web Tokens and common authentication flows.",
            "category": "Security",
            "tags": "jwt,auth,security,tokens",
            "author": "Security Team",
            "status": "Draft",
            "difficulty": "Intermediate",
            "content": """# JWT Authentication Guide

JWTs can carry signed claims between a client and a server.

## Typical Flow

1. User submits credentials.
2. Server validates the credentials.
3. Server issues a signed token.
4. Client sends the token with protected requests.
5. Server verifies the signature and claims.

> Never place passwords or sensitive secrets inside JWT payloads.

## Header Example

```http
Authorization: Bearer <token>
```
"""
        }
    ]
    for d in docs:
        create_document(d)

    apis = [
        dict(name="List Users", method="GET", path="/api/v1/users", category="Users",
             description="Returns a paginated list of users.", parameters="page: integer; limit: integer",
             response='{"data": [], "page": 1, "total": 0}', auth="Bearer Token"),
        dict(name="Create User", method="POST", path="/api/v1/users", category="Users",
             description="Creates a new user.", parameters="name: string; email: string",
             response='{"id": 101, "name": "Alex"}', auth="Bearer Token"),
        dict(name="Health Check", method="GET", path="/health", category="System",
             description="Returns service health information.", parameters="None",
             response='{"status": "ok"}', auth="None")
    ]
    for a in apis:
        create_api(a)

    snippets = [
        dict(title="Fetch JSON with Requests", language="python",
             code='import requests\\n\\nresponse = requests.get(url, timeout=10)\\nresponse.raise_for_status()\\ndata = response.json()',
             description="Basic safe JSON API request.", tags="python,api,http"),
        dict(title="Async JavaScript Fetch", language="javascript",
             code='const response = await fetch("/api/users");\\nif (!response.ok) throw new Error("Request failed");\\nconst data = await response.json();',
             description="Modern browser fetch pattern.", tags="javascript,fetch,api"),
        dict(title="SQL Parameterized Query", language="sql",
             code="SELECT id, name, email\\nFROM users\\nWHERE status = ?\\nORDER BY created_at DESC;",
             description="Use parameters instead of string concatenation.", tags="sql,security")
    ]
    for s in snippets:
        create_snippet(s)
