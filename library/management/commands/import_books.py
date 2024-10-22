import json
from django.core.management.base import BaseCommand
from library.models import Book, Author,Shelf
from django.db import transaction

class Command(BaseCommand):
    help = 'Load books from a JSON Lines file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')
        parser.add_argument(
            '--limit',
            type=int,
            default=10000,
            help='Number of records to load',
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        limit = options['limit']
        count = 0

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if count >= limit:
                        break
                    line = line.strip()
                    if not line:
                        continue  # Skip empty lines
                    try:
                        item = json.loads(line)
                        self.process_record(item)
                        count += 1
                        if count % 100 == 0:
                            self.stdout.write(f'Loaded {count} records...')
                    except json.JSONDecodeError as e:
                        self.stderr.write(self.style.ERROR(f'JSONDecodeError: {e}'))
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} records.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))

    @transaction.atomic
    def process_record(self, item):
        try:
            # Extract data from JSON item
            book_title = item.get('title', 'Unknown Title')
            book_isbn = item.get('isbn', None)
            book_isbn13 = item.get('isbn13', None)
            book_language = item.get('language', 'Unknown Language')

            # Handle average_rating
            book_average_rating_raw = item.get('average_rating', None)
            try:
                book_average_rating = float(book_average_rating_raw) if book_average_rating_raw else None
            except ValueError:
                book_average_rating = None

            book_format = item.get('format', 'Unknown Format')

            # Handle num_pages
            book_num_pages_raw = item.get('num_pages', None)
            try:
                book_num_pages = int(book_num_pages_raw) if book_num_pages_raw else None
            except ValueError:
                book_num_pages = None

            book_publisher = item.get('publisher', 'Unknown Publisher')
            book_publication_date = item.get('publication_date', None)
            book_description = item.get('description', '')
            book_image_url = item.get('image_url', '')
            # Handle shelves
            shelves_data = item.get('shelves', [])
            shelves = []
            for shelf_data in shelves_data:
                shelf_name = shelf_data.get('name', '').lower()
                if shelf_name:
                    shelf, _ = Shelf.objects.get_or_create(name=shelf_name)
                    shelves.append(shelf)

            # Handle authors
            authors_data = item.get('authors', [])
            authors = []
            for author_data in authors_data:
                full_name = author_data.get('name', 'Unknown Author')
                name_parts = full_name.strip().split(' ', 1)
                if len(name_parts) == 2:
                    first_name, last_name = name_parts
                else:
                    first_name = name_parts[0]
                    last_name = ''
                author_id = author_data.get('id', None)
                author, created = Author.objects.get_or_create(
                    first_name=first_name,
                    last_name=last_name,
                    defaults={'date_of_birth': None}
                )
                authors.append(author)

            # Create the book
            book = Book.objects.create(
                title=book_title,
                isbn=book_isbn,
                isbn13=book_isbn13,
                language=book_language,
                average_rating=book_average_rating,
                book_format=book_format,
                num_pages=book_num_pages,
                publisher=book_publisher,
                publication_date=book_publication_date,
                description=book_description,
                image_url=book_image_url
            )
            book.shelves.set(shelves)
            # Associate authors with the book
            book.authors.set(authors)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to process record: {e}'))
