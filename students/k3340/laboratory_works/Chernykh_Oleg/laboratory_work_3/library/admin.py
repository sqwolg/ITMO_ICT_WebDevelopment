from django.contrib import admin
from .models import Author, ReadingHall, Reader, Book, BookCopy, BookAssignment


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(ReadingHall)
class ReadingHallAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'capacity']
    search_fields = ['name', 'number']


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'full_name', 'reading_hall', 'education', 'is_active']
    list_filter = ['education', 'has_degree', 'is_active', 'reading_hall']
    search_fields = ['ticket_number', 'full_name', 'passport_number']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'publisher', 'publication_year', 'section']
    list_filter = ['section', 'publication_year']
    search_fields = ['title', 'code', 'publisher']
    filter_horizontal = ['authors']


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ['book', 'reading_hall', 'quantity']
    list_filter = ['reading_hall']
    search_fields = ['book__title', 'book__code']


@admin.register(BookAssignment)
class BookAssignmentAdmin(admin.ModelAdmin):
    list_display = ['book', 'reader', 'assignment_date', 'is_returned']
    list_filter = ['is_returned', 'assignment_date']
    search_fields = ['book__title', 'reader__full_name', 'reader__ticket_number']

