from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="income"),
    path('add-income', views.add_income, name="add-income"),
    path('edit-income/<int:id>', views.income_edit, name="income-edit"),
    path('income-delete/<int:id>', views.delete_income, name="income-delete"),
    path('search-income', views.search_income, name="search_income"),
    path('income_source_summary', views.income_source_summary, name="income_source_summary"),
    path('incomestats', views.income_stats_view, name="incomestats")
]
