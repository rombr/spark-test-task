from flask import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload

from app.models.products import Product
from app import db
from .validation import validate_product


products_blueprint = Blueprint('products', __name__)


@products_blueprint.route('/products', methods=['GET'])
def get_products():
    return jsonify({
        'results': [
            p.serialized for p in Product.query.options(
                joinedload('categories'), joinedload('brand'),
            ).all()
        ]
    })


@products_blueprint.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    return jsonify(
        Product.query.options(
            joinedload('categories'), joinedload('brand'),
        ).get_or_404(product_id).serialized
    )


@products_blueprint.route('/products', methods=['POST'])
def create_product():
    errors, item = validate_product(request.json, Product())

    if errors:
        return jsonify(errors=errors), 400

    db.session.add(item)
    db.session.commit()
    return jsonify(item.serialized), 201


@products_blueprint.route(
    '/products/<int:product_id>',
    methods=['PUT', 'PATCH']
)
def update_product(product_id):
    item = Product.query.options(
        joinedload('categories'), joinedload('brand'),
    ).get_or_404(product_id)

    errors, item = validate_product(request.json, item, edit=True)

    if errors:
        return jsonify(errors=errors), 400

    db.session.add(item)
    db.session.commit()

    return jsonify(item.serialized)


@products_blueprint.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    item = Product.query.get(product_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return '', 204
