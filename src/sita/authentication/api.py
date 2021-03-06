# -*- coding: utf-8 -*-
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from sita.api.v1.routers import router
from sita.utils import conekta_sita
from sita.users.models import User, Device, Subscription
from sita.subscriptions.models import Subscription as Subscriptions
from sita.cards.models import Card
from sita.users.serializers import UserSerializer
from sita.authentication.serializers import (LoginSerializer,
    RecoveryPasswordSerializer,
    LoginResponseSerializer,
    ResetPasswordWithCodeSerializer,
    SignUpSerializer)
from sita.core.api.routers.single import SingleObjectRouter
from datetime import datetime, timedelta

class LoginViewSet(viewsets.GenericViewSet):
    permission_classes = (AllowAny, )
    serializer_class = LoginSerializer

    @detail_route(methods=['POST'])
    def signin(self, request, *args, **kwards):
        """
        User login.
        ---
        type:
            token:
                type: string
            user:
                pytype: UserSerializer
        omit_parameters:
            - form
        parameters:
            - name: body
              pytype: LoginSerializer
              paramType: body
              description:
                'email: <b>required</b> <br>
                password: <b>required</b> <br>
                deviceOs: NOT required <br>
                deviceToken: NOT required'
        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 200
              message: OK
            - code: 500
              message: INTERNAL SERVER ERROR
        consumes:
            - application/json
        produces:
            - application/json
        """

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.get_user(serializer.data)
            response_serializer = LoginResponseSerializer()
            device_token=request.data.get("device_token")
            device_os=request.data.get("device_os")
            if device_token and device_os:
                device = Device.objects.register(
                    device_token=device_token,
                    device_os=device_os,
                    user=user)
            return Response(response_serializer.get_token(user))

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecoveryPasswordViewSet(viewsets.GenericViewSet):
    permission_classes = (AllowAny, )
    serializer_class = RecoveryPasswordSerializer

    @detail_route(methods=['POST'])
    def recovery_password(self, request, *args, **kwards):
        """
        Recovery Password.
        ---
        omit_parameters:
            - form
        parameters:
            - name: body
              type: RecoveryPasswordSerializer
              paramType: body
              description:
                'email: <b>required</b>'
        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 200
              message: OK
            - code: 500
              message: INTERNAL SERVER ERROR
        consumes:
            - application/json
        produces:
            - application/json
        """

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.generate_recovery_token(serializer.data)
            return Response()

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordWithCodeViewSet(viewsets.GenericViewSet):
    permission_classes = (AllowAny, )
    serializer_class = ResetPasswordWithCodeSerializer

    @detail_route(methods=['POST'])
    def reset_password_code(self, request, *args, **kwards):
        """
        Reset Password.
        ---
        omit_parameters:
            - form
        parameters:
            - name: body
              type: ResetPasswordWithCodeSerializer
              paramType: body
              description:
                'password: <b>required</b> <br>
                passwordConfim: <b>required</b> <br>
                recoveryCode: <b>required</b> <br>'
        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 200
              message: OK
            - code: 500
              message: INTERNAL SERVER ERROR
        consumes:
            - application/json
        produces:
            - application/json
        """

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.update_password(data=request.data)
            return Response()

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignUpViewSet(viewsets.GenericViewSet):
    permission_classes = (AllowAny, )
    serializer_class = SignUpSerializer

    @detail_route(methods=['POST'])
    def signup(self, request, *args, **kwards):
        """
        User login.
        ---
        omit_parameters:
            - form
        parameters:
            - name: body
              type: SignUpSerializer
              paramType: body
              description:
                'email: <b>required</b> <br>
                password: <b>required</b> <br>
                name:NOT required <br>
                firstName: NOT required <br>
                mothersName: NOT required <br>
                phone: NOT required<br>
                deviceOs: NOT required<br>
                deviceToken: NOT required<br>
                conektaCard: NOT required'
        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 200
              message: OK
            - code: 500
              message: INTERNAL SERVER ERROR
        consumes:
            - application/json
        produces:
            - application/json
        """

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            conekta_customer = ""
            if request.data.get("conekta_card"):
                customer = conekta_sita.create_customer(data=request.data)
                if customer is not None:
                    conekta_customer = customer.id
            for key in request.data:
                if key == "name" or key == "phone":
                    kwards.setdefault(key,request.data.get(key))
            user = User.objects.create_user(
                email=request.data.get("email"),
                password=request.data.get("password"),
                time_zone=request.data.get("time_zone"),
                conekta_customer=conekta_customer,
                automatic_payment=False,
                **kwards
            )

            if conekta_customer != "":
                card_data = {
                    "last_four":customer.payment_sources[0].last4,
                    "is_default":True,
                    "conekta_card":customer.payment_sources[0].id,
                    "brand_card":customer.payment_sources[0].brand,
                }
                fields = Card().get_fields()
                Card.objects.register(
                    data=card_data, fields=fields, user=user)
                subscription = Subscriptions.objects.get(id=request.data.get("subscription_id"))
                # next_time_expirate = datetime.now() + timedelta(minutes=43200)
                next_time_expirate = datetime.now() + timedelta(minutes=1)
                subscription_user = Subscription(
                    user_id=user.id,
                    time_in_minutes=43200,
                    is_test=True,
                    is_current=True,
                    next_time_in_minutes=subscription.time_in_minutes,
                    next_mount_pay=subscription.amount,
                    expiration_date=next_time_expirate,
                    next_pay_date=next_time_expirate,
                    title=subscription.title
                )
                subscription_user.save()
                user.has_subscription = True
                user.automatic_payment = True
                user.save()

            device_token=request.data.get("device_token")
            device_os=request.data.get("device_os")
            if device_token and device_os:
                device = Device.objects.register(
                    device_token=device_token,
                    device_os=device_os,
                    user=user)

            response_serializer = LoginResponseSerializer()
            return Response(response_serializer.get_token(user))

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


router.register(
    r'auth',
    LoginViewSet,
    base_name="signin",
    router_class=SingleObjectRouter
)
router.register(
    r'auth',
    RecoveryPasswordViewSet,
    base_name="recovery-password",
    router_class=SingleObjectRouter
)
router.register(
    r'auth',
    ResetPasswordWithCodeViewSet,
    base_name="reset-password-code",
    router_class=SingleObjectRouter
)
router.register(
    r'auth',
    SignUpViewSet,
    base_name="signup",
    router_class=SingleObjectRouter
)
