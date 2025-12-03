from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Tour, Reservation, Review
from .forms import UserRegistrationForm, UserLoginForm, ReservationForm, ReviewForm


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('tour_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'tours_app/register.html', {'form': form})


def login_view(request):
    """Вход в систему"""
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже авторизованы.')
        return redirect('tour_list')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('tour_list')
    else:
        form = UserLoginForm()
    return render(request, 'tours_app/login.html', {'form': form})


@login_required
def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('tour_list')


class TourListView(ListView):
    """Список туров с поиском и пагинацией"""
    model = Tour
    template_name = 'tours_app/tour_list.html'
    context_object_name = 'tours'
    paginate_by = 5
    
    def get_queryset(self):
        queryset = Tour.objects.all()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(agency__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(country__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class TourDetailView(DetailView):
    """Детальный просмотр тура"""
    model = Tour
    template_name = 'tours_app/tour_detail.html'
    context_object_name = 'tour'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()[:10]
        if self.request.user.is_authenticated:
            context['user_reservation'] = Reservation.objects.filter(
                user=self.request.user,
                tour=self.object
            ).first()
            context['user_review'] = Review.objects.filter(
                user=self.request.user,
                tour=self.object
            ).first()
        return context


@login_required
def create_reservation(request, tour_id):
    """Создание резервирования тура"""
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.tour = tour
            reservation.save()
            messages.success(request, 'Резервирование создано! Ожидайте подтверждения администратора.')
            return redirect('tour_detail', pk=tour_id)
    else:
        form = ReservationForm(initial={'tour': tour})
    return render(request, 'tours_app/reservation_create.html', {'form': form, 'tour': tour})


@login_required
def my_reservations(request):
    """Список резервирований пользователя"""
    reservations = Reservation.objects.filter(user=request.user).select_related('tour')
    return render(request, 'tours_app/my_reservations.html', {'reservations': reservations})


@login_required
def edit_reservation(request, reservation_id):
    """Редактирование резервирования"""
    reservation = get_object_or_404(Reservation, pk=reservation_id, user=request.user)
    if request.method == 'POST':
        # Можно добавить форму для редактирования, пока просто удаляем и создаем новое
        messages.info(request, 'Для изменения резервирования удалите старое и создайте новое.')
        return redirect('my_reservations')
    return render(request, 'tours_app/reservation_edit.html', {'reservation': reservation})


@login_required
def delete_reservation(request, reservation_id):
    """Удаление резервирования"""
    reservation = get_object_or_404(Reservation, pk=reservation_id, user=request.user)
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, 'Резервирование удалено.')
        return redirect('my_reservations')
    return render(request, 'tours_app/reservation_delete.html', {'reservation': reservation})


@login_required
def create_review(request, tour_id):
    """Создание отзыва к туру"""
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.tour = tour
            review.save()
            messages.success(request, 'Отзыв добавлен!')
            return redirect('tour_detail', pk=tour_id)
    else:
        form = ReviewForm()
    return render(request, 'tours_app/review_create.html', {'form': form, 'tour': tour})


@staff_member_required
def sold_tours_by_country(request):
    """Таблица проданных туров по странам (только для админов)"""
    sold_tours = Reservation.objects.filter(confirmed=True).values('tour__country').annotate(
        total_count=Count('id'),
        total_revenue=Sum('tour__price')
    ).order_by('-total_count')
    
    return render(request, 'tours_app/sold_tours_by_country.html', {
        'sold_tours': sold_tours
    })


@login_required
def admin_dashboard(request):
    """Панель администратора"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав доступа к этой странице.')
        return redirect('tour_list')
    
    total_reservations = Reservation.objects.count()
    confirmed_reservations = Reservation.objects.filter(confirmed=True).count()
    pending_reservations = Reservation.objects.filter(confirmed=False).count()
    total_tours = Tour.objects.count()
    
    context = {
        'total_reservations': total_reservations,
        'confirmed_reservations': confirmed_reservations,
        'pending_reservations': pending_reservations,
        'total_tours': total_tours,
    }
    return render(request, 'tours_app/admin_dashboard.html', context)
