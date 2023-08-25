


from django.urls import path
from .views import *

urlpatterns = [
    # anyone can register his own company
    path("add-company/",addCompany),
    
    # user of company who can handle company's employee, device
    path('create-user/', createUser),
    path('login/',loginUser),
    path('logout/',logoutUser),

    # adding an employee of the company
    path('add-employee/', addEmployee),
    path('employee-list/',employeeList),

    # adding a device of the company
    path('add-device/', addDevice),
    path('device-list/',deviceList),

    # assign a device to employee of the company
    path('assign-device/', assignDevice),
    path('return-device/', returnDevice),

    # available device (not assigned) of the company
    path('available-device/',availableDevice),

    # currently assigned device list
    path('active-assignment-list/', activeAssignments),
    
    # all log history of a device
    path('device-history/<str:device_serial>/', deviceHistory, name='device-history'),

]
