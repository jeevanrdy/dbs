from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from .models import LoginAttempt, Transaction
from django.contrib.auth.models import User
from .forms import RegisterForm, CustomUserCreationForm, LoginForm
from django.contrib import messages
from django.db import transaction
from django.utils.timezone import now
from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django import forms
from .models import BankAccount
from decimal import Decimal, InvalidOperation
from .models import BankAccount, Transaction
from django.db import models, transaction
import random

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

@login_required
def home_view(request):
    # ✅ Ensure the user has a bank account
    try:
        account = BankAccount.objects.get(user=request.user)
    except BankAccount.DoesNotExist:
        messages.error(request, "Bank account not found. Please contact support.")
        return redirect('support_page')  # Redirect instead of returning None

    # ✅ Fetch all accounts for display
    all_accounts = BankAccount.objects.all()

    # ✅ Handle Money Transfer
    if request.method == 'POST':
        to_account_num = request.POST.get('to_account')
        amount_str = request.POST.get('amount')

        try:
            amount = Decimal(amount_str)  # Convert to Decimal
            if amount <= 0:
                messages.error(request, "Enter a positive amount.")
            elif amount > account.balance:
                messages.error(request, "Insufficient balance.")
            else:
                try:
                    receiver = BankAccount.objects.get(account_number=to_account_num)
                    if receiver == account:
                        messages.error(request, "Cannot transfer to your own account.")
                    else:
                        with transaction.atomic():
                            account.balance -= amount
                            receiver.balance += amount
                            account.save()
                            receiver.save()
                            # ✅ Save transaction record
                            Transaction.objects.create(
                                sender=account,
                                receiver=receiver,
                                amount=amount
                            )
                        messages.success(request, f"Successfully transferred ₹{amount} to {receiver.user.username}.")
                except BankAccount.DoesNotExist:
                    messages.error(request, "Recipient account not found.")
        except (InvalidOperation, ValueError):
            messages.error(request, "Invalid amount entered.")

    # ✅ Fetch Transactions for This User
    transactions = Transaction.objects.filter(
        models.Q(sender=account) | models.Q(receiver=account)
    ).order_by('-timestamp') if account else None  # Ensure account exists

    return render(request, 'home.html', {
        'account': account,
        'all_accounts': all_accounts,
        'transactions': transactions,
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")  # ✅ Error message

    form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful!")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)



def generate_account_number():
    return str(random.randint(100000000000, 999999999999))

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create bank account with 100000 balance
            BankAccount.objects.create(
                user=user,
                account_number=generate_account_number(),
                balance=100000.00
            )
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})