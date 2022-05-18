import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings

from ..forms import PostForm
from ..models import Follow, Group, Post
from ..views import POSTS_ON_PAGE


User = get_user_model()
TEST_POSTS_ON_PAGE_2 = 3
TEST_POSTS_ON_PAGE = POSTS_ON_PAGE + TEST_POSTS_ON_PAGE_2
TEST_ZERO = 0
TEST_ONE = 1
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая пост. Пост. Пост.",
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewTest.user)
        cache.clear()

    def tearDown(self) -> None:
        cache.clear()

    def test_pages_uses_correct_template(self):
        """Test template's reference's correct"""
        post = PostsViewTest.post
        group = PostsViewTest.group
        user = PostsViewTest.user
        dict_templates_view = {
            reverse("posts:post_create"): "posts/create_post.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": post.pk}
            ): "posts/create_post.html",
            reverse(
                "posts:group_list", kwargs={"slug": group.slug}
            ): "posts/group_list.html",
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": post.pk}
            ): "posts/post_detail.html",
            reverse(
                "posts:profile", kwargs={"username": user.get_username()}
            ): "posts/profile.html",
        }
        for reverse_name, template in dict_templates_view.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_correct_context_post_detail(self):
        """Test context in template post_detail is correct."""
        post = PostsViewTest.post
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": post.pk}),
        )
        self.assertEqual(response.context["post"], post)

    def test_correct_context_post_create(self):
        """Test context in template post_create is correct."""
        response = self.authorized_client.get(
            reverse("posts:post_create"),
        )
        self.assertIsInstance(response.context["form"], PostForm)

    def test_correct_context_post_edit(self):
        """Test context in template post_edit is correct."""
        post = PostsViewTest.post
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": post.pk}),
        )
        self.assertIn("form", response.context)

    def test_correct_image_view(self):
        """Test image in context several view-functions."""
        post = PostsViewTest.post
        group = PostsViewTest.group
        user = PostsViewTest.user
        url_list = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": group.slug}),
            reverse(
                "posts:profile",
                kwargs={"username": user.get_username()},
            ),
            reverse(
                "posts:profile", kwargs={"username": user.get_username()}
            ),
        ]
        for url in url_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                post_list = response.context.get("page_obj")
                single_post = post_list[0]
                self.assertEqual(single_post.image, post.image)


class PageViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="auth",
        )
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        number_of_posts = TEST_POSTS_ON_PAGE
        for post_num in range(number_of_posts):
            Post.objects.create(
                author=cls.user,
                text="Тестовая пост. Пост. Пост. %s" % post_num,
                group=cls.group,
            )

    def setUp(self) -> None:
        self.guest_client = Client()
        cache.clear()

    def tearDown(self) -> None:
        cache.clear()

    def test_correct_index(self):
        """Test context in template index is correct."""
        response = self.guest_client.get(
            reverse("posts:index"),
        )
        self.assertTrue(response.context["page_obj"])

    def test_correct_group_list(self):
        """Test context in template group_list is correct."""
        group = PageViewTest.group
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": group.slug}),
        )
        self.assertTrue(response.context["page_obj"])
        self.assertEqual(response.context.get(
            "group").title, "Тестовая группа")
        self.assertEqual(response.context.get("group").slug, "test_slug")
        self.assertEqual(response.context.get(
            "group").description, "Тестовое описание")

    def test_correct_profile(self):
        """Test context in template profile is correct."""
        user = PageViewTest.user
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": user.get_username()}),
        )
        self.assertTrue(response.context["page_obj"])
        self.assertEqual(response.context.get("author").username, "auth")

    def test_paginator_first_page(self):
        """Test the amount of posts on 1st page is correct."""
        urls_list = [
            reverse("posts:group_list", kwargs={
                    "slug": PageViewTest.group.slug}),
            reverse("posts:index"),
            reverse(
                "posts:profile",
                kwargs={"username": PageViewTest.user.get_username()},
            ),
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(len(response.context["page_obj"]), POSTS_ON_PAGE)

    def test_paginator_second_page(self):
        """Test the amount of posts on 2nd page is correct."""
        urls_list = [
            reverse("posts:group_list", kwargs={
                    "slug": PageViewTest.group.slug}),
            reverse("posts:index"),
            reverse(
                "posts:profile",
                kwargs={"username": PageViewTest.user.get_username()},
            ),
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url + "?page=2")
                self.assertEqual(
                    len(response.context["page_obj"]), TEST_POSTS_ON_PAGE_2)


class GroupViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.group_2 = Group.objects.create(
            title="Тестовая группа_2",
            slug="test_slug_2",
            description="Тестовое описание_2",
        )

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_shows_post_with_group_correctly(self):
        """Test proper view of the post's group."""
        urls_list = [
            reverse("posts:group_list", kwargs={
                    "slug": GroupViewTest.group.slug}),
            reverse("posts:index"),
            reverse(
                "posts:profile",
                kwargs={"username": GroupViewTest.user.get_username()},
            ),
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(len(response.context["page_obj"]), TEST_ZERO)
                post = Post.objects.create(
                    author=GroupViewTest.user,
                    text="Тестовая пост. Пост. Пост.",
                    group=GroupViewTest.group,
                )
                cache.clear()
                response = self.guest_client.get(url)
                self.assertEqual(len(response.context["page_obj"]), TEST_ONE)
                post.delete()

    def test_is_not_in_wrong_group(self):
        """Test if new post is in wrong_group"""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={
                    "slug": GroupViewTest.group_2.slug})
        )
        self.assertEqual(len(response.context["page_obj"]), TEST_ZERO)
        post = Post.objects.create(
            author=GroupViewTest.user,
            text="Тестовая пост. Пост. Пост.",
            group=GroupViewTest.group,
        )
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={
                    "slug": GroupViewTest.group_2.slug})
        )
        self.assertEqual(
            len(response.context["page_obj"]), TEST_ZERO, f'{post} не найден')


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="author")
        cls.follower = User.objects.create_user(username="follower")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text="Тестовая пост. Пост. Пост.",
            group=cls.group,
        )
        cls.follow = Follow.objects.create(
            author=cls.author,
            user=cls.follower,
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowViewTest.follower)

    def test_post_in_follow(self):
        """Test view post in posts:follow_index correctly."""
        posts_count = Post.objects.count()
        response = self.authorized_client.get(reverse("posts:follow_index"))
        post_list = response.context.get("page_obj")
        single_post = post_list[0]
        self.assertEqual(single_post, FollowViewTest.post)

        nonfollower = User.objects.create_user(username="nonfollower")
        self.authorized_client = Client()
        self.authorized_client.force_login(nonfollower)
        response = self.authorized_client.get(reverse("posts:follow_index"))
        posts_count_delayed = Post.objects.count()
        self.assertEqual(posts_count, posts_count_delayed)

    def test_follow_unfollow(self):
        """Test follow (within self&double follow prohibited) and unfollow."""
        author = FollowViewTest.author
        follower = FollowViewTest.follower
        follow_filtered = Follow.objects.filter(
            author=author,
            user=follower,
        )
        follow_count = follow_filtered.count()
        self.authorized_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": author.get_username()}
            )
        )
        follow_count_delayed = follow_filtered.count()
        self.assertEqual(follow_count, follow_count_delayed)
        self.assertTrue(follow_filtered.exists())

        self.authorized_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": author.get_username()}
            )
        )
        follow_count_delayed = follow_filtered.count()
        self.assertEqual(follow_count, follow_count_delayed + TEST_ONE)
        self.assertFalse(follow_filtered.exists())

        self.authorized_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": author.get_username()}
            )
        )
        follow_count_delayed = follow_filtered.count()
        self.assertEqual(follow_count, follow_count_delayed)
        self.assertTrue(follow_filtered.exists())

        self.authorized_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": follower.get_username()}
            )
        )
        self_follow = Follow.objects.filter(
            user=follower,
            author=follower
        )
        self.assertFalse(self_follow.exists())
