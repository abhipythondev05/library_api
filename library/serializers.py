from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Writer, Publication, UserFavorite, LibraryShelf
from django.db import transaction

CustomUser = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'password',
            'password_confirm',
            'email',
            'first_name',
            'last_name',
        )
        extra_kwargs = {'email': {'required': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user

class WriterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Writer
        fields = ('id', 'given_name', 'surname', 'birth_date')
        extra_kwargs = {
            'given_name': {'required': True},
            'surname': {'required': True},
        }

    def validate(self, attrs):
        if not attrs.get('given_name') or not attrs.get('surname'):
            raise serializers.ValidationError("Writer's first and last name are required.")
        return attrs

class LibraryShelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryShelf
        fields = ['shelf_name']

class PublicationSerializer(serializers.ModelSerializer):
    writers = WriterSerializer(many=True)
    associated_shelves = LibraryShelfSerializer(many=True, required=False)

    class Meta:
        model = Publication
        fields = (
            'id', 'book_title', 'pub_date', 'book_isbn', 'writers', 'associated_shelves', 'book_description'
        )
        extra_kwargs = {
            'book_title': {'required': True},
            'book_isbn': {'required': True},
        }

    def validate(self, attrs):
        if not attrs.get('book_title') or not attrs.get('book_isbn'):
            raise serializers.ValidationError("Both title and ISBN are required.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        writers_data = validated_data.pop('writers')
        shelves_data = validated_data.pop('associated_shelves', [])
        book_isbn = validated_data.get('book_isbn')

        if Publication.objects.filter(book_isbn=book_isbn).exists():
            raise serializers.ValidationError({'book_isbn': 'A publication with this ISBN already exists.'})

        publication = Publication.objects.create(**validated_data)

        for writer_data in writers_data:
            writer = self._get_or_create_writer(writer_data)
            publication.writers.add(writer)

        for shelf_data in shelves_data:
            shelf, _ = LibraryShelf.objects.get_or_create(shelf_name=shelf_data['shelf_name'])
            publication.associated_shelves.add(shelf)

        return publication

    @transaction.atomic
    def update(self, instance, validated_data):
        writers_data = validated_data.pop('writers')
        shelves_data = validated_data.pop('associated_shelves', [])

        instance.book_title = validated_data.get('book_title', instance.book_title)
        instance.pub_date = validated_data.get('pub_date', instance.pub_date)
        book_isbn = validated_data.get('book_isbn', instance.book_isbn)

        if book_isbn != instance.book_isbn and Publication.objects.filter(book_isbn=book_isbn).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({'book_isbn': 'A publication with this ISBN already exists.'})
        instance.book_isbn = book_isbn

        instance.book_description = validated_data.get('book_description', instance.book_description)
        instance.save()

        instance.writers.clear()
        for writer_data in writers_data:
            writer = self._get_or_create_writer(writer_data)
            instance.writers.add(writer)

        instance.associated_shelves.clear()
        for shelf_data in shelves_data:
            shelf, _ = LibraryShelf.objects.get_or_create(shelf_name=shelf_data['shelf_name'])
            instance.associated_shelves.add(shelf)

        return instance

    def _get_or_create_writer(self, writer_data):
        writer, _ = Writer.objects.get_or_create(
            given_name=writer_data['given_name'],
            surname=writer_data['surname'],
            defaults={'birth_date': writer_data.get('birth_date')}
        )
        return writer

class UserFavoriteSerializer(serializers.ModelSerializer):
    publication_id = serializers.IntegerField(write_only=True)
    publication = PublicationSerializer(read_only=True)

    class Meta:
        model = UserFavorite
        fields = ('id', 'publication_id', 'publication', 'date_added')
        read_only_fields = ('id', 'publication', 'date_added')

    def validate(self, attrs):
        user = self.context['request'].user
        publication_id = attrs.get('publication_id')

        if UserFavorite.objects.filter(user=user, publication_id=publication_id).exists():
            raise serializers.ValidationError('This publication is already in your favorites.')

        favorite_count = UserFavorite.objects.filter(user=user).count()
        if favorite_count >= 20:
            raise serializers.ValidationError('You can have a maximum of 20 favorite publications.')

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        publication_id = validated_data.pop('publication_id')
        publication = Publication.objects.get(id=publication_id)
        favorite = UserFavorite.objects.create(user=user, publication=publication)
        return favorite

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add extra responses here
        data.update(
            {
                'user': {
                    'id': self.user.id,
                    'username': self.user.username,
                    'email': self.user.email,
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                }
            }
        )
        return data
