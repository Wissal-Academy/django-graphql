import graphene
from graphene_django import DjangoConnectionField
from graphql import GraphQLError

from .types import ProductType, CategoryType
from ..models import Product, Category


class Query(graphene.ObjectType):
    # PRODUCTS
    products = DjangoConnectionField(
        ProductType,
        description="List all the products with pagination and filtering",
        active=graphene.Boolean(description="Filter by active Status"),
    )

    product = graphene.Field(
        ProductType, id=graphene.ID(required=True), description="Get product by Id"
    )

    # resolve_product --> product
    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            raise GraphQLError(f"Product with {id} does not exist")

    # CATEGORIES
    categories = DjangoConnectionField(
        CategoryType,
        description="List all the categories with pagination and filtering",
        active=graphene.Boolean(description="Filter by active Status"),
    )

    category = graphene.Field(
        CategoryType, id=graphene.ID(required=True), description="Get category by Id"
    )

    # resolve_category --> category
    def resolve_category(self, info, id):
        try:
            return Category.objects.get(pk=id)
        except Category.DoesNotExist:
            raise GraphQLError(f"Category with {id} does not exist")


schema = graphene.Schema(query=Query)
