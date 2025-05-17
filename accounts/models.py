from django.db import models
from django.contrib.auth.models import User

class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10)  # "Success" or "Failed"

    def __str__(self):
        return f"{self.username} - {self.status} at {self.timestamp}"
# Create your models here.

class BankAccount(models.Model):
    objects = None
    DoesNotExist = None
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=12, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=100000.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.account_number}"

class Transaction(models.Model):
    objects = None
    sender = models.ForeignKey('BankAccount', related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey('BankAccount', related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.user.username} sent ₹{self.amount} to {self.receiver.user.username} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"