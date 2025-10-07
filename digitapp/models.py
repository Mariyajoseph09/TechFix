from django.db import models
from django.conf import settings
from django.contrib.auth.models import User





#from .models import customuser


# Create your models here.
class CustomUser(models.Model):
    user_id = models.AutoField(primary_key=True)  # auto-incremented primary key
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    
    USER_TYPE_CHOICES = (
        ('Admin', 'Admin'),
        ('Customer', 'Customer'),
        ('Technician', 'Technician'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='Customer')

    def __str__(self):
        return self.name



#class ServiceRequest(models.Model):
 #   request_id = models.AutoField(primary_key=True)
  #  customer = models.ForeignKey('customuser', on_delete=models.CASCADE, related_name="requests")
   # technician = models.ForeignKey('customuser', on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_requests")
    #device = models.CharField(max_length=100)
    #request_date = models.DateTimeField(auto_now_add=True)
    #status = models.CharField(max_length=20, choices=[
     #   ('Pending', 'Pending'),
      #  ('In Progress', 'In Progress'),
       # ('Completed', 'Completed')
    #], default='Pending')
    #description = models.TextField()

    #def __str__(self):
     #   return f"Request {self.request_id} - {self.status}"

class ServiceRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    device = models.CharField(max_length=100)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")
    description = models.TextField(null=True, blank=True)
    customer = models.ForeignKey('customuser', on_delete=models.CASCADE)
    #feedback = models.TextField(blank=True, null=True)


    warranty_status = models.CharField(
        max_length=20,
        choices=[("Yes", "Yes"), ("No", "No")],
        default="No"
    )
    assigned_to = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_jobs"
    )




    class Meta:
        db_table = 'digitapp_servicerequest'  # <-- link to your existing table

    def __str__(self):
        return f"Request {self.request_id} - {self.status}"





class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    service_request = models.ForeignKey('ServiceRequest', on_delete=models.CASCADE)
    customer = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.feedback_id} - Rating {self.rating}"







class Payment(models.Model):
    PAYMENT_METHODS = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Service #{self.service_request.id} - {self.status}"