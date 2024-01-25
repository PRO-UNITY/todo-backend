from django.contrib.auth import authenticate
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from authen.renderers import UserRenderers
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from authen.utils import Util
from todo.pagination import StandardResultsSetPagination, Pagination
from django.utils.encoding import (
    smart_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)

from authen.serializers import (
    UserSignUpSerializer,
    UserSigInSerializer,
    UserInformationSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    PasswordResetCompleteSerializer,
    UserUpdateSerializer,
)

User = get_user_model()
def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class UsersViews(APIView, Pagination):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = UserInformationSerializer

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
        queryset = User.objects.all().order_by('-id')
        page = super().paginate_queryset(queryset)
        if page is not None:
            serializer = super().get_paginated_response(self.serializer_class(page, many=True, context={"request": request}).data)
        else:
            serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSignUp(APIView):
    render_classes = [UserRenderers]

    @action(methods=['post'], detail=False)
    @swagger_auto_schema(
        request_body=UserSignUpSerializer,
        responses={201: "Created - Item created successfully",},
        tags=["auth"],)
    def post(self, request):
        username = request.data.get("username", "")
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        confirm_password = request.data.get('confirm_password', "")
        first_name = request.data.get('first_name', "")
        last_name = request.data.get('last_name', "")
        if not username or not email or not password or not confirm_password:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({"error": "User with this username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if password != confirm_password:
            return Response({"error": "Password and Confirm Password do not match"}, status=status.HTTP_400_BAD_REQUEST)
        my_user = User.objects.create(username=username, email=email, first_name=first_name, last_name=last_name)
        my_user.set_password(password)
        my_user.save()
        token = get_token_for_user(my_user)
        return Response({"token": token}, status=status.HTTP_201_CREATED)


class UserSignIn(APIView):
    render_classes = [UserRenderers]

    @action(methods=['post'], detail=True)
    @swagger_auto_schema(
        request_body=UserSigInSerializer,
        responses={201: "Created - Item created successfully",},
        tags=["auth"],)
    def post(self, request):
        expected_fields = set(["username", "password"])
        received_fields = set(request.data.keys())
        unexpected_fields = received_fields - expected_fields
        if unexpected_fields:
            error_message = (f"Unexpected fields in request data: {', '.join(unexpected_fields)}")
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSigInSerializer(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            username = request.data["username"]
            password = request.data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                tokens = get_token_for_user(user)
                return Response({"token": tokens}, status=status.HTTP_200_OK)
            else:
                return Response({"error": ["This user is not available to the system"]}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfile(APIView):
    render_classes = [UserRenderers]
    permission = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            serializer = UserInformationSerializer(request.user, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "The user is not logged in"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['put'], detail=True)
    @swagger_auto_schema(
        request_body=UserUpdateSerializer,
        responses={201: "update - Item update successfully",},
        tags=["auth"],)
    def put(self, request, *args, **kwarg):
        if request.user.is_authenticated:
            expected_fields = set(["id", "first_name", "last_name", "email",])
            received_fields = set(request.data.keys())
            unexpected_fields = received_fields - expected_fields
            if unexpected_fields:
                error_message = (f"Unexpected fields in request data: {', '.join(unexpected_fields)}")
                return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
            queryset = get_object_or_404(User, id=request.user.id)
            serializer = UserUpdateSerializer(context={"request": request}, instance=queryset, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"error": "update error data"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "The user is not logged in"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request):
        if request.user.is_authenticated:
            user_delete = User.objects.get(id=request.user.id)
            user_delete.delete()
            return Response({"message": "delete success"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "The user is not logged in"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method == "POST":
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get("old_password")):
                user.set_password(serializer.data.get("new_password"))
                user.save()
                update_session_auth_hash(request, user)
                return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
            return Response({"error": "Incorrect old password."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordRestEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    @action(methods=['post'], detail=False)
    def post(self, request):
        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            print(user)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            absurl = f"http://localhost:8081/reset-password/{uidb64}/{token}"
            email_body = f"Hi \n Use link below to reset password \n link: {absurl}"
            data = {
                "email_body": email_body,
                "to_email": user.email,
                "email_subject": "Reset your password",
            }

            Util.send(data)

            return Response({"success": "We have sent you to rest your password"}, status=status.HTTP_200_OK)
        return Response({"error": "This email is not found.."}, status=status.HTTP_404_NOT_FOUND)


class PasswordTokenCheckView(generics.GenericAPIView):
    serializer_class = UserInformationSerializer

    @action(methods=['get'], detail=False)
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"error": "Token is not valid, Please request a new one"}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({"success": True, "msg": "Credential Valid", "uidb64": uidb64, "token": token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError:
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"error": "Token is not valid, Please request a new one"}, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordView(generics.GenericAPIView):
    serializer_class = PasswordResetCompleteSerializer

    @action(methods=['patch'], detail=False)
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "success"}, status=status.HTTP_200_OK)