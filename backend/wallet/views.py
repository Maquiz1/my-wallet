from django.shortcuts import render, redirect
from .models import Wallet, Transaction, Category
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm

@login_required
def dashboard(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all().order_by('-date')
    return render(request, 'wallet/dashboard.html', {'wallet': wallet, 'transactions': transactions})

@login_required
def add_transaction(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.wallet = wallet
            transaction.save()
            return redirect('wallet:dashboard')
    else:
        form = TransactionForm()
    return render(request, 'wallet/add_transaction.html', {'form': form})
