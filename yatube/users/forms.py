from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    """Define a form to create users."""

    class Meta(UserCreationForm.Meta):
        """Customize form's parameters."""

        model = User
        fields = ("first_name", "last_name", "username", "email")
