import random
from decimal import Decimal

from django.db.models import When, Case, F
from django.db.models.aggregates import Sum
from django.db.models.fields import DecimalField
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from redis import Redis
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, \
    RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.filters import TransactionFilter
from apps.models import User, Transaction, Category, Notification, ExchangeRate
from apps.send import send_email
from apps.serializers import RegisterUserModelSerializer, OtpVerifySerializer, SendEmailSerializer, \
    CustomTokenRefreshSerializer, LoginUserSerializer, TransactionModelSerializer, CategoryModelSerializer, \
    NotificationModelSerializer, ChangePasswordSerializer, ChangeEmailRequestSerializer, ChangeEmailConfirmSerializer, \
    UserProfileSerializer, TransactionCreateSerializer
from apps.utils import get_tokens_for_user


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

class VerifyEmailAPIView(GenericAPIView):
    serializer_class = SendEmailSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        code = random.randint(100000, 999999)
        send_email(email, code=code)

        redis = Redis()
        redis.setex(email, 120, code)

        return Response({"message": "tasdiqlash code jo'natildi"}, status=HTTP_200_OK)


class VerifyOtpCodeAPIView(APIView):
    serializer_class = OtpVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OtpVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "otp code success"}, status=HTTP_200_OK)

class RegisterUserAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserModelSerializer
    permission_classes = [AllowAny]

class LoginUserAPIView(APIView):
    serializer_class = LoginUserSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        tokens = get_tokens_for_user(user)
        return Response({
            **tokens,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=HTTP_200_OK)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            raise ValidationError({"refresh": "refresh token kerak"})
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception:
            raise ValidationError({"refresh": "token yaroqsiz yoki muddati tugagan"})
        return Response({"message": "Muvaffaqiyatli chiqildi"}, status=HTTP_200_OK)

class UserProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ChangePasswordAPIView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Parol muvaffaqiyatli yangilandi"}, status=HTTP_200_OK)


class ChangeEmailRequestAPIView(GenericAPIView):
    serializer_class = ChangeEmailRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        new_email = serializer.save()
        return Response(
            {"message": f"{new_email} manziliga tasdiqlash kodi yuborildi"},
            status=HTTP_200_OK,
        )


class ChangeEmailConfirmAPIView(GenericAPIView):
    serializer_class = ChangeEmailConfirmSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Email muvaffaqiyatli yangilandi"}, status=HTTP_200_OK)

class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategoryModelSerializer
    permission_classes = [AllowAny]


def _rates_map():
    rates = {'UZS': Decimal('1')}
    for row in ExchangeRate.objects.all():
        rates[row.code] = row.rate_to_uzs
    return rates


class CategoryStatsAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def _stats_for_type(self, user, tx_type, start_of_month, end_of_month, target, rates):
        rows = (
            Transaction.objects
            .filter(
                user=user,
                status='confirmed',
                type=tx_type,
                date__gte=start_of_month,
                date__lt=end_of_month,
            )
            .values('category__id', 'category__name', 'currency')
            .annotate(total=Sum('amount'))
        )

        target_rate = rates.get(target, Decimal('1'))
        merged = {}
        for row in rows:
            code = row['currency']
            if code != 'UZS' and code not in rates:
                continue
            rate = rates.get(code, Decimal('1'))
            converted = (row['total'] or 0) * rate / target_rate

            cid = row['category__id']
            if cid not in merged:
                merged[cid] = {'name': row['category__name'], 'total': Decimal('0')}
            merged[cid]['total'] += converted

        total_sum = sum(v['total'] for v in merged.values()) or Decimal('0')

        categories = [
            {
                'category_id': cid,
                'category_name': v['name'],
                'total': round(v['total'], 2),
                'pct': round((v['total'] / total_sum) * 100, 1) if total_sum else 0,
            }
            for cid, v in sorted(merged.items(), key=lambda kv: -kv[1]['total'])
        ]
        return {'total': round(total_sum, 2), 'categories': categories}

    def get(self, request):
        target = request.query_params.get('currency', 'UZS').upper()
        if target not in ('UZS', 'USD', 'EUR'):
            raise ValidationError({"currency": "UZS, USD yoki EUR bo'lishi kerak"})

        rates = _rates_map()
        if target != 'UZS' and target not in rates:
            raise ValidationError({"currency": "Kurs ma'lumoti hali yuklanmagan, birozdan so'ng urinib ko'ring"})

        now = timezone.now()
        try:
            year = int(request.query_params.get('year', now.year))
            month = int(request.query_params.get('month', now.month))
        except ValueError:
            raise ValidationError({"month": "year va month butun son bo'lishi kerak"})
        if not (1 <= month <= 12):
            raise ValidationError({"month": "month 1 dan 12 gacha bo'lishi kerak"})

        start_of_month = timezone.make_aware(timezone.datetime(year, month, 1))
        if month == 12:
            end_of_month = timezone.make_aware(timezone.datetime(year + 1, 1, 1))
        else:
            end_of_month = timezone.make_aware(timezone.datetime(year, month + 1, 1))

        return Response({
            'year': year,
            'month': month,
            'expense': self._stats_for_type(request.user, 'expense', start_of_month, end_of_month, target, rates),
            'income': self._stats_for_type(request.user, 'income', start_of_month, end_of_month, target, rates),
        }, status=HTTP_200_OK)

class TransactionCreateAPIView(CreateAPIView):
    serializer_class = TransactionCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionListAPIView(ListAPIView):
    serializer_class = TransactionModelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TransactionFilter
    search_fields = ['name']

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')

class TransactionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionModelSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class BalanceAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        target = request.query_params.get('currency', 'UZS').upper()
        if target not in ('UZS', 'USD', 'EUR'):
            raise ValidationError({"currency": "UZS, USD yoki EUR bo'lishi kerak"})

        rates = _rates_map()
        if target != 'UZS' and target not in rates:
            raise ValidationError({"currency": "Kurs ma'lumoti hali yuklanmagan, birozdan so'ng urinib ko'ring"})

        data = (Transaction.objects.filter(user=request.user, status='confirmed')
        .values('currency')
        .annotate(
            total_income=Sum(
                Case(When(type='income', then=F('amount')), default=0, output_field=DecimalField())
            ),
            total_expense=Sum(
                Case(When(type='expense', then=F('amount')), default=0, output_field=DecimalField())
            )))

        total_income = Decimal('0')
        total_expense = Decimal('0')
        target_rate = rates.get(target, Decimal('1'))

        for row in data:
            code = row['currency']
            if code != 'UZS' and code not in rates:
                continue
            rate = rates.get(code, Decimal('1'))
            total_income += (row['total_income'] or 0) * rate / target_rate
            total_expense += (row['total_expense'] or 0) * rate / target_rate

        return Response({
            'currency': target,
            'income': round(total_income, 2),
            'expense': round(total_expense, 2),
            'balance': round(total_income - total_expense, 2),
        })

class NotificationCreateAPIView(CreateAPIView):
    serializer_class = NotificationModelSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NotificationListAPIView(ListAPIView):
    serializer_class = NotificationModelSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class NotificationRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationModelSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


