from django.db import models

# Create your models here.

from django.contrib.auth.hashers import make_password
    

class Company(models.Model):
    name = models.CharField(max_length=100)
    registration_no=models.CharField(max_length=100,primary_key=True)

    def __str__(self):
        return self.name

class UserData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def __str__(self):
        return self.username
    

class Employee(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    employee_id=models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Device(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    serial_no = models.CharField(max_length=100)

    def __str__(self):
        return self.name





class ConditionChoice(models.TextChoices):
    choice1 = 'better', "better"
    choice2 = 'good', "good"
    choice3 = 'bad', "bad"

class AssignDeviceToEmployee(models.Model):
    company=models.ForeignKey(Company,on_delete=models.CASCADE)
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE)
    device=models.ForeignKey(Device,on_delete=models.CASCADE,default=0)
    assign_date=models.DateField(auto_now=True)
    return_date=models.DateField()
    log=models.CharField(max_length=20,choices=ConditionChoice.choices)

class ReturnDeviceToCompany(models.Model):
    company=models.ForeignKey(Company,on_delete=models.CASCADE)
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE)
    device=models.ForeignKey(Device,on_delete=models.CASCADE,default=0)
    date=models.DateField(auto_now=True)
    log=models.CharField(max_length=50,choices=ConditionChoice.choices)
