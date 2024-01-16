from django import forms
from .models import *
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
# Create your Forms here

# class Addpost(forms.ModelForm):
#     class Meta:
#         model=Blogpost
#         fields ="__all__"

# class BlogPos(forms.Form):
#     name = forms.CharField()
#     phone = forms.IntegerField()
#     email = forms.EmailField()


class NewPostForm(forms.ModelForm):
    picture = forms.ImageField(required=True)
    caption = forms.CharField(widget=forms.Textarea(attrs={'class':'post-input', 'placeholder': 'Caption', 'rows' : '1'}), required=True)
    tag = forms.CharField(widget=forms.TextInput(attrs={'class': 'tag-input', 'placeholder': '# Tags'}), required=True)
    picture = forms.ImageField(required=True, widget=forms.ClearableFileInput(attrs={'class': 'image-input'}))
    class Meta:
        model = Post
        fields = ['picture', 'caption', 'tag']


class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields='__all__'

class TweetForm(forms.ModelForm):
    class Meta:
        model=Tweet
        fields=['tweet']
        
class ReplyForm(forms.ModelForm):
    class Meta:
        model=Reply
        fields='__all__'

class EditProfileForm(forms.ModelForm):
    picture = forms.ImageField(required=True)
    first_name = forms.CharField(widget=forms.Textarea(attrs={'class':'input', 'placeholder': 'First Name'}), required=True)
    last_name = forms.CharField(widget=forms.Textarea(attrs={'class':'input', 'placeholder': 'Last Name'}), required=True)
    location = forms.CharField(widget=forms.Textarea(attrs={'class':'input', 'placeholder': 'Location'}), required=True)
    url = forms.CharField(widget=forms.Textarea(attrs={'class':'input', 'placeholder': 'URL'}), required=True)
    bio = forms.CharField(widget=forms.Textarea(attrs={'class':'input', 'placeholder': 'Bio'}), required=True)

    class Meta:
        model = Profile
        fields = ['picture', 'first_name', 'last_name', 'location', 'url', 'bio']