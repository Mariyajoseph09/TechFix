from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser
from .models import ServiceRequest, Payment
from .models import Feedback
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache






def home(request):
    return render(request, 'home.html')  # this will render your HTML page

def registration(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        confirm = request.POST['confirm']
       # user_type = request.POST['user_type']

        #password mathch check

        if password != confirm:
            messages.error(request, "password do not match")
            return redirect('register')


        #email uniquness check

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "email already exists!")
            return redirect('register')

         #save users to database
        user = CustomUser(
            name = name,
            email = email,
            phone = phone,
            password = password,
            user_type = 'Customer'
        ) 
        user.save() 
        messages.success(request, "Registration successful! you can now login.")
        return redirect('login')  
    return render(request, 'registration.html')  # form for new users




def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        

        try:
            user = CustomUser.objects.get(email=email, password=password)


            request.session['user_id'] = user.user_id
            request.session['user_name'] = user.name
            request.session['user_type'] = user.user_type


            if user.user_type == 'Admin':
                return redirect('admin_dashboard')
            elif user.user_type == 'Customer':
                return redirect('customer_dashboard')
            elif user.user_type == 'Technician':
                return redirect('technician_dashboard')


            #redirct based on user_type
            #if user.user_type == 'Admin':
             #   return render(request, 'admin_dashboard.html', {'user': user})
            #elif user.user_type =='Customer':
              #  return render(request, 'customer_dashboard.html', {'user' : user})
           # elif user.user_type == 'Technician' :
            #    return render(request, 'technician_dashboard.html',{'user' :user})


        except CustomUser.DoesNotExist:
            messages.error(request, "invalid email or password!")
            return redirect('login') 


    return render(request, 'login.html')  # login form
   







#@login_required
def customer_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')


    user_id = request.session['user_id']
    user = CustomUser.objects.get(user_id=user_id)

    requests = ServiceRequest.objects.filter(customer=user)    
    
   # requests = ServiceRequest.objects.filter(customer=request.user) 
   

    return render(request, "customer_dashboard.html", {
        "user":user,
        "requests": requests})


def logout_view(request):
    request.session.flush()
    return redirect('home')


#def repair_request(request):
 #   if request.method == "POST":
  #      device = request.POST.get("device")
   #     issue = request.POST.get("issue")
        # For now, just show the data back
    #    return HttpResponse(f"Repair Request Submitted! <br> Device: {device} <br> Issue: {issue}")
    #return render(request, 'repair_form.html')

# Create your views here.
#@login_required
#def repair_request(request):
 #   if request.method == "POST":
  #      device = request.POST.get("device")
   #     issue = request.POST.get("issue")

        # Save to existing DB table
    #    ServiceRequest.objects.create(
     #       customer=request.user,
      #      device=device,
       #     description=issue,
        #    status="Pending"
        #)

        #return redirect('my_requests')  # redirect after submit
    #return render(request, 'repair_form.html')

def repair_request(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = CustomUser.objects.get(user_id=user_id)


    if request.method == "POST":
        device = request.POST.get("device")
        issue = request.POST.get("issue")


        ServiceRequest.objects.create(
            customer=user,
            device=device,
            description=issue,
            status="Pending",
            warranty_status="No",
            assigned_to=None
        )        


        return redirect('my_requests')
    return render(request, 'repair_form.html', {"user": user})    



#@login_required
def my_requests(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = CustomUser.objects.get(user_id=user_id)

    requests_list = ServiceRequest.objects.filter(customer=user)
    # IDs of service requests that already have feedback
    feedbacked_ids = list(
        Feedback.objects.filter(service_request__in=requests_list)
        .values_list('service_request__request_id', flat=True)
    )

    # Handle feedback submission (POST)
    if request.method == "POST":
        request_id = request.POST.get("request_id")
        feedback_text = request.POST.get("feedback")
        rating = int(request.POST.get("rating", 0))

        # Validate
        service_request = ServiceRequest.objects.get(request_id=request_id)
        if service_request.status != "Completed":
            messages.error(request, "Feedback can only be submitted for completed requests.")
        elif Feedback.objects.filter(service_request=service_request).exists():
            messages.info(request, "Feedback already submitted for this request.")
        elif rating < 1 or rating > 5:
            messages.error(request, "Please select a valid rating (1-5).")
        else:
            # Create Feedback
            Feedback.objects.create(
                service_request=service_request,
                customer=user,
                rating=rating,
                comments=feedback_text
            )
            messages.success(request, "Feedback submitted successfully!")
            feedbacked_ids.append(service_request.request_id)  # update list to hide form immediately

    return render(request, 'my_requests.html', {
        'requests': requests_list,
        'user': user,
        'feedbacked_ids': feedbacked_ids
    })








    

def admin_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')



    user_id  = request.session['user_id']
    user = CustomUser.objects.get(user_id=user_id)

    if user.user_type != 'Admin':
        messages.error(request, "Access denied!")
        return redirect('login')


    return render(request, 'admin_dashboard.html', {'user': user})
        
    # Get all service requests
   # requests = ServiceRequest.objects.select_related('customer', 'assigned_to').all()


    # Get all technicians for assignment
   # technicians = CustomUser.objects.filter(user_type='Technician')


    #return render(request, 'admin_dashboard.html', {    
     #   'user': user,
      #  'requests': requests,
       # 'technicians': technicians
    #})

 
#def assign_technician(request, req_id):
 #   if request.method == 'POST':
  #      technician_id = request.POST.get('technician_id')
   #     if technician_id:
    #        req = ServiceRequest.objects.get(request_id=req_id)
     #       tech = CustomUser.objects.get(user_id=technician_id)
      #      req.assigned_to = tech
       #     req.status = "In Progress"
        #    req.save()
   # return redirect('admin_dashboard')
    #return redirect('view_requests')



def assign_technician(request, req_id):
    if request.method == 'POST':
        technician_id = request.POST.get('technician_id')
        if technician_id:
            req = ServiceRequest.objects.get(request_id=req_id)

            # Prevent assigning if already completed
            if req.status == "Completed":
                messages.warning(request, "Cannot assign technician. Work is already completed.")
                return redirect('view_requests')

            # Prevent reassigning if already in progress
            if req.status == "In Progress" and req.assigned_to:
                messages.warning(request, "Technician is already assigned for this request.")
                return redirect('view_requests')

            # Normal assignment
            tech = CustomUser.objects.get(user_id=technician_id)
            req.assigned_to = tech
            req.status = "In Progress"
            req.save()
            messages.success(request, f"Technician {tech.name} assigned successfully!")

    return redirect('view_requests')





def view_requests(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = CustomUser.objects.get(user_id=user_id)

    if user.user_type != 'Admin':
        messages.error(request, "Access denied!")
        return redirect('login')

    requests = ServiceRequest.objects.select_related('customer', 'assigned_to').all()
    technicians = CustomUser.objects.filter(user_type='Technician')

    return render(request, 'view_requests.html', {
        'requests': requests,
        'technicians': technicians,
        'user': user
    })



# Edit customer details
def view_customers(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = CustomUser.objects.get(user_id=user_id)

    if user.user_type != 'Admin':
        messages.error(request, "Access denied!")
        return redirect('login')

    customers = CustomUser.objects.filter(user_type='Customer')
    return render(request, 'view_customers.html', {'user': user, 'customers': customers})


def edit_customer(request, customer_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    admin = CustomUser.objects.get(user_id=user_id)

    if admin.user_type != 'Admin':
        messages.error(request, "Access denied!")
        return redirect('login')

    customer = CustomUser.objects.get(user_id=customer_id)

    if request.method == "POST":
        customer.name = request.POST.get('name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone')
        customer.password = request.POST.get('password')
        customer.save()
        return redirect('view_customers')

    return render(request, 'edit_customer.html', {'customer': customer})




def manage_technicians(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = CustomUser.objects.get(user_id=user_id)

    # Add new technician
    if request.method == 'POST' and 'add_tech' in request.POST:
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()

        if not name or not email or not phone or not password:
            messages.error(request, "All fields are required to add a technician.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
        else:
            CustomUser.objects.create(
                name=name,
                email=email,
                phone=phone,
                password=password,
                user_type='Technician'
            )
        return redirect('manage_technicians')

    # Edit technician
    if request.method == 'POST' and 'edit_tech' in request.POST:
        tech_id = request.POST.get('tech_id')
        if tech_id:
            tech = CustomUser.objects.get(user_id=tech_id)
            tech.name = request.POST.get('name', tech.name)
            tech.email = request.POST.get('email', tech.email)
            tech.phone = request.POST.get('phone', tech.phone)
            tech.password = request.POST.get('password', tech.password)
            tech.save()
        return redirect('manage_technicians')

    # Delete technician
    if request.method == 'POST' and 'delete_tech' in request.POST:
        tech_id = request.POST.get('tech_id')
        if tech_id:
            CustomUser.objects.get(user_id=tech_id).delete()
        return redirect('manage_technicians')

    # Get all technicians
    technicians = CustomUser.objects.filter(user_type='Technician')
    return render(request, 'manage_technicians.html', {'user': user, 'technicians': technicians})








#def technician_dashboard(request):
    # session check
 #   if 'user_id' not in request.session:
  #      return redirect('login')

   # user = CustomUser.objects.get(user_id=request.session['user_id'])
    #if user.user_type != 'Technician':
     #   messages.error(request, "Access denied!")
      #  return redirect('login')

    # all jobs assigned to this technician (most recent first)
    #jobs = ServiceRequest.objects.select_related('customer').filter(assigned_to=user).order_by('-request_date')

    #return render(request, 'technician_dashboard.html', {
     #   'user': user,
      #  'jobs': jobs
    #})

@never_cache
def technician_dashboard(request):
    # Check session
    if 'user_id' not in request.session:
        return redirect('login')

    user = CustomUser.objects.get(user_id=request.session['user_id'])
    if user.user_type != 'Technician':
        messages.error(request, "Access denied!")
        return redirect('login')

    # Assigned jobs for this technician
    jobs = ServiceRequest.objects.select_related('customer').filter(assigned_to=user).order_by('-request_date')

    return render(request, 'technician_dashboard.html', {
        'user': user,
        'jobs': jobs
    })


@never_cache
def technician_job_detail(request, req_id):
    # Check session
    if 'user_id' not in request.session:
        return redirect('login')

    user = CustomUser.objects.get(user_id=request.session['user_id'])
    if user.user_type != 'Technician':
        messages.error(request, "Access denied!")
        return redirect('login')

    job = get_object_or_404(ServiceRequest, request_id=req_id, assigned_to=user)

    return render(request, 'technician_job_detail.html', {
        'user': user,
        'job': job
    })


def update_job(request, req_id):
    # Check session
    if 'user_id' not in request.session:
        return redirect('login')

    user = CustomUser.objects.get(user_id=request.session['user_id'])
    if user.user_type != 'Technician':
        messages.error(request, "Access denied!")
        return redirect('login')

    job = get_object_or_404(ServiceRequest, request_id=req_id, assigned_to=user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'start':
            job.status = "In Progress"
            job.save()
            messages.success(request, "Job started.")
        elif action == 'complete':
            job.status = "Completed"
            job.save()
            messages.success(request, "Job marked as completed.")
        else:
            messages.error(request, "Unknown action.")
        return redirect('technician_dashboard')

    return redirect('technician_job_detail', req_id=req_id)


@never_cache
def technician_feedback_detail(request, req_id):
    # Check session
    if 'user_id' not in request.session:
        return redirect('login')

    user = CustomUser.objects.get(user_id=request.session['user_id'])
    if user.user_type != 'Technician':
        messages.error(request, "Access denied!")
        return redirect('login')

    job = get_object_or_404(ServiceRequest, request_id=req_id, assigned_to=user)

    return render(request, 'technician_feedback_detail.html', {
        'job': job
    })

    
def feedback_form(request, req_id):
    # only customer who owns the request can add feedback, and only if request is completed
    if 'user_id' not in request.session:
        return redirect('login')

    user = CustomUser.objects.get(user_id=request.session['user_id'])
    req = get_object_or_404(ServiceRequest, request_id=req_id)

    # ensure the logged-in user is the customer of this request
    if req.customer != user:
        messages.error(request, "You are not allowed to give feedback for this request.")
        return redirect('my_requests')

    if req.status != 'Completed':
        messages.error(request, "Feedback can be submitted only after the job is completed.")
        return redirect('my_requests')

    # prevent duplicate feedback for same request
    if Feedback.objects.filter(service_request=req).exists():
        messages.info(request, "Feedback already submitted for this request.")
        return redirect('my_requests')

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        comments = request.POST.get('comments', '').strip()

        if rating < 1 or rating > 5:
            messages.error(request, "Please select a valid rating (1-5).")
            return redirect('feedback_form', req_id=req_id)

        Feedback.objects.create(
            service_request=req,
            customer=user,
            rating=rating,
            comments=comments
        )
        messages.success(request, "Thank you — your feedback has been submitted.")
        return redirect('my_requests')

    return render(request, 'feedback_form.html', {'req': req, 'user': user})



def admin_feedbacks(request):
    # Check if logged in
    if 'user_id' not in request.session:
        return redirect('login')

    user = CustomUser.objects.get(user_id=request.session['user_id'])
    if user.user_type != 'Admin':
        messages.error(request, "Access denied!")
        return redirect('login')

    # Get all feedback with related service request and customer
    feedbacks = Feedback.objects.select_related('service_request', 'customer').order_by('-created_at')

    return render(request, 'admin_feedbacks.html', {
        'feedbacks': feedbacks,
        'user': user
    })







def add_feedback(request, request_id):
    service_request = get_object_or_404(ServiceRequest, request_id=request_id)

    # Check if the user is logged in
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to submit feedback.")
        return render(request, "add_feedback.html", {"request_obj": service_request, "user_logged_in": False})

    if request.method == "POST":
        feedback_text = request.POST.get("feedback")
        rating = request.POST.get("rating")

        # Create Feedback object
        Feedback.objects.create(
            service_request=service_request,
            comments=feedback_text,
            rating=rating,
            customer=request.user
        )
        messages.success(request, "Feedback submitted successfully!")
        return render(request, "add_feedback.html", {"request_obj": service_request, "user_logged_in": True})

    return render(request, "add_feedback.html", {"request_obj": service_request, "user_logged_in": True})








#@login_required
#def make_payment(request, service_id):
 #   service = get_object_or_404(ServiceRequest, request_id=service_id)

  #  if service.status != "Completed":
   #     messages.warning(request, "You can only pay for completed services.")
    #    return redirect('view_requests')

  #  if hasattr(service, 'payment') and service.payment.exists():
   #     messages.info(request, "Payment has already been made for this service.")
    #    return redirect('view_requests')
    

    # Check if Payment already exists
    #try:
     #   payment = service.payment
        # If already completed, no need to pay again
      #  if payment.status == 'Completed':
       #     messages.info(request, "Payment has already been completed.")
        #    return redirect('view_requests')
    #except Payment.DoesNotExist:
     #   payment = None  # Payment not yet created

    #if request.method == "POST":
     #   amount = payment.amount if payment else 0  # Take admin-set amount

        # Create Payment record if not exists
       #3 if not payment:
      #     Payment.objects.create(
        #        service_request=service,
         #       amount=amount,
          #      payment_method='Online',
           #     status='Completed'
            #)
        #else:
            # If payment object exists but status not completed, mark it completed
          #  payment.status = 'Completed'
         #   payment.save()

        #messages.success(request, "Payment done successfully!")
        #return redirect('view_requests')

    #return render(request, 'customer_pay.html', {'service': service, 'payment': payment})
   # if request.method == "POST":
    #    amount = request.POST.get('amount')
      #  method = request.POST.get('method')

     #   Payment.objects.create(
      #      service_request=service,
       #     amount=amount,
        #    payment_method='Online',
         #   status='Completed'
        #)

        #messages.success(request, "Payment added successfully!")
        #return redirect('view_requests')

    #return render(request, 'customer_pay.html', {'service': service})




#@login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import ServiceRequest, Payment

def make_payment(request, service_id):
    # Get the service request
    service = get_object_or_404(ServiceRequest, request_id=service_id)

    # ---------------- ADMIN FUNCTIONALITY ----------------
    if request.session.get('user_type') == 'Admin':
        if request.method == "POST":
            amount = request.POST.get("amount")
            method = request.POST.get("method")

            if not amount or not method:
                messages.error(request, "Please enter amount and method.")
                # Stay on the same page
                return redirect(request.META.get('HTTP_REFERER', '/'))

            # Create or update payment for this service request
            payment, created = Payment.objects.get_or_create(
                service_request=service,
                defaults={
                    'amount': amount,
                    'payment_method': method,
                    'status': 'Pending'
                }
            )

            if not created:
                payment.amount = amount
                payment.payment_method = method
                payment.save()

            messages.success(request, "Payment amount added successfully.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # GET request for admin: just redirect back
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # ---------------- CUSTOMER FUNCTIONALITY ----------------
    elif request.session.get('user_type') == 'Customer':
        # Only allow viewing if service is completed
        if service.status != "Completed":
            messages.warning(request, "Service not completed yet.")
            return redirect('view_requests')

        # Try to get payment; can be None
        try:
            payment = service.payment
        except Payment.DoesNotExist:
            payment = None

        # Render a simple page showing the amount (read-only)
        return render(request, 'view_payment.html', {
            'service': service,
            'payment': payment
        })

    # ---------------- NOT LOGGED IN ----------------
    else:
        messages.error(request, "Please log in first.")
        return redirect('login')