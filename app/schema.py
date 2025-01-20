import graphene
from graphene import relay
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphql import GraphQLError

from .models import Category, Product


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
        filter_fields = ['name']
        interfaces = (relay.node, )

    def resolve_product_count(self, info):
        return self.products.count()


class ProductType(DjangoObjectType):
    is_in_stock = graphene.Boolean()

    class Meta:
        model = Product
        fields = '__all__'
        description = 'Just a Product description'
        filter_fields = ['name']
        interfaces = (relay.node, )

    def resolve_is_in_stock(self, info):
        return self.stock_quantity > 0


class Query(graphene.ObjectType):

    node = relay.Node.Field()

    products = DjangoConnectionField(
        ProductType,
        description="List all the products with pagination and filtering",
        active=graphene.Boolean(description="Filter by active Status")
    )

    product = graphene.Field(
        ProductType,
        id=graphene.ID(required=True),
        description="Get product by Id"
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
        active=graphene.Boolean(description="Filter by active Status")
    )

    category = graphene.Field(
        CategoryType,
        id=graphene.ID(required=True),
        description="Get category by Id"
    )

    # resolve_category --> category
    def resolve_category(self, info, id):
        try:
            return Category.objects.get(pk=id)
        except Category.DoesNotExist:
            raise GraphQLError(f"Category with {id} does not exist")


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        price = graphene.Float(required=True)
        category_id = graphene.Int(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info , name, description, price, category_id):
        product = Product(
            name=name,
            description=description,
            price=price,
            category=category_id
        )
        product.save()
        return CreateProduct(product=product)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()


schema = graphene.Schema(
    query=Query,
    mutation=Mutation
)
