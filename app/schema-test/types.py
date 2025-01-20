import graphene
from graphene_django import DjangoObjectType

from ..models import Category, Product


class CategoryType(DjangoObjectType):
    """
        Definition

    """
    product_count = graphene.Int(
        description="Number of products in this category"
        )

    class Meta:
        model = Category
        fields = '__all__'
        description = 'Just a category description'

    def resolve_product_count(self, info):
        # resolve_<name_of_the_function> --> nameOfTheFunction :: GraphQL
        return self.products.count()


class ProductType(DjangoObjectType):
    is_in_stock = graphene.Boolean()

    class Meta:
        model = Product
        fields = '__all__'
        description = 'Just a Product description'

    def resolve_is_in_stock(self, info):
        return self.stock_quantity > 0
