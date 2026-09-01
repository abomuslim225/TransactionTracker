import random
from redis import Redis
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, EmailField
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.models import User, Transaction, Category, Notification
from apps.send import send_email


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs["refresh"])
        user_id = refresh["user_id"]
        user = User.objects.get(id=user_id)

        data['email'] = user.email
        return data

class SendEmailSerializer(Serializer):
    email = EmailField(max_length=255)


class OtpVerifySerializer(Serializer):
    email = CharField(max_length=255)
    code = CharField(max_length=6)

    def validate(self, value):
        email = value.get("email")
        code = value.get("code")
        redis = Redis()

        attempts_key = f"otp_attempts:{email}"
        attempts = int(redis.get(attempts_key) or 0)
        if attempts >= 7:
            raise ValidationError("Urinishlar soni tugadi, keyinroq qayta urinib ko'ring")

        otp_code = redis.get(email)
        if not otp_code:
            raise ValidationError("Kod muddati tugagan")
        if otp_code.decode() != str(code):
            redis.incr(attempts_key)
            redis.expire(attempts_key, 120)  # 2 daqiqa
            raise ValidationError("Kod xato")

        redis.delete(email)
        redis.delete(attempts_key)
        redis.setex(f"verified:register:{email}", 1800, "1")
        return value

class RegisterUserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
        }
    def validate_email(self, email):
        if not Redis().get(f"verified:register:{email}"):
            raise ValidationError("Avval emailni tasdiqlang")
        return email

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Redis().delete(f"verified:register:{validated_data['email']}")
        return user

class LoginUserSerializer(Serializer):
    login = CharField()
    password = CharField(write_only=True)
    def validate(self, data):
        user = authenticate(username=data["login"], password=data["password"])
        if user is None:
            raise ValidationError("email yoki password xato")
        data['user'] = user
        return data

class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'avatar']
        read_only_fields = ['id', 'email']

class ChangePasswordSerializer(Serializer):
    old_password = CharField(write_only=True)
    new_password = CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Joriy parol xato")
        return value

    def validate(self, data):
        if data['old_password'] == data['new_password']:
            raise ValidationError("Yangi parol eskisidan farq qilishi kerak")
        return data

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class ChangeEmailRequestSerializer(Serializer):
    new_email = EmailField()
    current_password = CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Joriy parol xato")
        return value

    def validate_new_email(self, value):
        user = self.context['request'].user
        if value == user.email:
            raise ValidationError("Bu allaqachon sizning joriy emailingiz")
        if User.objects.filter(email=value).exists():
            raise ValidationError("Bu email allaqachon band")
        return value

    def save(self):
        request = self.context['request']
        new_email = self.validated_data['new_email']

        code = random.randint(100000, 999999)
        send_email(new_email, code=code)

        redis = Redis()
        # Namespace bilan ajratilgan kalit — register OTP bilan
        # to'qnashmasligi va faqat shu foydalanuvchi + shu yangi email
        # kombinatsiyasiga tegishli bo'lishi uchun.
        key = f"change_email:{request.user.id}:{new_email}"
        redis.setex(key, 120, code)  # 2 daqiqa amal qiladi

        return new_email


class ChangeEmailConfirmSerializer(Serializer):
    new_email = EmailField()
    code = CharField(max_length=6)

    def validate(self, data):
        request = self.context['request']
        key = f"change_email:{request.user.id}:{data['new_email']}"
        redis = Redis()

        stored_code = redis.get(key)
        if not stored_code:
            raise ValidationError("Kod muddati tugagan yoki so'ralmagan")
        if stored_code.decode() != data['code']:
            raise ValidationError("Kod xato")

        redis.delete(key)
        return data

    def save(self):
        user = self.context['request'].user
        user.email = self.validated_data['new_email']
        user.save()
        return user

class CategoryModelSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TransactionModelSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id','name', 'amount', 'description', 'status', 'type', 'date', 'category', 'currency']
        read_only_fields = ['id']

class TransactionCreateSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'name', 'amount', 'description', 'status', 'type', 'date', 'category', 'currency']
        read_only_fields = ['id']

    def validate_status(self, value):
        if value not in ('pending', 'confirmed'):
            raise ValidationError("status faqat 'pending' yoki 'confirmed' bo'lishi mumkin")
        return value

class NotificationModelSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = ['transaction']

    def validate_transaction(self, value):
        request = self.context.get('request')
        if value.user != request.user:
            raise ValidationError("Bu tranzaksiya sizga tegishli emas")
        return value
