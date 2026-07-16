# tests/unit/test_searching.py

import pytest
from django.test import RequestFactory
from ninja import FilterSchema, Schema

from ninja_search.searching import searching

from .models import Item, Tag


class ItemFilter(FilterSchema):
    name: str | None = None


@searching(
    filter_schema=ItemFilter,
    search_fields=["name", "description"],
    sort_fields=["name"],
)
def list_items(request):
    return Item.objects.all()


def get(query: str = ""):
    return RequestFactory().get(f"/{query}")


@pytest.fixture
def fruit():
    banana = Item.objects.create(name="Banana", description="Yellow fruit")
    apple = Item.objects.create(name="Apple", description="Red fruit")
    return banana, apple


# --- search ---


@pytest.mark.django_db
def test_search_filters_items(fruit):
    result = list_items(get("?search=Banana"))
    assert list(result.values_list("name", flat=True)) == ["Banana"]


@pytest.mark.django_db
def test_search_multi_term_is_and(fruit):
    # "Yellow" and "fruit" both match only Banana; OR semantics would return both
    result = list_items(get("?search=Yellow+fruit"))
    assert list(result.values_list("name", flat=True)) == ["Banana"]


@pytest.mark.django_db
def test_search_single_char_term_is_applied(fruit):
    # "w" appears only in "Yellow" — must not be dropped for being short
    result = list_items(get("?search=w"))
    assert list(result.values_list("name", flat=True)) == ["Banana"]


@pytest.mark.django_db
def test_search_term_count_is_capped(fruit):
    # 10 matching terms + an 11th non-matching term; the 11th must be ignored
    terms = ["fruit"] * 10 + ["zzz"]
    result = list_items(get("?search=" + "+".join(terms)))
    assert result.count() == 2


@pytest.mark.django_db
def test_search_across_to_many_relation_is_distinct():
    banana = Item.objects.create(name="Banana", description="Yellow fruit")
    Tag.objects.create(item=banana, label="sweet fruit")
    Tag.objects.create(item=banana, label="tropical fruit")

    @searching(search_fields=["tags.label"])
    def by_tag(request):
        return Item.objects.all()

    result = by_tag(get("?search=fruit"))
    assert result.count() == 1


@pytest.mark.django_db
def test_multi_term_search_matches_across_different_related_rows():
    # each term may be satisfied by a DIFFERENT related row
    banana = Item.objects.create(name="Banana", description="Yellow fruit")
    Tag.objects.create(item=banana, label="sweet fruit")
    Tag.objects.create(item=banana, label="tropical mango")

    @searching(search_fields=["tags.label"])
    def by_tag(request):
        return Item.objects.all()

    result = by_tag(get("?search=sweet+tropical"))
    assert result.count() == 1
    assert by_tag(get("?search=sweet+zzz")).count() == 0


# --- ordering ---


@pytest.mark.django_db
def test_ordering_ascending(fruit):
    result = list_items(get("?ordering=name"))
    assert list(result.values_list("name", flat=True)) == ["Apple", "Banana"]


@pytest.mark.django_db
def test_ordering_descending(fruit):
    result = list_items(get("?ordering=-name"))
    assert list(result.values_list("name", flat=True)) == ["Banana", "Apple"]


@pytest.mark.django_db
def test_default_ordering_without_param(fruit):
    result = list_items(get())
    assert list(result.values_list("name", flat=True)) == ["Apple", "Banana"]


@pytest.mark.django_db
def test_invalid_ordering_falls_back_to_default(fruit):
    result = list_items(get("?ordering=bogus"))
    assert list(result.values_list("name", flat=True)) == ["Apple", "Banana"]


@pytest.mark.django_db
def test_double_dash_ordering_is_rejected_not_500(fruit):
    # "--name" used to pass lstrip("-") validation and crash order_by()
    result = list_items(get("?ordering=--name"))
    assert list(result.values_list("name", flat=True)) == ["Apple", "Banana"]


@pytest.mark.django_db
def test_comma_separated_ordering(fruit):
    Item.objects.create(name="Apple", description="Green fruit")

    @searching(sort_fields=["name", "description"])
    def ordered(request):
        return Item.objects.all()

    result = ordered(get("?ordering=name,-description"))
    assert list(result.values_list("name", "description")) == [
        ("Apple", "Red fruit"),
        ("Apple", "Green fruit"),
        ("Banana", "Yellow fruit"),
    ]


@pytest.mark.django_db
def test_descending_default_sort_fields(fruit):
    @searching(sort_fields=["-name"])
    def newest_first(request):
        return Item.objects.all()

    assert list(newest_first(get()).values_list("name", flat=True)) == [
        "Banana",
        "Apple",
    ]
    # bare field still allowed for explicit ordering
    assert list(newest_first(get("?ordering=name")).values_list("name", flat=True)) == [
        "Apple",
        "Banana",
    ]


# --- filtering ---


@pytest.mark.django_db
def test_filter_schema_filters(fruit):
    result = list_items(get(), filters=ItemFilter(name="Banana"))
    assert list(result.values_list("name", flat=True)) == ["Banana"]


@pytest.mark.django_db
def test_no_filters_returns_all(fruit):
    assert list_items(get()).count() == 2


def test_plain_schema_rejected_at_decoration_time():
    class NotAFilter(Schema):
        pass

    with pytest.raises(TypeError, match="FilterSchema"):

        @searching(filter_schema=NotAFilter)
        def view(request):
            return Item.objects.all()


def test_filterschema_kwarg_is_deprecated_alias():
    with pytest.deprecated_call():

        @searching(filterSchema=ItemFilter)
        def view(request):
            return Item.objects.all()


def test_filter_schema_wins_over_deprecated_alias():
    class Other(FilterSchema):
        pass

    with pytest.deprecated_call():
        decorator = searching(filter_schema=ItemFilter, filterSchema=Other)

    @decorator
    def view(request):
        return Item.objects.all()


@pytest.mark.django_db
def test_view_declaring_own_params_still_receives_them(fruit):
    seen = {}

    @searching(search_fields=["name"], sort_fields=["name"])
    def view(request, search: str = "", ordering: str = ""):
        seen["search"] = search
        seen["ordering"] = ordering
        return Item.objects.all()

    result = view(get(), search="Banana", ordering="name")
    assert seen == {"search": "Banana", "ordering": "name"}
    assert list(result.values_list("name", flat=True)) == ["Banana"]


# --- return-value contract ---


@pytest.mark.django_db
def test_status_tuple_is_preserved(fruit):
    @searching(search_fields=["name"], sort_fields=["name"])
    def created(request):
        return 201, Item.objects.all()

    status, queryset = created(get("?search=Banana"))
    assert status == 201
    assert list(queryset.values_list("name", flat=True)) == ["Banana"]


@pytest.mark.django_db
def test_non_queryset_return_raises_type_error(fruit):
    @searching(search_fields=["name"])
    def broken(request):
        return list(Item.objects.all())

    with pytest.raises(TypeError, match="must return a QuerySet"):
        broken(get())
