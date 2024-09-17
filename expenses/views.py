from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Category, Expense
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
# Create your views here.



def search_expenses(request):
    if request.method == 'POST':
        try:
            # Check if request body is not empty
            if not request.body:
                return JsonResponse({'error': 'Empty request body'}, status=400)

            # Attempt to load the JSON from the request body
            search_str = json.loads(request.body).get('searchText')
            
            if not search_str:
                return JsonResponse([], safe=False)  # Return empty if no search string is provided
            
            # Your filtering logic
            expenses = Expense.objects.filter(
                amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
                date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
                description__icontains=search_str, owner=request.user) | Expense.objects.filter(
                category__icontains=search_str, owner=request.user)

            # Return filtered expenses as JSON
            data = expenses.values()
            return JsonResponse(list(data), safe=False)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
    


@login_required(login_url='authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'expenses/index.html', context)



def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST  # This will preserve the data in case of errors
    }

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category = request.POST.get('category')
        date = request.POST.get('expense_date')

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expenses.html', context)
        
        elif not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/add_expenses.html', context)
        
        elif not date:
            messages.error(request, 'Date is required')
            return render(request, 'expenses/add_expenses.html', context)
        
        # Create the Expense object only if validation passes
        Expense.objects.create(owner=request.user, amount=amount, description=description,
                               category=category, date=date)
        messages.success(request, 'Expense added successfully')
        
        return redirect('expenses')
    
    return render(request, 'expenses/add_expenses.html', context)
    

def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')
    

def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')