from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import CartItem, Product
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import render_template
import json

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/", methods=["GET"])
@jwt_required()
def view_cart():
    identity = json.loads(get_jwt_identity())  # FIX: decode JWT string
    user_id = identity["id"]
    items = CartItem.query.filter_by(user_id=user_id).all()
    out = []
    for it in items:
        p = Product.query.get(it.product_id)
        out.append({
            "cart_item_id": it.id,
            "product_id": it.product_id,
            "product_name": p.name if p else None,
            "quantity": it.quantity,
            "price": float(p.price) if p else None
        })
    return jsonify({"items": out})

@cart_bp.route("/add", methods=["POST"])
@jwt_required()
def add_to_cart():
    identity = json.loads(get_jwt_identity())  # FIX: decode JWT string
    user_id = identity["id"]
    data = request.get_json() or {}
    product_id = data.get("product_id")
    qty = data.get("quantity", 1)
    if isinstance(qty, bool) or not isinstance(qty, int) or qty < 1:
        return jsonify({"msg": "quantity must be a positive integer"}), 400
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg":"product not found"}), 404
    existing = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    new_quantity = qty + (existing.quantity if existing else 0)
    if new_quantity > product.stock:
        return jsonify({"msg": "requested quantity exceeds available stock"}), 400
    if existing:
        existing.quantity = new_quantity
    else:
        existing = CartItem(user_id=user_id, product_id=product_id, quantity=qty)
        db.session.add(existing)
    db.session.commit()
    return jsonify({"msg":"added"}), 200

@cart_bp.route("/remove/<int:cart_id>", methods=["DELETE"])
@jwt_required()
def remove_from_cart(cart_id):
    identity = json.loads(get_jwt_identity())  # FIX: decode JWT string
    user_id = identity["id"]
    it = CartItem.query.filter_by(id=cart_id, user_id=user_id).first_or_404()
    db.session.delete(it)
    db.session.commit()
    return jsonify({"msg":"removed"}), 200

@cart_bp.route("/view_cart_page")
@jwt_required()
def view_cart_page():
    identity = json.loads(get_jwt_identity())
    user_id = identity["id"]
    items = CartItem.query.filter_by(user_id=user_id).all()
    
    out = []
    for it in items:
        p = Product.query.get(it.product_id)
        out.append({
            "id": it.id,
            "product_name": p.name if p else None,
            "quantity": it.quantity,
            "price": float(p.price) if p else None
        })
    return render_template("cart.html", cart_items=out)
