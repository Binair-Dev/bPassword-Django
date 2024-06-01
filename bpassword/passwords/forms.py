from pyexpat import model
from django.forms import Form

class CredentialForm(Form):
    name = ''
    username = ''
    password = ''