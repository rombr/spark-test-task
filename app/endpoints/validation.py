import datetime

from werkzeug.datastructures import MultiDict
from wtforms.validators import ValidationError, Optional
from wtforms.ext.sqlalchemy.orm import model_form

from app.models.products import Product, Brand, Category
from app import db


def expiration_date_check(form, field):
    if not field.data:
        return

    if field.data < (
        datetime.datetime.utcnow() + datetime.timedelta(days=30)
    ):
        raise ValidationError(
            'must expire not less than 30 days since now.'
        )


CreateProductForm = model_form(
    Product,
    db_session=db.session,
    only=(
        'name', 'rating', 'receipt_date',
        'categories', 'expiration_date', 'featured',
        'items_in_stock',
        'brand_id',  # Не прокинулось в форму
        'categories',  # Не прокинулось в форму
    ),
    field_args={
        'expiration_date': {
            'validators': [expiration_date_check],
        },
        'featured': {
            'validators': [Optional()],
        },
    }
)


EditProductForm = model_form(
    Product,
    db_session=db.session,
    only=(
        'name', 'rating', 'receipt_date',
        'categories', 'expiration_date', 'featured',
        'items_in_stock',
        'brand_id',  # Не прокинулось в форму
        'categories',  # Не прокинулось в форму
    ),
    field_args={
        'expiration_date': {
            'validators': [expiration_date_check],
        },
        'featured': {
            'validators': [Optional()],
        },
        'items_in_stock': {
            'validators': [Optional()],
        },
    }
)


def validate_product(input_data, obj, edit=False):
    errors = {}
    input_data = input_data or {}
    ProductForm = EditProductForm if edit else CreateProductForm

    brand_id = input_data.pop('brand_id', None)
    brand = Brand.query.get(brand_id) if brand_id else None
    if not brand and not edit:
        errors['brand_id'] = ['brand_id is invalid']

    categories_ids = input_data.pop('categories', [])
    categories = (
        Category.query.filter(Category.id.in_(categories_ids)).all()
        if categories_ids else []
    )
    future_categories_ids = set([o.id for o in obj.categories + categories])
    if not (1 <= len(future_categories_ids) <= 5):
        errors['categories'] = ['A product must have from 1 to 5 categories']

    # Clean null
    form_data = {k: v for k, v in input_data.items() if v is not None}
    form = ProductForm(
        MultiDict(mapping=form_data),
        obj=obj
    )
    if form.validate():
        form.populate_obj(obj)
    else:
        errors.update(form.errors)

    if brand:
        obj.brand_id = brand.id

    if categories:
        obj.categories += categories

    if obj.rating and obj.rating > 8:
        obj.featured = True

    return errors, obj
