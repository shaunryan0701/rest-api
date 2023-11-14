import unittest
from app import create_app, db
from models import ItemModel

class TestItemAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            item = ItemModel(name='test item', price=10.99)
            db.session.add(item)
            db.session.commit()
            self.item_id = item.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_item(self):
        response = self.client.get(f'/item/{self.item_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'test item')
        self.assertEqual(response.json['price'], 10.99)

    def test_delete_item(self):
        response = self.client.delete(f'/item/{self.item_id}')
        self.assertEqual(response.status_code, 501)

    def test_update_item(self):
        data = {'name': 'updated item', 'price': 15.99}
        response = self.client.put(f'/item/{self.item_id}', json=data)
        self.assertEqual(response.status_code, 501)

if __name__ == '__main__':
    unittest.main()