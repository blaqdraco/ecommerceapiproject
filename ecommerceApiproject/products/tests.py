from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Product


class TestProductAPI(APITestCase):
    def setUp(self):
        self.list_url = "/api/products/"

    def test_list_products_empty(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 0)
        self.assertEqual(resp.data["results"], [])

    def test_create_and_retrieve_product(self):
        payload = {
            "name": "Test Product",
            "description": "A thing",
            "price": "19.99",
        }
        create = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        pid = create.data["id"]

        # list should have 1 item
        list_resp = self.client.get(self.list_url)
        self.assertEqual(list_resp.data["count"], 1)

        # retrieve
        detail_url = f"{self.list_url}{pid}/"
        retrieve = self.client.get(detail_url)
        self.assertEqual(retrieve.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve.data["name"], payload["name"])

    def test_update_and_delete_product(self):
        p = Product.objects.create(name="Old", description="", price=5)
        detail_url = f"{self.list_url}{p.id}/"

        update = self.client.patch(detail_url, {"name": "New"}, format="json")
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        self.assertEqual(update.data["name"], "New")

        delete = self.client.delete(detail_url)
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure it's gone
        get_missing = self.client.get(detail_url)
        self.assertEqual(get_missing.status_code, status.HTTP_404_NOT_FOUND)
