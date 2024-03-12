from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from master.models import *
from .serializers import *
from .decorators import *

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmployeeTokenObtainPairSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        user = None
        serializer = self.get_serializer(data=request.data)
        if User.objects.filter(username=request.data['username']).exists():
            try:
                user = User.objects.get(username=request.data['username'])
                user_id = User.objects.filter(username=request.data['username']).values('id')[0]['id']
                role_id = UserAccess.objects.filter(emp_id=user_id).values('role_id_id')
                if role_id.exists():
                    role_id = role_id[0]['role_id_id']
                    role_id = RoleMaster.objects.filter(role_id=role_id).values('role_id')[0]['role_id']
                    user.role = role_id
                else:
                    user.role = None
            except User.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=status.HTTP_401_UNAUTHORIZED)

        if serializer.is_valid():
            # Getting menu for user role
            menu_response = get_user_menu(user.role)
            root_list = get_root_list(user.role)
            # Returning combined response
            return Response({
                'access': serializer.validated_data['access'],
                'refresh': serializer.validated_data['refresh'],
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'name': user.name,
                    'department': user.department.id if user.department else None,
                    'subDepartment': user.sub_department.id if user.sub_department else None,
                    'role': user.role if user.role else 'No Role Assigned',
                },
                'menu': menu_response,
                'sub_menu': root_list
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
