from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text="Тестовая пост. Пост. Пост.",
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTest.user)
        cache.clear()

    def tearDown(self) -> None:
        cache.clear()

    def test_urls_exist_guest(self):
        """Test urls in posts guest client."""
        urls_list = [
            "/",
            f"/group/{PostsURLTest.group.slug}/",
            f"/profile/{PostsURLTest.user.get_username()}/",
            f"/posts/{PostsURLTest.post.pk}/",
        ]
        for request in urls_list:
            with self.subTest(request=request):
                response = self.guest_client.get(request)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_url(self):
        """Test url not found in posts."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")

    def test_url_create__edit_post(self):
        """Test creating and editing post."""
        urls_list = [
            "/create/",
            f"/posts/{PostsURLTest.post.pk}/edit/",
        ]
        for request in urls_list:
            with self.subTest(request=request):
                response = self.authorized_client.get(request)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect_post_guest(self):
        """Test redirect guest creating, commenting and editing post."""
        post = PostsURLTest.post
        dict_urls = {
            "/create/": "/auth/login/?next=/create/",
            f"/posts/{post.pk}/edit/": 
            f"/auth/login/?next=/posts/{post.pk}/edit/",
            f"/posts/{post.pk}/comment/": 
            f"/auth/login/?next=/posts/{post.pk}/comment/",
        }
        for url, redirect_url in dict_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_url_redirect_post_comment_create_authorized(self):
        """Test redirect authorized creating, commenting post."""
        form_data = {
            "text": "Тестовый текст",
            "group": PostsURLTest.group.pk,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile",
                kwargs={"username": PostsURLTest.user.get_username()},
            ),
        )
        post = Post.objects.latest("pub_date")
        comment_data = {
            "text": "Тестовый комментарий",
        }
        response_comment = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": post.pk}),
            data=comment_data,
            follow=True,
            post=post.pk,
        )
        self.assertRedirects(
            response_comment, reverse("posts:post_detail", kwargs={"post_id": post.pk})
        )

    def test_url_redirect_post_edit_authorized(self):
        """Test redirect authorized editing post."""
        post = PostsURLTest.post
        group_1 = Group.objects.create(
            title="Тестовая группа_1",
            slug="test_slug_1",
            description="Тестовое описание_1",
        )
        form_data = {
            "text": "Тестовый текст",
            "group": group_1.pk,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={"post_id": post.pk},
            ),
        )

    def test_using_templates_correctly(self):
        """Test url uses template properly."""
        post = PostsURLTest.post
        user = PostsURLTest.user
        dict_templates_url = {
            "/create/": "posts/create_post.html",
            f"/posts/{post.pk}/edit/": "posts/create_post.html",
            f"/group/{PostsURLTest.group.slug}/": "posts/group_list.html",
            "/": "posts/index.html",
            f"/posts/{post.pk}/": "posts/post_detail.html",
            f"/profile/{user.get_username()}/": "posts/profile.html",
        }
        for address, template in dict_templates_url.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
