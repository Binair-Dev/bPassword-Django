from pyexpat import model
from django.forms import Form

class LoginForm(Form):
    username = ''
    password = ''