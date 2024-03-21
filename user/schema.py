from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from .serializer import UserSerializer
from .schemaSerializer import *

signUpSchema = extend_schema(
    summary="Sign up a new user account",
    request=UserSerializer,
    responses = {
        200: OpenApiResponse(response=SuccessSignUpSerializer, description='Operations successfully'),
        400: OpenApiResponse(response=GeneralMessageSerializer, description='Bad Request')
    }
)

loginSchema = extend_schema(
    summary="Login after verified",
    request = UserLoginSerializer,
    responses = {
        200: OpenApiResponse(response=SuccessUserLoginSerializer, description="Operations when login successfully!"),
        401: OpenApiResponse(response=GeneralMessageSerializer, description="User is not unauthorized"),
        403: OpenApiResponse(response=GeneralMessageSerializer, description="User is banned"),
        404: OpenApiResponse(response=GeneralMessageSerializer, description="User not found")
    }
)

verifyEmailSchema = extend_schema(
    summary="Verify account after signup",
    request=VerifyEmailSerializer,
    responses = {
        200: OpenApiResponse(response=GeneralMessageSerializer, description="Verified successfully!"),
        400: OpenApiResponse(response=GeneralMessageSerializer, description="Bad request"),
        404: OpenApiResponse(response=GeneralMessageSerializer, description="User not found")
    }
)

resendVerificationSchema = extend_schema(
    summary="Resend verification code if having some problems with previous code",
    request=ResendVerificationSerializer,
    responses= {
        200: OpenApiResponse(response=SuccessResendVerificationCode, description="Resend code successfully"),
        400: OpenApiResponse(response=GeneralMessageSerializer, description="Bad request"),
        404: OpenApiResponse(response=GeneralMessageSerializer, description="User not found")
    }
)

changePasswordSchema = extend_schema(
    summary="Provide both old password and new password to change password",
    request=ChangePasswordSerializer,
    responses= {
        200: OpenApiResponse(response=GeneralMessageSerializer, description='Update password successfuly'),
        400: OpenApiResponse(response=GeneralMessageSerializer, description="Something went wrong"),
    }
)




    
