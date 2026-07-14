from django.db import models

# Create your models here.

class MetaData(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # This tells Django NOT to make a separate database table for MetaData
        abstract = True


class ContactLeads(MetaData):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    phone_no = models.CharField(max_length=15, null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, default='new', choices=[('new', 'New'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')])

    def __str__(self):
        return self.name

class Testimonials(MetaData):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    message = models.TextField()
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)

    def __str__(self):
        return self.name



class Partner(MetaData):
    name = models.CharField(max_length=100) 
    image = models.ImageField(upload_to='partners/', null=True, blank=True)
    def __str__(self):
        return self.name
    