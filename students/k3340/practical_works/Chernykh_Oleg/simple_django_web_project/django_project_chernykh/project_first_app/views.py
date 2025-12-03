from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from .models import Owner, Car
from .forms import UserOwnerForm, OwnerForm, CarForm


def owners_list(request):
    """Функциональное представление для списка всех владельцев"""
    owners = Owner.objects.select_related('user').all()
    return render(request, 'owners_list.html', {'owners': owners})


def owner_create(request):
    """Функциональное представление для создания владельца (пользователя)"""
    if request.method == 'POST':
        form = UserOwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('owners_list')
    else:
        form = UserOwnerForm()
    return render(request, 'owner_create.html', {'form': form})


def owner_detail(request, owner_id):
    try:
        owner = Owner.objects.get(pk=owner_id)
    except Owner.DoesNotExist:
        raise Http404("Owner does not exist")
    return render(request, 'owner.html', {'owner': owner})


class CarListView(ListView):
    """Классовое представление для списка всех автомобилей"""
    model = Car
    template_name = 'cars_list.html'
    context_object_name = 'cars'


class CarDetailView(DetailView):
    """Классовое представление для детального просмотра автомобиля"""
    model = Car
    template_name = 'car_detail.html'
    context_object_name = 'car'


class CarCreateView(CreateView):
    """Классовое представление для создания автомобиля"""
    model = Car
    form_class = CarForm
    template_name = 'car_create.html'
    success_url = reverse_lazy('cars_list')


class CarUpdateView(UpdateView):
    """Классовое представление для обновления автомобиля"""
    model = Car
    form_class = CarForm
    template_name = 'car_update.html'
    success_url = reverse_lazy('cars_list')


class CarDeleteView(DeleteView):
    """Классовое представление для удаления автомобиля"""
    model = Car
    template_name = 'car_delete.html'
    success_url = reverse_lazy('cars_list')
