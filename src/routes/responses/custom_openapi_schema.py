from typing import Any

from fastapi import FastAPI


def custom_422_openapi_schema(fastapi_app: FastAPI) -> dict[str, Any]:
    if fastapi_app.openapi_schema:
        return fastapi_app.openapi_schema

    # call original openapi get the openapi schema
    original_openapi = fastapi_app.openapi_original()

    for path in original_openapi["paths"]:
        for method in original_openapi["paths"][path]:
            if "422" in original_openapi["paths"][path][method]["responses"]:
                original_openapi["paths"][path][method]["responses"]["422"] = {
                    "description": "Unprocessable Content",
                    "content": {
                        "application/json": {
                            "examples": {
                                "example_1": {
                                    "summary": "Data Serialization/Validation Error",
                                    "value": {
                                        "detail": [
                                            {
                                                "type": "string_type",
                                                "loc": ["body", "name"],
                                                "msg": "Input should be a valid string",
                                                "input": 123,
                                                "url": "https://errors.pydantic.dev/2.6/v/string_type",
                                            }
                                        ]
                                    },
                                },
                                "example_2": {
                                    "summary": "Inconsistent Database",
                                    "value": {
                                        "message": "Inconsistent Database! ...",
                                        "details": {"key": "value"},
                                    },
                                },
                            }
                        }
                    },
                }

    # override openapi schema with new one
    fastapi_app.openapi_schema = original_openapi

    # return new openapi schema
    return fastapi_app.openapi_schema
