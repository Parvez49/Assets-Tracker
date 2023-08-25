


from rest_framework import serializers
from .models import Company, Employee, Device, UserData, AssignDeviceToEmployee, ReturnDeviceToCompany

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id',"name","employee_id")

class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ('company', 'username', 'email', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserData(**validated_data)
        user.set_password(password)
        user.save()
        return user


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id','name','serial_no')


class AssignDeviceToEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignDeviceToEmployee
        fields = '__all__'


class ReturnDeviceToCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnDeviceToCompany
        fields = '__all__'

class AssignDeviceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model=AssignDeviceToEmployee
        fields=("device","employee","assign_date","return_date","log")



class ReturnDeviceHistorySerializer(serializers.ModelSerializer):
    return_date = serializers.DateField(source='date')
    class Meta:
        model=ReturnDeviceToCompany
        fields=("device","employee","return_date","log",)
