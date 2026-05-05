from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from foodapp.models import Category, Restaurant, Review, Role, UserProfile

class Command(BaseCommand):
    help = 'Seed starter data for the food review app'

    def handle(self, *args, **kwargs):
        admin_role, _ = Role.objects.get_or_create(name='admin')
        user_role, _ = Role.objects.get_or_create(name='user')

        users = [
            ('bsmith', 'Brian', 'Smith', 'bsmith@example.com', 'Password123!', admin_role),
            ('pjones', 'Paige', 'Jones', 'pjones@example.com', 'Password123!', user_role),
            ('adoe', 'Ava', 'Doe', 'adoe@example.com', 'Password123!', user_role),
            ('mlee', 'Mason', 'Lee', 'mlee@example.com', 'Password123!', user_role),
        ]
        for username, first_name, last_name, email, password, role in users:
            user, created = User.objects.get_or_create(username=username, defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
            })
            if created:
                user.set_password(password)
                user.save()
            UserProfile.objects.get_or_create(user=user, defaults={'role': role})

        categories = ['Mexican', 'Italian', 'American', 'Asian', 'Cafe']
        category_objects = {}
        for name in categories:
            category_objects[name], _ = Category.objects.get_or_create(name=name)

        restaurant_data = [
            ('Red Iguana', 'Salt Lake City', 'Popular Utah restaurant known for Mexican food.', 'Mexican'),
            ("Valters Osteria", 'Salt Lake City', 'Italian fine dining restaurant.', 'Italian'),
            ('Ruths Diner', 'Emigration Canyon', 'Classic diner with breakfast and brunch.', 'American'),
            ('Pretty Bird', 'Salt Lake City', 'Hot chicken sandwiches and fries.', 'American'),
            ('Takashi', 'Salt Lake City', 'Sushi and Japanese dishes.', 'Asian'),
            ('Cafe Niche', 'Salt Lake City', 'Small cafe with local dishes.', 'Cafe'),
            ('Santo Taco', 'Murray', 'Street tacos and burritos.', 'Mexican'),
            ('Osteria Amore', 'Salt Lake City', 'Fresh pasta and Italian plates.', 'Italian'),
            ('Slackwater', 'Sandy', 'Pizza and craft drinks.', 'American'),
            ('Laziz Kitchen', 'Salt Lake City', 'Mediterranean-inspired menu.', 'Cafe'),
            ('Jinya Ramen', 'Midvale', 'Ramen and Japanese comfort food.', 'Asian'),
            ('The Park Cafe', 'Salt Lake City', 'Breakfast and casual comfort food.', 'Cafe'),
        ]
        restaurants = []
        for name, location, description, category_name in restaurant_data:
            restaurant, _ = Restaurant.objects.get_or_create(
                name=name,
                defaults={
                    'location': location,
                    'description': description,
                    'category': category_objects[category_name],
                },
            )
            restaurants.append(restaurant)

        sample_comments = [
            'Great food and quick service.',
            'Loved the atmosphere and the meal.',
            'Solid place, would go again.',
            'Good value and friendly staff.',
            'Fresh food and nice location.',
            'A fun place for dinner with friends.',
        ]
        all_users = list(User.objects.all())
        if not Review.objects.exists():
            for index, restaurant in enumerate(restaurants):
                for offset in range(2):
                    user = all_users[(index + offset) % len(all_users)]
                    Review.objects.create(
                        user=user,
                        restaurant=restaurant,
                        rating=((index + offset) % 5) + 1,
                        comment=sample_comments[(index + offset) % len(sample_comments)],
                    )
        self.stdout.write(self.style.SUCCESS('Seed data created successfully.'))
