from django.db import models
from django.contrib.auth import get_user_model

from posts.validators import validate_not_empty


User = get_user_model()
TEXT_LENGTH = 15


class Group(models.Model):
    """Stores groups"""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return str(self.title)


class Post(models.Model):
    """
    Stores posts, related to :model:'posts.Group'
    and :model:'posts.User'.
    """

    text = models.TextField(validators=[validate_not_empty])
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="posts",
        null=True,
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
    )
    image = models.ImageField(
        "Картинка",
        upload_to="posts/",
        blank=True,
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self) -> str:
        return str(self.text[:TEXT_LENGTH])


class Comment(models.Model):
    """
    Stores comments, related to :model:'posts.User'
    and :model:'posts.Post'.
    """

    text = models.TextField(validators=[validate_not_empty])
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
    )


class Follow(models.Model):
    """
    Stores follow, a relatinship between :model:'posts.User'
    as authorised user and :model:'posts.User' as
    :model:'posts.Post' instance author.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
    )
