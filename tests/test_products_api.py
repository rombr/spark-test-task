import json
import datetime

from sqlalchemy.sql import insert
from flask import url_for

from app.models.products import Product, Brand, Category


def create_fixture_data(session):
    brands = Brand.metadata.tables['brands']
    categories = Category.metadata.tables['categories']
    products = Product.metadata.tables['products']
    products_categories = Product.metadata.tables['products_categories']

    brands_data = [
        {'name': 'Apple', 'country_code': 'US'},
        {'name': 'Milka', 'country_code': 'DE'}
    ]

    categories_data = [
        {'name': 'Mobile phones'},
        {'name': 'Food'}
    ]

    products_data = [
        {
            'name': 'iPhone', 'rating': 10, 'featured': True,
            'items_in_stock': 10, 'receipt_date': None,
            'created_at': datetime.datetime.utcnow()
        },
        {
            'name': 'Chocolate', 'rating': 7, 'featured': False,
            'items_in_stock': 0,
            'receipt_date': (
                datetime.datetime.utcnow() +
                datetime.timedelta(days=10)
            ),
            'created_at': datetime.datetime.utcnow()
        }
    ]

    # insert initial brands
    for brand in brands_data:
        result = session.execute(insert(brands).values(brand))
        brand['id'] = result.lastrowid

    # insert initial categories
    for category in categories_data:
        result = session.execute(insert(categories).values(category))
        category['id'] = result.lastrowid

    # insert initial products
    for i, product in enumerate(products_data):
        product['brand_id'] = brands_data[i]['id']
        result = session.execute(insert(products).values(product))
        product['id'] = result.lastrowid

        # associate product with a category
        session.execute(insert(products_categories).values({
            'product_id': product['id'],
            'category_id': categories_data[i]['id']
        }))

    session.commit()


def test_products_empty_list(client):
    url = url_for('products.get_products')

    with client as c:
        response = c.get(url)

        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert json_data['results'] == []


def test_products_list(client, session):
    create_fixture_data(session)

    url = url_for('products.get_products')

    with client as c:
        response = c.get(url)

        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert len(json_data['results']) == 2


def test_product_details_not_exists(client):

    url = url_for('products.get_product', product_id=1)

    with client as c:
        response = c.get(url)

        assert response.status_code == 404


def test_product_details(client, session):
    create_fixture_data(session)

    url = url_for('products.get_product', product_id=1)

    with client as c:
        response = c.get(url)

        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert json_data['id'] == 1


def test_product_delete(client, session):
    create_fixture_data(session)

    url = url_for('products.delete_product', product_id=1)

    with client as c:
        response = c.delete(url)

        assert response.status_code == 204


def test_product_delete_not_exists(client):
    url = url_for('products.delete_product', product_id=1)

    with client as c:
        response = c.delete(url)

        assert response.status_code == 204


def test_product_create(client, session):
    create_fixture_data(session)

    url = url_for('products.create_product')

    with client as c:
        response = c.post(
            url,
            json={
                'brand_id': 1,
                'categories': [1],
                'expiration_date': None,
                'featured': True,
                'items_in_stock': 10,
                'name': 'oPhone',
                'rating': 10.0,
                'receipt_date': None
            },
        )

        assert response.status_code == 201
        json_data = json.loads(response.data)
        assert json_data['id'] == 3
        assert json_data['name'] == 'oPhone'
        assert len(json_data['categories']) == 1


def test_product_create_with_invalid_field_name(client, session):
    create_fixture_data(session)

    url = url_for('products.create_product')

    with client as c:
        # Name length
        response = c.post(
            url,
            json={
                'brand_id': 1,
                'categories': [1],
                'expiration_date': None,
                'featured': True,
                'items_in_stock': 10,
                'name': 'o' * 60,
                'rating': 10.0,
                'receipt_date': None
            },
        )

        assert response.status_code == 400
        json_data = json.loads(response.data)
        assert 'name' in json_data['errors']
        assert json_data['errors']['name'][0] == (
            'Field cannot be longer than 50 characters.'
        )


def test_product_create_with_invalid_field_categories(client, session):
    create_fixture_data(session)

    url = url_for('products.create_product')

    with client as c:
        # A product must have from 1 to 5 categories.

        response = c.post(
            url,
            json={
                'brand_id': 1,
                'categories': [],
                'expiration_date': None,
                'featured': True,
                'items_in_stock': 10,
                'name': 'oPhone',
                'rating': 10.0,
                'receipt_date': None
            },
        )

        assert response.status_code == 400
        json_data = json.loads(response.data)
        assert 'categories' in json_data['errors']
        assert json_data['errors']['categories'][0] == (
            'A product must have from 1 to 5 categories'
        )


def test_product_create_with_invalid_field_expiration_date(client, session):
    create_fixture_data(session)

    url = url_for('products.create_product')

    with client as c:
        # If a product has an expiration date it must expire not
        # less than 30 days since now.
        response = c.post(
            url,
            json={
                'brand_id': 1,
                'categories': [1],
                'expiration_date': datetime.datetime.utcnow().strftime(
                    '%Y-%m-%d %H:%M:%S'
                ),
                'featured': True,
                'items_in_stock': 10,
                'name': 'oPhone',
                'rating': 10.0,
                'receipt_date': None
            },
        )

        assert response.status_code == 400
        json_data = json.loads(response.data)
        assert json_data['errors']['expiration_date'][0] == (
            'must expire not less than 30 days since now.'
        )


def test_product_update_not_exists(client, session):
    create_fixture_data(session)

    url = url_for('products.update_product', product_id=7)

    with client as c:
        response = c.put(url)

        assert response.status_code == 404


def test_product_update(client, session):
    create_fixture_data(session)

    url = url_for('products.update_product', product_id=2)

    with client as c:
        response = c.put(
            url,
            json={
                'rating': 11.0,
            },
        )

        assert response.status_code == 200, response.data
        json_data = json.loads(response.data)
        assert json_data['rating'] == 11.0
        assert json_data['featured'] is True
