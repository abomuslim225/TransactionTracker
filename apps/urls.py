from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.views import VerifyEmailAPIView, VerifyOtpCodeAPIView, RegisterUserAPIView, LoginUserAPIView, \
    TransactionCreateAPIView, LogoutAPIView, ChangeEmailRequestAPIView, ChangeEmailConfirmAPIView, \
    ChangePasswordAPIView, CategoryListAPIView, TransactionListAPIView, TransactionRetrieveUpdateDestroyAPIView, \
    BalanceAPIView, NotificationCreateAPIView, NotificationListAPIView, NotificationRetrieveUpdateDestroyAPIView, \
    CustomTokenRefreshView, CategoryStatsAPIView, UserProfileAPIView

urlpatterns = [
    # ── SCHEMA ────────────────────────────────────────────────────────
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('user/verify/email/', VerifyEmailAPIView.as_view()),
    path('user/verify/otp/', VerifyOtpCodeAPIView.as_view()),
    path('user/register/', RegisterUserAPIView.as_view()),
    path('user/login/', LoginUserAPIView.as_view()),
    path('user/logout/', LogoutAPIView.as_view()),
    path('user/profile/', UserProfileAPIView.as_view()),
    path('user/token/refresh/', CustomTokenRefreshView.as_view()),
    path('user/change/email/request/', ChangeEmailRequestAPIView.as_view()),
    path('user/change/email/confirm/', ChangeEmailConfirmAPIView.as_view()),
    path('user/change/password/', ChangePasswordAPIView.as_view()),

    path('category/list/', CategoryListAPIView.as_view()),
    path('stats/categories/', CategoryStatsAPIView.as_view()),

    path('transactions/create/', TransactionCreateAPIView.as_view()),
    path('transactions/list/', TransactionListAPIView.as_view()),
    path('transactions/rud/<int:pk>/', TransactionRetrieveUpdateDestroyAPIView.as_view()),

    path('balance/', BalanceAPIView.as_view()),

    path('notifications/create/', NotificationCreateAPIView.as_view()),
    path('notifications/list/', NotificationListAPIView.as_view()),
    path('notifications/rud/<int:pk>/', NotificationRetrieveUpdateDestroyAPIView.as_view()),
]