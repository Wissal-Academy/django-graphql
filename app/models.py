from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class WaBaseModel(models.Model):
    create_at = models.DateTimeField(_("Create at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        abstract = True


class Category(WaBaseModel):
    """
    _('') == For using mutliple languages
    """

    name = models.CharField(
        _("Name"),
        max_length=200,
        blank=True,
        help_text=_("The name of the category that you wish to be displayed"),
    )
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        """
        Order by name
        Indexes for DB optimization
        """

        verbose_name_plural = "Categories"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"]), models.Index(fields=["is_active"])]

    def __str__(self):
        return f"{self.name}"


class Product(WaBaseModel):
    name = models.CharField(
        _("Name"),
        max_length=200,
        blank=True,
        help_text=_("The name of the product that you wish to be displayed"),
    )
    description = models.TextField(_("Description"), blank=True)
    price = models.DecimalField(
        _("Price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.1"))],
    )
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    sku = models.CharField(_("SKU"), max_length=200, unique=True)
    stock_quantity = models.PositiveIntegerField(_("Stock Quanitity"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        """
        Ordering = ["FIELD"] From oldest to new
        Ordering = ["-FIELD"] From last created to old
        """

        ordering = ["-create_at"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} | {self.sku}"

    def is_in_stock(self) -> bool:
        # True / False
        return self.stock_quantity > 0

    def update_stock(self, qte: int) -> None:
        new_qte = self.stock_quantity + qte
        if new_qte < 0:
            raise ValueError("Stock can't be negative")
        self.stock_quantity = new_qte
        self.save()
