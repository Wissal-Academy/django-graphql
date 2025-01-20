import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import Category, Product


class CategoryType(DjangoObjectType):
    product_count = graphene.Int(description="Number of products in this category")

    class Meta:
        model = Category
        fields = '__all__'
        description = 'Just a category description'

    def resolve_product_count(self, info):
        return self.products.count()


class ProductType(DjangoObjectType):
    is_in_stock = graphene.Boolean()

    class Meta:
        model = Product
        fields = '__all__'
        description = 'Just a Product description'

    def resolve_is_in_stock(self, info):
        return self.stock_quantity > 0


class Query(graphene.ObjectType):
    products = graphene.List(
        ProductType,
        description="List all the products"
    )
    
    product = graphene.Field(
        ProductType,
        id=graphene.ID(required=True),
        description="Get product by Id"
    )

    categories = graphene.List(
        CategoryType,
        description="List all the categories"
    )
    
    category = graphene.Field(
        CategoryType,
        id=graphene.ID(required=True),
        description="Get category by Id"
    )

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            raise GraphQLError(f"Product with id {id} does not exist")

    def resolve_categories(self, info):
        return Category.objects.all()

    def resolve_category(self, info, id):
        try:
            return Category.objects.get(pk=id)
        except Category.DoesNotExist:
            raise GraphQLError(f"Category with id {id} does not exist")


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        price = graphene.Float(required=True)
        sku = graphene.String(required=True)
        category_id = graphene.ID(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, description, price, category_id, sku):
        category = Category.objects.get(pk=category_id)
        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            category=category,
            sku=sku
        )
        return CreateProduct(product=product)


class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    category = graphene.Field(CategoryType)

    def mutate(self, info, name):
        category = Category.objects.create(name=name)
        return CreateCategory(category=category)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    create_category = CreateCategory.Field()


schema = graphene.Schema(
    query=Query,
    mutation=Mutation
)
