# tests/unit/test_integration.py
#
# End-to-end tests through Django Ninja's request/response machinery —
# these exercise signature resolution, query-param parsing, and OpenAPI
# generation, which direct view calls bypass.

import pytest
from ninja import FilterSchema, NinjaAPI, Query, Router, Schema
from ninja.testing import TestClient

from ninja_search import searching

from .models import Item


class ItemOut(Schema):
    name: str
    description: str


class ItemFilter(FilterSchema):
    name: str | None = None


received_filters: list = []

router = Router()


@router.get("/items", response=list[ItemOut])
@searching(
    filter_schema=ItemFilter,
    search_fields=["name", "description"],
    sort_fields=["name"],
)
def list_items(request):
    # no filters/search/ordering params declared: the decorator injects them
    return Item.objects.all()


@router.get("/items-explicit", response=list[ItemOut])
@searching(
    filter_schema=ItemFilter,
    search_fields=["name"],
    sort_fields=["name"],
)
def list_items_explicit(request, filters: ItemFilter = Query(...)):
    received_filters.append(filters)
    return Item.objects.all()


@router.get("/items-tuple", response={201: list[ItemOut]})
@searching(search_fields=["name"], sort_fields=["name"])
def list_items_tuple(request):
    return 201, Item.objects.all()


api = NinjaAPI()
api.add_router("", router)
client = TestClient(router)


@pytest.fixture
def fruit():
    Item.objects.create(name="Banana", description="Yellow fruit")
    Item.objects.create(name="Apple", description="Red fruit")


@pytest.mark.django_db
def test_search_over_http(fruit):
    response = client.get("/items?search=banana")
    assert response.status_code == 200
    assert [i["name"] for i in response.json()] == ["Banana"]


@pytest.mark.django_db
def test_injected_filters_param_works_over_http(fruit):
    # the view declares no filters param; ninja must still parse ?name=
    response = client.get("/items?name=Apple")
    assert response.status_code == 200
    assert [i["name"] for i in response.json()] == ["Apple"]


@pytest.mark.django_db
def test_ordering_over_http(fruit):
    response = client.get("/items?ordering=-name")
    assert [i["name"] for i in response.json()] == ["Banana", "Apple"]


@pytest.mark.django_db
def test_malformed_ordering_does_not_500(fruit):
    response = client.get("/items?ordering=--name")
    assert response.status_code == 200
    assert [i["name"] for i in response.json()] == ["Apple", "Banana"]


@pytest.mark.django_db
def test_explicit_filters_param_reaches_view_body(fruit):
    received_filters.clear()
    response = client.get("/items-explicit?name=Banana")
    assert response.status_code == 200
    assert [i["name"] for i in response.json()] == ["Banana"]
    # the wrapped view received the parsed schema, not a FieldInfo default
    assert received_filters == [ItemFilter(name="Banana")]


@pytest.mark.django_db
def test_status_tuple_over_http(fruit):
    response = client.get("/items-tuple?search=apple")
    assert response.status_code == 201
    assert [i["name"] for i in response.json()] == ["Apple"]


def test_params_are_documented_in_openapi():
    schema = api.get_openapi_schema(path_prefix="")
    operation = schema["paths"]["/items"]["get"]
    params = {p["name"] for p in operation["parameters"]}
    assert {"search", "ordering", "name"} <= params
