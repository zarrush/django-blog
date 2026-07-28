from django.forms import ModelForm
from .models import Comment


# Define a ModelForm for creating new blog comments.
class CommentForm(ModelForm):

    class Meta:
        # Specify the model and expose only the fields required for user input.
        model = Comment
        fields = ['name', 'email', 'body']