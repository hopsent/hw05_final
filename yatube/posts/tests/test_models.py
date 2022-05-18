from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import TEXT_LENGTH, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_models_have_correct_object_names(self):
        """Test proper work of '__str__'."""
        post = PostModelTest.post
        group = PostModelTest.group
        objects_dict = {
            f'{post.text[:TEXT_LENGTH]}': post,
            f'{group.title}': group,
        }
        for value, object in objects_dict.items():
            with self.subTest(object=object):
                result = str(object)
                self.assertEqual(result, value)
