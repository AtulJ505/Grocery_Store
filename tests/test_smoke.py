import pytest
from app.extensions import db
from app.models import Product


def test_products_empty_catalog(client):
    response = client.get('/api/products/')
    assert response.status_code == 200
    assert response.get_json() == {'products': [], 'page': 1, 'pages': 0, 'total': 0}


@pytest.mark.parametrize('query', ['page=abc', 'page=0', 'page=-1', 'per_page=0', 'per_page=101', 'per_page=abc'])
def test_invalid_pagination_returns_400(client, query):
    assert client.get('/api/products/?' + query).status_code == 400


def test_search_returns_matching_products(client, app):
    with app.app_context():
        db.session.add_all([Product(name='Apple', price=2, stock=5), Product(name='Bread', price=3, stock=4)])
        db.session.commit()
    result = client.get('/api/products/?q=apple').get_json()
    assert result['total'] == 1
    assert result['products'][0]['name'] == 'Apple'


@pytest.fixture
def customer(client):
    response = client.post('/api/auth/register', json={'email': 'test@example.com', 'password': 'test-only-password'})
    assert response.status_code == 201
    return {'Authorization': 'Bearer ' + response.get_json()['access_token']}


@pytest.fixture
def product_id(app):
    with app.app_context():
        product = Product(name='Apples', price=2, stock=5)
        db.session.add(product)
        db.session.commit()
        return product.id


@pytest.mark.parametrize('quantity', [0, -1, 1.5, '2', None, True, {}, 6])
def test_invalid_cart_quantity_does_not_modify_cart(client, customer, product_id, quantity):
    response = client.post('/api/cart/add', headers=customer, json={'product_id': product_id, 'quantity': quantity})
    assert response.status_code == 400
    assert client.get('/api/cart/', headers=customer).get_json()['items'] == []


def test_cart_repeated_add_respects_stock(client, customer, product_id):
    def add(qty):
        return client.post('/api/cart/add', headers=customer, json={'product_id': product_id, 'quantity': qty})
    assert add(3).status_code == 200
    assert add(3).status_code == 400
    items = client.get('/api/cart/', headers=customer).get_json()['items']
    assert items[0]['quantity'] == 3
    assert add(2).status_code == 200
    assert client.get('/api/cart/', headers=customer).get_json()['items'][0]['quantity'] == 5
