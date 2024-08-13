"""All tests for custom_openapi_schema are located here."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="scope")


@pytest.mark.dependency
async def test_custom_openapi_schema(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    openapi_schema = response.json()

    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            responses = openapi_schema["paths"][path][method].get("responses", {})
            if "422" in responses:
                content = responses["422"]["content"]["application/json"]
                examples = content.get("examples", {})
                assert "example_1" in examples
                assert "example_2" in examples
                assert examples["example_1"]["summary"] == "Data Serialization/Validation Error"
                assert examples["example_2"]["summary"] == "Inconsistent Database"
                assert examples["example_1"]["value"]["detail"][0]["type"] == "string_type"
                assert examples["example_2"]["value"]["message"] == "Inconsistent Database! ..."
