from django.core.management.base import BaseCommand
from library.models import Book, Author
from django.db import transaction

class Command(BaseCommand):
    help = 'Delete all entries from Book and Author models.'

    def handle(self, *args, **options):
        confirm = input("Are you sure you want to delete all Book and Author entries? Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.WARNING("Operation cancelled. No data was deleted."))
            return

        try:
            with transaction.atomic():
                # Clear ManyToMany relationships
                for book in Book.objects.all():
                    book.authors.clear()

                # Delete all Book and Author entries
                book_count = Book.objects.count()
                author_count = Author.objects.count()

                Book.objects.all().delete()
                Author.objects.all().delete()

            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {book_count} Book entries and {author_count} Author entries."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {str(e)}"))
