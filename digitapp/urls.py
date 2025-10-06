from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.registration, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('customer_dashboard/' , views.customer_dashboard, name='customer_dashboard'),
    path('repair_request/', views.repair_request, name="repair_request"),

    path('my_requests/', views.my_requests, name='my_requests'),
    
    path('admin_dashboard/' , views.admin_dashboard, name='admin_dashboard'),
   
    path('view_requests/', views.view_requests, name='view_requests'),

   # Optional: you can keep assign_technician as a POST action in view_requests form
    path('assign_technician/<int:req_id>/', views.assign_technician, name='assign_technician'),
    path('view_customers/', views.view_customers, name='view_customers'),
    path('edit_customer/<int:customer_id>/', views.edit_customer, name='edit_customer'),
    path('manage_technicians/', views.manage_technicians, name='manage_technicians'),



    path('technician_dashboard/', views.technician_dashboard, name='technician_dashboard'),
    #path('job/<int:req_id>/', views.technician_job_detail, name='technician_job_detail'),
    path('job_detail/<int:req_id>/', views.technician_job_detail, name='technician_job_detail'),
    path('update_job/<int:req_id>/', views.update_job, name='update_job'),
    path('feedback/<int:req_id>/', views.technician_feedback_detail, name='technician_feedback_detail'),


    path('feedback/<int:req_id>/', views.feedback_form, name='feedback_form'),
    path('admin_feedbacks/', views.admin_feedbacks, name='admin_feedbacks'),
   # path('technician_feedbacks/', views.technician_feedbacks, name='technician_feedbacks'),
    path("add_feedback/<int:request_id>/", views.add_feedback, name="add_feedback"),
   # path('technician/feedback/<int:req_id>/', views.technician_feedback_detail, name='technician_feedback_detail'),





# path('assign_technician/<int:req_id>/' , views.assign_technician, name='assign_technician'),
]
