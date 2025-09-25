from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.frame_list, name='frame_list'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('add-frame/', views.add_frame, name='add_frame'),
    path('frame/<int:frame_id>/preview/', views.preview_frame, name='preview_frame'),
    path('frame/<int:frame_id>/edit/', views.edit_frame, name='edit_frame'),
    path('frame/<int:frame_id>/delete/', views.delete_frame, name='delete_frame'),
    path('frame_detail/<int:frame_id>/', views.frame_detail, name='frame_detail'),
    path('frame/<int:frame_id>/outputs-ajax/', views.frame_outputs_ajax, name='frame_outputs_ajax'),
    path('delete_output/<int:output_id>/', views.delete_output, name='delete_output'),
]


