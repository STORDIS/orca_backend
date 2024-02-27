from django.urls import include, re_path, path
from oauth2_provider import views as oauth2_views
from authentication import views


urlpatterns = [
    re_path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    re_path('authorize/', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    re_path('token/', views.CustomTokenView.as_view(), name="token"),
    re_path('revoke-token/', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
    re_path('callback', views.callback),
    path('login', views.login, name="login"),
    path("user/change_password", views.ChangePasswordView.as_view()),
    path("user/is_admin/<value>", views.UpdateIsStaffView.as_view()),
    path("user/register", views.CreateUserView.as_view()),
    path("user/update", views.UpdateUserView.as_view()),
    path("user/delete", views.DeleteUserView.as_view()),
    path("user/<pk>", views.GetUserView.as_view()),
    path("users", views.UserList.as_view()),
]