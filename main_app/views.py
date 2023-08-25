from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import AuthenticationFailed
from .models import *
from .serializers import *
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse

import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError
import datetime
from django.utils import timezone

from django.db.models import Q, F

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema



@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING),
            'registration_no': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['name', 'registration_no']
    ),
    responses={
        200: openapi.Response('Company Added', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        400: openapi.Response('Bad Request', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        401: openapi.Response('Unauthorized', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        403: openapi.Response('Forbidden', schema=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)
@api_view(['POST'])
def addCompany(request):
    # This function handles the addition of a new company.

    if request.method=="POST":
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success":"Successfully added this company"})
        return Response(serializer.errors)



@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company': openapi.Schema(type=openapi.TYPE_STRING),
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['company','username','email','password']
    ),
    responses={
        200: openapi.Response('User Added', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        400: openapi.Response('Bad Request', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        401: openapi.Response('Unauthorized', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        403: openapi.Response('Forbidden', schema=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)
@api_view(['POST'])
def createUser(request):
    """
    Create a new user who handle company's employees, devices
    """
    serializer = UserDataSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"success":"User created"}, status=201)
    return Response(serializer.errors, status=400)




@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'company': openapi.Schema(type=openapi.TYPE_STRING),
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['company','username','password']
    ),
    responses={
        200: openapi.Response('Successfully logged in..', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        400: openapi.Response('Bad Request', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        401: openapi.Response('Unauthorized', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        403: openapi.Response('Forbidden', schema=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)
@api_view(['POST'])
def loginUser(request):
    """
    Authenticate a user and issue a JWT for successful logins.

    This view handles incoming POST requests containing user login credentials,
    including the company, username, and password. If the user is found and the password
    matches, a JWT token is generated with a payload containing user information
    and expiration time. The token is then set as a cookie in the response.
    """

    company=request.data['company']
    username=request.data['username']
    password=request.data['password']
    user = UserData.objects.filter(company=company,username=username).first()

    if not user:
        raise AuthenticationFailed('User not found!')

    if not check_password(password,user.password):
        raise AuthenticationFailed('Incorrect password!')    
     
    payload = {
        'id': user.id,
        'company':company,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, 'secret', algorithm='HS256')

    response = Response()
    response.set_cookie(key='logintoken', value=token, httponly=True)
    response.data = {"You are logged in"}
    return response

@api_view(['GET'])
def logoutUser(request):
    response = Response()
    response.delete_cookie('logintoken')
    response.data = {"you are logged out"}
    return response



def authenticateUser(token):
    # helper function for checking whether user log in or not
    
    if not token:
        raise AuthenticationFailed({"error":'Log in first!'})
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except ExpiredSignatureError:
        raise AuthenticationFailed({"error":'You session has expired!'})
    except DecodeError:
        raise AuthenticationFailed({"error":'Log in failed!'})
    return payload



@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING),
            'employee_id': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['name','employee_id']
    ),
    responses={
        200: openapi.Response('Employee Added', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        400: openapi.Response('Bad Request', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        401: openapi.Response('Unauthorized', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        403: openapi.Response('Forbidden', schema=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)
@api_view(['POST'])
def addEmployee(request):
    """
    Adding a new employee to a company.
    The employee's details are included in the request data.
    The view first authenticates the user using the token, then retrieves the company,
    assigns it to the employee, and saves the employee record using the EmployeeSerializer.
    """

    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)

    # Authenticate the user and retrieve the company
    company=Company.objects.filter(registration_no=payload['company']).first()
    request.data['company']=company.pk

    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"success":"Successfully added"}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def employeeList(request):
    # show all employees of company
    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)

    data=Employee.objects.filter(company=payload['company'])
    serializer=EmployeeSerializer(data,many=True)
    return Response(serializer.data)




@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING),
            'serial_no': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['name','serial_no']
    ),
    responses={
        200: openapi.Response('Device Added', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        400: openapi.Response('Bad Request', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        401: openapi.Response('Unauthorized', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        403: openapi.Response('Forbidden', schema=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)
@api_view(['POST'])
def addDevice(request):
    """
    Adds a new device to the company's inventory.
    The function expects the device details including the device name and serial number in the request data.
    """

    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)

    request.data['company']=payload['company']
    serializer = DeviceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"success":"Successfully added"}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def deviceList(request):
    """
    Retrieves a list of devices associated with the authenticated user's company.
    """

    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)

    # show all devices
    data=Device.objects.filter(company=payload['company'])
    serializer=DeviceSerializer(data,many=True)
    return Response(serializer.data)


from django.utils.timezone import now

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'employee_id': openapi.Schema(type=openapi.TYPE_STRING),
            'device_serial': openapi.Schema(type=openapi.TYPE_STRING),
            'assigned_date': openapi.Schema(type=openapi.TYPE_STRING),
            'return_date': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['employee_id','device_serial','assigned_date','return_date']
    ),
    responses={
        200: openapi.Response('Device Assigned', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        400: openapi.Response('Bad Request', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        401: openapi.Response('Unauthorized', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        403: openapi.Response('Forbidden', schema=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)
@api_view(['POST'])
def assignDevice(request):
    """
    Handle device assignment to an employee.

    It performs the following steps:
    1. Authenticate the user using the provided token.
    2. Retrieve company information based on the authenticated payload.
    3. Check if the provided employee exists within the company.
    4. Check if the provided device exists within the company.
    5. Set employee and device IDs in the request data.
    6. Check if the device has a 'bad' log in the return history.
    7. Check device availability by comparing its latest return date with the current date.
    8. If all checks pass, create a new assignment record using the serializer.
    """
    
    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)

    
    company=Company.objects.filter(registration_no=payload['company']).first()
    request.data['company']=company.pk

    # Check if the employee exists
    employee=Employee.objects.filter(employee_id=request.data['employee_id'],company=payload['company']).first()
    if not employee:
        return Response({"error":"Employee not found"})
    
    # Check if the device exists
    device=Device.objects.filter(serial_no=request.data['device_serial'],company=payload['company']).first()
    if not device:
        return Response({"error": "Device not found"})
    
    request.data['employee']=employee.pk
    request.data['device']=device.pk

    # Check if the device is not allowed to be assigned
    if ReturnDeviceToCompany.objects.filter(device=device, log='bad').exists():
        return Response({"error": "Device cannot be assigned due to bad log"})
    
    # Check device availability
    latest_assignment = AssignDeviceToEmployee.objects.filter(device=device).order_by('-assign_date').first()
    current_date = now().date()
    if latest_assignment and latest_assignment.return_date > current_date:
        return Response({"error": "Device is not available"})

    serializer = AssignDeviceToEmployeeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"success":"Assigned device"}, status=201)
    return Response(serializer.errors, status=400)




@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'employee_id': openapi.Schema(type=openapi.TYPE_STRING),
            'device_serial': openapi.Schema(type=openapi.TYPE_STRING),
            'condition': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['employee_id','device_serial','condition']
    ),
    responses={
        200: openapi.Response('Device Returned', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        400: openapi.Response('Bad Request', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        401: openapi.Response('Unauthorized', schema=openapi.Schema(type=openapi.TYPE_STRING)),
        403: openapi.Response('Forbidden', schema=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)
@api_view(['POST'])
def returnDevice(request):
    """
    Handle the device return process.
    1. Authenticate the user via the token.
    2. Fetch the company information based on the user's payload.
    3. Verify the existence of the employee and the device.
    4. If the device was previously assigned, update the return date.
    5. Serialize the return data and save it.
    6. Return a success message or error response accordingly.
    """

    token=request.COOKIES.get("logintoken")
    payload=authenticateUser(token)

    company=Company.objects.filter(registration_no=payload['company']).first()
    request.data['company']=company.pk

    # Check if the employee exists
    employee=Employee.objects.filter(employee_id=request.data['employee_id'],company=payload['company']).first()
    if not employee:
        return Response({"error":"Employee not found"})
    
    # Check if the device exists
    device=Device.objects.filter(serial_no=request.data['device_serial'],company=payload['company']).first()
    if not device:
        return Response({"error": "Device not found"})

    request.data['employee']=employee.pk
    request.data['device']=device.pk

    # Update AssignDeviceToEmployee if device return device before or after return_date
    latest_assignment = AssignDeviceToEmployee.objects.filter(employee=employee,device=device).order_by('-assign_date').first()
    if latest_assignment:
        latest_assignment.return_date = now().date()
        latest_assignment.save()

    serializer = ReturnDeviceToCompanySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Device returned successfully"}, status=200)

    return Response(serializer.errors, status=400)
        



from django.db.models import F 

@api_view(['GET'])
def availableDevice(request):
    """
    Returns a list of devices that are currently available for 
    assignment in the company.
    """
        
    token = request.COOKIES.get("logintoken")
    payload = authenticateUser(token)

    company = Company.objects.filter(registration_no=payload['company']).first()

    # Get a list of devices that are not assigned or have a bad log
    available_devices = Device.objects.filter(company=company
    ).exclude(
        assigndevicetoemployee__return_date__gt=F('assigndevicetoemployee__assign_date')
    ).exclude(
        returndevicetocompany__log='bad'
    )

    serializer = DeviceSerializer(available_devices, many=True)
    return Response(serializer.data, status=200)



@api_view(['GET'])
def deviceHistory(request, device_serial):
    """
    Retrieve and return the history of assignments and returns for a specific device.
    """

    # Authenticate the user using the token
    token = request.COOKIES.get("logintoken")
    payload = authenticateUser(token)

    company = Company.objects.filter(registration_no=payload['company']).first()

    # Check if the device exists
    device = Device.objects.filter(serial_no=device_serial, company=company).first()
    if not device:
        return Response({"error": "Device not found"})

    # Fetch assignments and returns for the device
    assignments = AssignDeviceToEmployee.objects.filter(device=device).order_by('-assign_date')
    returns = ReturnDeviceToCompany.objects.filter(device=device).order_by('-date')

    assignment_serializer = AssignDeviceHistorySerializer(assignments, many=True)
    return_serializer = ReturnDeviceHistorySerializer(returns, many=True)

    # Combine assignment and return data and sort by date
    logs = []
    logs.extend(assignment_serializer.data)
    logs.extend(return_serializer.data)

    sorted_logs = sorted(logs, key=lambda log: log.get('assign_date', log.get('return_date')), reverse=True)
    renderer = JSONRenderer()
    return HttpResponse(renderer.render(sorted_logs), content_type='application/json')



@api_view(['GET'])
def activeAssignments(request):
    """
    Retrieves a list of active device assignments for the company.
    """

    token = request.COOKIES.get("logintoken")
    payload = authenticateUser(token)

    company = Company.objects.filter(registration_no=payload['company']).first()

    # Get active assignments with return_date > current date
    active_assignments = AssignDeviceToEmployee.objects.filter(employee__company=company,
        return_date__gt=now().date()  
    ).order_by('-assign_date')

    active_assignment_serializer = AssignDeviceToEmployeeSerializer(active_assignments, many=True)

    return Response(active_assignment_serializer.data, status=200)


