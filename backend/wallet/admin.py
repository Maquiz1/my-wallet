from django.contrib import admin
from .models import Wallet, Transaction, Category

admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(Category)
