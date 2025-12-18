from rest_framework import serializers
from .models import Author, ReadingHall, Reader, Book, BookCopy, BookAssignment


class AuthorSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books_count']
    
    def get_books_count(self, obj):
        return obj.books.count()


class ReadingHallSerializer(serializers.ModelSerializer):
    readers_count = serializers.SerializerMethodField()
    books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReadingHall
        fields = ['id', 'number', 'name', 'capacity', 'readers_count', 'books_count']
    
    def get_readers_count(self, obj):
        return obj.readers.filter(is_active=True).count()
    
    def get_books_count(self, obj):
        return obj.book_copies.filter(quantity__gt=0).count()


class ReaderSerializer(serializers.ModelSerializer):
    reading_hall_detail = ReadingHallSerializer(source='reading_hall', read_only=True)
    assigned_books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Reader
        fields = [
            'id', 'ticket_number', 'full_name', 'passport_number', 
            'birth_date', 'address', 'phone', 'education', 'has_degree',
            'reading_hall', 'reading_hall_detail', 'registration_date',
            'is_active', 'assigned_books_count'
        ]
    
    def get_assigned_books_count(self, obj):
        return obj.book_assignments.filter(is_returned=False).count()


class BookCopyNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for BookCopy when used inside BookSerializer (avoids circular reference)"""
    reading_hall_detail = ReadingHallSerializer(source='reading_hall', read_only=True)
    
    class Meta:
        model = BookCopy
        fields = ['id', 'book', 'reading_hall', 'reading_hall_detail', 'quantity']


class BookSerializer(serializers.ModelSerializer):
    authors_detail = AuthorSerializer(source='authors', many=True, read_only=True)
    copies_detail = serializers.SerializerMethodField()
    assignments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'authors', 'authors_detail', 'publisher',
            'publication_year', 'section', 'code', 'assignment_date',
            'copies_detail', 'assignments_count'
        ]
    
    def get_copies_detail(self, obj):
        copies = obj.copies.all()
        return BookCopyNestedSerializer(copies, many=True).data
    
    def get_assignments_count(self, obj):
        return obj.assignments.filter(is_returned=False).count()


class BookCopySerializer(serializers.ModelSerializer):
    book_detail = BookSerializer(source='book', read_only=True)
    reading_hall_detail = ReadingHallSerializer(source='reading_hall', read_only=True)
    
    class Meta:
        model = BookCopy
        fields = ['id', 'book', 'book_detail', 'reading_hall', 'reading_hall_detail', 'quantity']


class BookAssignmentSerializer(serializers.ModelSerializer):
    book_detail = BookSerializer(source='book', read_only=True)
    reader_detail = ReaderSerializer(source='reader', read_only=True)
    
    class Meta:
        model = BookAssignment
        fields = [
            'id', 'book', 'book_detail', 'reader', 'reader_detail',
            'assignment_date', 'is_returned'
        ]

