from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Product, Category
from django.conf import settings
import tempfile
import shutil
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


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


class TestCategoryAndImagesAPI(APITestCase):
    def setUp(self):
        # Use a temp media directory for file uploads
        self._old_media = settings.MEDIA_ROOT
        self._tmpdir = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._tmpdir
        self.categories_url = "/api/categories/"
        self.products_url = "/api/products/"

    def tearDown(self):
        settings.MEDIA_ROOT = self._old_media
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def _make_image(self, name="test.png", size=(2, 2), color=(255, 0, 0)):
        buf = BytesIO()
        Image.new("RGB", size, color).save(buf, format="PNG")
        buf.seek(0)
        return SimpleUploadedFile(name, buf.read(), content_type="image/png")

    def test_category_crud_with_image(self):
        # Create
        img = self._make_image("cat.png")
        create = self.client.post(self.categories_url, {"name": "Electronics", "image": img}, format="multipart")
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        cid = create.data["id"]
        self.assertTrue(create.data.get("slug"))
        # List
        listed = self.client.get(self.categories_url)
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(listed.data["count"], 1)
        # Retrieve
        detail_url = f"{self.categories_url}{cid}/"
        retrieve = self.client.get(detail_url)
        self.assertEqual(retrieve.status_code, status.HTTP_200_OK)
        # Update
        patch = self.client.patch(detail_url, {"name": "Gadgets"}, format="json")
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        # Delete
        delete = self.client.delete(detail_url)
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(detail_url).status_code, status.HTTP_404_NOT_FOUND)

    def test_product_create_with_category_and_image(self):
        # Create category
        cat = self.client.post(self.categories_url, {"name": "Accessories"}, format="multipart").data
        # Create product
        pimg = self._make_image("p.png")
        payload = {
            "name": "Headphones",
            "description": "",
            "price": "49.99",
            "category_id": cat["id"],
            "image": pimg,
        }
        created = self.client.post(self.products_url, payload, format="multipart")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertTrue(created.data.get("slug"))
        self.assertIsNotNone(created.data.get("category"))
        # List
        listed = self.client.get(self.products_url)
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(listed.data["count"], 1)
