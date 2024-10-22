from django.core.management.base import BaseCommand
from library.models import Book, BookSimilarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db import transaction

class Command(BaseCommand):
    help = 'Compute and store book similarities using vectorization'

    def handle(self, *args, **options):
        self.stdout.write('Fetching book data...')
        books = Book.objects.all()
        total_books = books.count()
        self.stdout.write(f'Total books: {total_books}')

        # Clear existing similarities
        BookSimilarity.objects.all().delete()

        # Prepare data for vectorization
        self.stdout.write('Preparing data for vectorization...')
        book_ids = []
        documents = []  # Each document represents a book's features

        for book in books:
            book_ids.append(book.id)
            authors = ' '.join([f'{author.first_name}_{author.last_name}' for author in book.authors.all()])
            shelves = ' '.join([shelf.name.replace(' ', '_') for shelf in book.shelves.all()])
            # Combine features
            document = f'{authors} {shelves}'
            documents.append(document)

        self.stdout.write('Vectorizing documents...')
        # Use TF-IDF Vectorizer
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents)

        self.stdout.write('Computing cosine similarity matrix...')
        # Compute cosine similarity matrix
        cosine_sim = cosine_similarity(tfidf_matrix)

        # For each book, find top N similar books
        MAX_SIMILARS = 50  # Adjust as necessary

        self.stdout.write('Storing similarities...')
        similarities_to_create = []
        for idx, book_id in enumerate(book_ids):
            # Get similarity scores for the current book
            sim_scores = cosine_sim[idx]
            # Get indices of the top similar books (excluding itself)
            similar_indices = sim_scores.argsort()[::-1][1:MAX_SIMILARS+1]
            for sim_idx in similar_indices:
                similar_book_id = book_ids[sim_idx]
                similarity = sim_scores[sim_idx]
                if similarity > 0:
                    similarities_to_create.append(
                        BookSimilarity(
                            book1_id=book_id,
                            book2_id=similar_book_id,
                            similarity=similarity
                        )
                    )
            if idx % 100 == 0:
                self.stdout.write(f'Processed {idx} books...')

        # Bulk create all similarities
        self.stdout.write('Bulk creating similarities...')
        with transaction.atomic():
            BookSimilarity.objects.bulk_create(similarities_to_create, batch_size=10000)

        self.stdout.write(self.style.SUCCESS('Successfully computed and stored book similarities.'))
