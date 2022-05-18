from django.forms import ModelForm

from posts.models import Post, Comment


class PostForm(ModelForm):
    """
    Shapes a form related to
    :model:'posts.Post'.
    """

    class Meta:
        model = Post
        fields = (
            "text",
            "group",
            "image",
        )
        labels = {
            "text": "Текст поста",
            "group": "Group",
            "image": "Picture",
        }
        help_texts = {
            "text": "Текст нового поста",
            "group": "Выберите группу",
            "image": "Добавьте картинку",
        }


class CommentForm(ModelForm):
    """
    Shapes a form related to
    :model:'posts.Comment'.
    """

    class Meta:
        model = Comment
        fields = ("text",)
        labels = {
            "text": "Текст комментария",
        }
        help_texts = {
            "text": "Текст нового комментария",
        }
