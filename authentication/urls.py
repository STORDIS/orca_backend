from django.urls import path

from authentication import views

urlpatterns = [
    path("user/register", views.RegisterView.as_view()),
    path('login', views.LoginView.as_view(), name="login"),
    path("user/change_password", views.ChangePasswordView.as_view()),
    path("user/delete", views.DeleteUserView.as_view()),
    path("users", views.UserList.as_view()),
    path("user/update", views.UpdateUserView.as_view()),
    path("user/<pk>", views.GetUserView.as_view()),
    path("user/is_admin/<value>", views.UpdateIsStaffView.as_view()),
]