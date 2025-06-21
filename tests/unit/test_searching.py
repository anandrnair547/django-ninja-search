# tests/unit/test_searching.py
import pytest
from django.test import RequestFactory
from ninja import Query
from ninja import Schema

from tests.unit.models import Item
from ninja_search.searching import searching


class DummyFilterSchema(Schema):
    pass


@searching(
    filterSchema=DummyFilterSchema,
    search_fields=["name", "description"],
    sort_fields=["name"],
)
def list_items(request, filters: DummyFilterSchema = Query(...)):
    return Item.objects.all()


@pytest.mark.django_db
def test_searching_decorator_filters_items():
    Item.objects.create(name="Banana", description="Yellow fruit")
    Item.objects.create(name="Apple", description="Red fruit")

    request = RequestFactory().get("/?search=Banana")
    result = list_items(request)

    assert result.count() == 1
    assert result.first().name == "Banana"


@pytest.mark.django_db
def test_searching_decorator_sorts_items():
    Item.objects.create(name="Banana", description="Yellow")
    Item.objects.create(name="Apple", description="Red")

    request = RequestFactory().get("/?ordering=name")
    result = list_items(request)

    names = list(result.values_list("name", flat=True))
    assert names == ["Apple", "Banana"]
