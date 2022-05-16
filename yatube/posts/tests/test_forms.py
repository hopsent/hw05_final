import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

from posts.models import Post, Group, Comment
from posts.forms import PostForm


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post_create_comment(self):
        """Test form creates new Post.object, create new Comment.Object."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small_1.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.assertFalse(
            Post.objects.filter(
                text="Тестовый текст тестового поста",
                group=PostCreateFormTests.group.pk,
                author=PostCreateFormTests.user,
                image=uploaded,
            ).exists()
        )
        form_data = {
            "text": "Тестовый текст тестового поста",
            "group": PostCreateFormTests.group.pk,
            "image": uploaded,
        }
        self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        post = Post.objects.latest("pub_date")
        post_data = {
            post.text: form_data["text"],
            post.group.pk: form_data["group"],
            post.author: PostCreateFormTests.user,
            post.image: 'posts/small_1.gif',
        }
        for datum, value in post_data.items():
            with self.subTest(datum=datum):
                self.assertEqual(datum, value)
        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertFalse(
            Comment.objects.filter(
                text="Тестовый текст комментария",
                author=PostCreateFormTests.user,
                post=post.pk,
            ).exists()
        )
        comments_count = Comment.objects.count()
        data_for_comment = {
            "text": "Тестовый текст комментария",
        }
        self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": post.pk}),
            data=data_for_comment,
            post=post.pk,
            follow=True,
        )
        comment = Comment.objects.latest("created")
        comment_data = {
            comment.text: data_for_comment["text"],
            comment.post.pk: post.pk,
            comment.author: PostCreateFormTests.user,
        }
        for field, value in comment_data.items():
            with self.subTest(field=field):
                self.assertEquals(field, value)
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_edit_post(self):
        """Test form edites Post.object."""
        small_gif_2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small_2.gif',
            content=small_gif_2,
            content_type='image/gif'
        )
        post = Post.objects.create(
            author=PostCreateFormTests.user,
            text="Тестовая пост. Пост. Пост.",
            group=PostCreateFormTests.group,
            image=uploaded,
        )
        self.assertTrue(Post.objects.filter(
            text="Тестовая пост. Пост. Пост.",
            group=PostCreateFormTests.group.pk,
            pub_date=post.pub_date,
            author=post.author,
            image='posts/small_2.gif',
        ).exists()
        )
        posts_count = Post.objects.count()
        small_gif_3 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_1 = SimpleUploadedFile(
            name='small_3.gif',
            content=small_gif_3,
            content_type='image/gif',
        )
        group_1 = Group.objects.create(
            title="Тестовая группа_1",
            slug="test_slug_1",
            description="Тестовое описание_1",
        )
        form_data = {
            "text": "Тестовый текст",
            "group": group_1.pk,
            "image": uploaded_1,
        }
        self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": post.pk}),
            data=form_data,
            follow=True,
        )
        post_filtered = Post.objects.get(pk=post.pk)
        post_filtered_data = {
            post_filtered.text: form_data["text"],
            post_filtered.group.pk: form_data["group"],
            post_filtered.pub_date: post.pub_date,
            post_filtered.author: post.author,
            post_filtered.image: 'posts/small_3.gif',
        }
        for datum, value in post_filtered_data.items():
            with self.subTest(datum=datum):
                self.assertEquals(datum, value)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_title_label(self):
        form = PostCreateFormTests.form
        test_labels = {
            form.fields['text'].label: "Текст поста",
            form.fields['group'].label: "Group",
            form.fields['image'].label: "Picture",
        }
        for field, value in test_labels.items():
            with self.subTest(field=field):
                self.assertEquals(field, value)

    def test_title_help_text(self):
        form = PostCreateFormTests.form
        test_help_text = {
            form.fields['text'].help_text: "Текст нового поста",
            form.fields['group'].help_text: "Выберите группу",
            form.fields['image'].help_text: "Добавьте картинку",
        }
        for field, value in test_help_text.items():
            with self.subTest(field=field):
                self.assertEquals(field, value)
