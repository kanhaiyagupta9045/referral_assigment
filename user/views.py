from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status
import json
from .models import User
from django.contrib.auth.hashers import make_password,check_password
from rest_framework.decorators import api_view,permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.views.decorators.csrf import csrf_exempt


def generate_referral_code():
        import uuid
        return uuid.uuid4().hex[:10] 

@api_view(['POST'])
def CreateUser(request):
    try:
        data = json.loads(request.body)
        
        
        if not data.get('name') or not data.get('mobile_number') or not data.get('email') or not data.get('city') or not data.get('password'):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if User.objects.filter(email=data['email']).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        
        referrer = None
        if 'referrer_code' in data and data['referrer_code']:
            try:
                referrer = User.objects.get(referral_code=data['referrer_code'])
            except User.DoesNotExist:
                return Response({"error": "Invalid referral code"}, status=status.HTTP_400_BAD_REQUEST)

        
        referral_code = generate_referral_code()

       
        user = User.objects.create(
            email=data['email'],
            name=data['name'],
            mobile_number=data['mobile_number'],
            city=data['city'],
            referral_code=referral_code,
            referrer=referrer,
            password=make_password(data['password'])  
        )

        
        return Response({
            "message": "User created successfully",
            "referral_code": referral_code,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "mobile_number": user.mobile_number,
                "city": user.city,
                "referral_code": user.referral_code,
                "referrer": user.referrer.email if user.referrer else None
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": f"Invalid data: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not check_password(password, user.password):
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Login successful",
                "access_token": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "name": user.name
                }
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(['GET'])
def referral_details(request,referral_code):
    try:

        if not referral_code:
            return Response(
                {"error": "Referral token is required", "code": "missing_referral_token"},
                status=status.HTTP_400_BAD_REQUEST
            )

       
        user = User.objects.filter(referral_code =  referral_code).first()
        if not user:
            return Response({"error": "User not found for the provided referral token", "code": "user_not_found"},status=status.HTTP_404_NOT_FOUND)

        
        referees = User.objects.filter(referrer=user).values('name', 'email', 'created_at')
        response_data = [
            {
                "name": referee['name'],
                "email": referee['email'],
                "registration_date": referee['created_at']
            }
            for referee in referees
        ]

        return Response({"message": "Referees fetched successfully", "referees": response_data},status=status.HTTP_200_OK)

    except Exception as e:
        
        return Response({"error": str(e), "code": "internal_server_error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)




