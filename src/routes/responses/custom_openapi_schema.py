"""Custom openapi schema definitions are located here."""

from typing import Any

from fastapi import FastAPI

from src.custom_types import EndpointRouteType


def custom_400_500_openapi_schema(fastapi_app: FastAPI) -> dict[str, Any]:
    if fastapi_app.openapi_schema:
        return fastapi_app.openapi_schema

    # adapt sets to exclude paths in autom. response code generations
    api_root = EndpointRouteType.APP_ROOT
    app_root = EndpointRouteType.APP

    exclude_401_for_paths: set[str] = {
        f"/{api_root}/{app_root}/login",
    }
    exclude_403_for_paths: set[str] = {
        f"/{api_root}/{app_root}/login",
    }

    # call original openapi get the openapi schema
    original_openapi: dict[str, Any] = fastapi_app.openapi_original()  # type: ignore

    for path in original_openapi["paths"]:
        for method in original_openapi["paths"][path]:
            # remove default 422 status codes
            if "422" in original_openapi["paths"][path][method]["responses"]:
                del original_openapi["paths"][path][method]["responses"]["422"]

            original_openapi["paths"][path][method]["responses"]["400"] = {
                "description": "Bad Request",
                "content": {
                    "application/json": {
                        "example": {
                            "summary": "Bad Request",
                            "value": {
                                "error": "Validation Error",
                                "details": {
                                    "detail": [
                                        {
                                            "type": "string_type",
                                            "loc": ["body", "name"],
                                            "msg": "Input should be a valid string",
                                            "input": 123,
                                            "url": "https://errors.pydantic.dev/2.6/v/string_type",
                                            # noqa: E501  # pylint: disable=line-too-long
                                        }
                                    ]
                                },
                            },
                        },
                    }
                },
            }

            if path not in exclude_401_for_paths:
                original_openapi["paths"][path][method]["responses"]["401"] = {
                    "description": "Unauthorized",
                    "content": {
                        "application/json": {
                            "example": {
                                "summary": "Unauthorized",
                                "value": {
                                    "message": "Unauthorized",
                                },
                            },
                        }
                    },
                }

            if path not in exclude_403_for_paths:
                original_openapi["paths"][path][method]["responses"]["403"] = {
                    "description": "Forbidden",
                    "content": {
                        "application/json": {
                            "example": {
                                "summary": "Forbidden",
                                "value": {
                                    "message": "Forbidden",
                                },
                            },
                        }
                    },
                }

            original_openapi["paths"][path][method]["responses"]["500"] = {
                "description": "Internal Server Error",
                "content": {
                    "application/json": {
                        "example": {
                            "summary": "Internal Server Error",
                            "value": {
                                "error": "No Database Connection",
                                "details": {
                                    "ip": "127.0.0.1",
                                },
                            },
                        },
                    }
                },
            }

    # override openapi schema with new one
    fastapi_app.openapi_schema = original_openapi

    # return new openapi schema
    return fastapi_app.openapi_schema
