import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from decimal import Decimal
from .models import Category, Product


class CategoryType(DjangoObjectType):
    product_count = graphene.Int(description="Number of products in this category")

    class Meta:
        model = Category
        fields = "__all__"
        description = "Just a category description"

    def resolve_product_count(self, info):
        return self.products.count()


class ProductType(DjangoObjectType):
    is_in_stock = graphene.Boolean()

    class Meta:
        model = Product
        fields = "__all__"
        description = "Just a Product description"

    def resolve_is_in_stock(self, info):
        return self.stock_quantity > 0


class Query(graphene.ObjectType):
    products = graphene.List(
        ProductType,
        name=graphene.String(),
        min_price=graphene.Decimal(),
        max_price=graphene.Decimal(),
        in_stock=graphene.Boolean(),
        description="List all the products"
    )

    product = graphene.Field(
        ProductType, id=graphene.ID(required=True), description="Get product by Id"
    )

    categories = graphene.List(CategoryType, description="List all the categories")

    category = graphene.Field(
        CategoryType, id=graphene.ID(required=True),
        description="Get category by Id"
    )

    def resolve_products(
            self,
            info,
            name=None,
            min_price=None,
            max_price=None,
            in_stock=None
            ):
        queryset = Product.objects.all()
        if name:
            queryset = queryset.filter(name__icontains=name)
        if min_price:
            queryset = queryset.filter(price__gte=Decimal(str(min_price)))
        if max_price:
            queryset = queryset.filter(price__lte=Decimal(str(min_price)))
        if in_stock:
            queryset = queryset.filter(stock_quantity_gt=0 if in_stock else 0)
        return queryset

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
        price = graphene.Decimal(required=True)
        sku = graphene.String(required=True)
        category_id = graphene.ID(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, description, price, category_id, sku):
        category = Category.objects.get(pk=category_id)
        product = Product.objects.create(
            name=name,
            description=description,
            price=Decimal(str(price)),
            category=category,
            sku=sku,
        )
        return CreateProduct(product=product)


class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()
        price = graphene.Decimal()
        category_id = graphene.ID()

    product = graphene.Field(ProductType)

    def mutate(
        self, info, id, name=None, descrption=None, price=None, category_id=None
    ):
        product = Product.objects.get(pk=id)
        if name:
            product.name = name
        if descrption:
            product.descrption = descrption
        if price:
            product.price = Decimal(str(price))
        if category_id:
            # ForeingKey
            product.category = Category.objects.get(pk=category_id)
        product.save()
        return UpdateProduct(product=product)


class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            product = Product.objects.get(pk=id)
            product.delete()
            return DeleteProduct(success=True)
        except Product.DoesNotExist:
            raise GraphQLError(f"Product with id: {id} does not exists")


class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    category = graphene.Field(CategoryType)

    def mutate(self, info, name):
        category = Category.objects.create(name=name)
        return CreateCategory(category=category)


class UpdateCategory(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)

    category = graphene.Field(CategoryType)

    def mutate(self, info, id, name):
        try:
            category = Category.objects.get(pk=id)
            category.name = name
            category.save()
            return UpdateCategory(category=category)
        except Category.DoesNotExist:
            raise GraphQLError(f"Category with id: {id} does not exists")


class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            product = Category.objects.get(pk=id)
            product.delete()
            return DeleteCategory(success=True)
        except Category.DoesNotExist:
            raise GraphQLError(f"Category with id: {id} does not exists")


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()

    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
