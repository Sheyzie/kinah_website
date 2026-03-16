from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from faker import Faker
from decimal import Decimal
import random
import uuid

from accounts.models import Role
from accounts.permissions import DefaultPermission
from finance.models import Address, Order, OrderItem, Payment, Coupon
from logistics.models import Vehicle, Dispatch
from products.models import ProductsCategory, ProductsType, Product, Review
from accounts.models import OTPRecord

fake = Faker()
User = get_user_model()


if not settings.DEBUG:
    raise Exception("Seeding is disabled in production")


# self.stdout.write(self.style.SUCCESS("Users created"))
# self.stdout.write(self.style.WARNING("Creating orders..."))
# self.stdout.write(self.style.ERROR("Something failed"))

class Command(BaseCommand):
    help = "Seed database with sample data"

    def add_arguments(self, parser):

        parser.add_argument(
            "--users",
            type=int,
            default=20,
            help="Number of users to create",
        )

        parser.add_argument(
            "--products",
            type=int,
            default=50,
            help="Number of products to create",
        )

        parser.add_argument(
            "--orders",
            type=int,
            default=100,
            help="Number of orders to create",
        )

        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )

    def handle(self, *args, **options):

        users_count = options["users"]
        products_count = options["products"]
        orders_count = options["orders"]
        clear_db = options["clear"]

        # python manage.py seed_db --users 50 --orders 200
        # python manage.py seed_db --clear

        if clear_db:
            self.stdout.write(self.style.SUCCESS("Clearing existing data..."))
            self.clear_database()
            self.stdout.write(self.style.SUCCESS("Data cleared successfully"))
            return
        
        self.stdout.write(self.style.SUCCESS("Seeding database..."))
        
        with transaction.atomic():
            try:
                users = self.seed_users(users_count)
                products = self.seed_products(products_count)
                addresses = self.seed_addresses(users)
                vehicles = self.seed_vehicles()
                dispatches = self.seed_dispatch(users, vehicles, addresses)
                orders = self.seed_orders(users, addresses, orders_count)
                self.seed_order_items(orders, products)
                self.seed_payments(orders)
                self.seed_reviews(users, products)
                self.seed_coupons()
                self.seed_otps(users, orders)

            except Exception as e:
                self.stderr.write(self.style.ERROR('Error seeding database.'))
                self.stderr.write(self.style.ERROR(str(e)))
                self.stderr.write(self.style.ERROR(e.with_traceback()))

            self.stdout.write(self.style.SUCCESS("Database seeded successfully"))


    def seed_roles(self):
        self.stdout.write('Seeding roles...')
        roles = [
            {
                'name': "admin",
                'default': {
                    'color': '#00ff00',
                    'is_admin': True,
                    'is_default': False,
                    'is_active': True,
                    'is_editable': False
                },             
            },
            {
                'name': "buyer",
                'default': {
                    'color': "#ee3b9d",
                    'is_admin': False,
                    'is_default': True,
                    'is_active': True,
                    'is_editable': False
                },
            },
            {
                'name': "staff",
                'default': {
                    'color': "#ee3b9d",
                    'is_admin': False,
                    'is_default': True,
                    'is_active': True,
                    'is_editable': False
                },
            },
            {
                'name': "dispatcher",
                'default': {
                    'color': "#b700ff",
                    'is_admin': False,
                    'is_default': False,
                    'is_active': True,
                    'is_editable': False
                },
            },
        ]

        objs = []

        for role in roles:
            obj, _ = Role.objects.get_or_create(role_name=role['name'], defaults=role['default'])
            objs.append(obj)

            perms = DefaultPermission(obj)
            
            if role['name'] == 'buyer':
                perms.set_buyer_default_perms()
            if role['name'] == 'admin':
                perms.set_admin_default_perms()
            if role['name'] == 'staff':
                perms.set_staff_default_perms()
            if role['name'] == 'dispatcher':
                perms.set_dispatcher_default_perms()

        self.stdout.write('Roles seeded successfully')
        return objs

    def seed_users(self, count=20):
        self.stdout.write('Seeding users...')
        roles = self.seed_roles()
        
        users = []

        for i in range(count):

            user = User.objects.create_user(
                email=fake.unique.email(),
                phone=f"+23480{random.randint(10000000,99999999)}",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password="password123",
                role=random.choice(roles)
            )

            users.append(user)

        self.stdout.write(f'({len(users)}/{count}) users seeded successfully')
        return users
    
    def seed_products_meta(self):
    
        categories = []
        types = []

        for name in ["male", "female", "children"]:

            category, _ = ProductsCategory.objects.get_or_create(
                name=name,
                defaults={"color": fake.hex_color()}
            )

            categories.append(category)

        for name in ["shirt", "trouser", "dress", 'skirt', 'unisex']:

            type_obj, _ = ProductsType.objects.get_or_create(
                name=name,
                defaults={"color": fake.hex_color()}
            )

            types.append(type_obj)

        return categories, types
    
    def seed_products(self, count=50):
        self.stdout.write('Seeding products...')
        products = []

        categories, types = self.seed_products_meta()

        for _ in range(30):
            name = fake.unique.word()
            category = random.choice(categories)
            product_type = random.choice(types)

            exist = Product.objects.filter(name=name, category=category, type=product_type).exists()

            if exist:
                continue

            product = Product.objects.create(
                name=name,
                category=category,
                type=product_type,
                package_type=random.choice(["single","bundle"]),
                price=Decimal(random.randint(1000,20000)),
                quantity=random.randint(10,200),
                description=fake.text(),
            )

            products.append(product)
        self.stdout.write(f'({len(products)}/{count}) products seeded successfully')
        return products
    
    def seed_addresses(self, users):
        self.stdout.write('Seeding address...')
        addresses = []

        for user in users:

            address = Address.objects.create(
                user=user,
                address_type="shipping",
                full_name=user.full_name,
                street_address=fake.street_address(),
                city=fake.city(),
                state=fake.state(),
                country="Nigeria",
            )

            addresses.append(address)

        self.stdout.write(f'({len(addresses)}/{len(users)}) address created for {len(users)} users')
        return addresses
    
    def seed_vehicles(self):
        self.stdout.write('Seeding vehicles...')
        vehicles = []

        for _ in range(5):

            vehicle = Vehicle.objects.create(
                vehicle_type="Bike",
                vehicle_brand="Honda",
                plate_number=f"ABC-{random.randint(100,999)}",
                plate_state="Lagos",
                plate_country="Nigeria",
                color="Red"
            )

            vehicles.append(vehicle)
        self.stdout.write('Vehicles seeded successfully')
        return vehicles
    
    def seed_dispatch(self, users, vehicles, addresses):
        self.stdout.write('Seeding dispatches...')
        dispatchers = [u for u in users if u.role.role_name == "dispatcher"]

        dispatches = []

        for i, driver in enumerate(dispatchers):

            exist = Dispatch.objects.filter(vehicle=vehicles[i % len(vehicles)]).exists()

            if exist:
                continue

            dispatch = Dispatch.objects.create(
                driver=driver,
                company_name="Kinah Logistics",
                company_address=random.choice(addresses),
                vehicle=vehicles[i % len(vehicles)],
                is_active=True
            )

            dispatches.append(dispatch)
        self.stdout.write(f'{len(dispatches)}/{len(dispatchers)} dispatches seeded successfully')
        return dispatches
    
    def seed_orders(self, users, addresses, count=20):
        self.stdout.write('Seeding orders...')
        orders = []

        for _ in range(count):

            user = random.choice(users)

            order = Order.objects.create(
                user=user,
                shipping_address=random.choice(addresses),
                billing_address=random.choice(addresses),
                payment_method="card",
                tracking_number=str(uuid.uuid4())[:10],
                customer_email=user.email
            )

            orders.append(order)
        self.stdout.write(f'({len(orders)}/{count} orders seeded successfully')
        return orders
    
    def seed_order_items(self, orders, products):

        for order in orders:

            for _ in range(random.randint(1,3)):

                product = random.choice(products)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_category=product.category.name,
                    product_type=product.type.name,
                    package_type=product.package_type,
                    quantity=random.randint(1,3),
                    unit_price=product.price
                )

    def seed_payments(self, orders):
        self.stdout.write('Seeding payments...')
        for order in orders:

            Payment.objects.create(
                order=order,
                transaction_id=str(uuid.uuid4()),
                payment_method="card",
                amount=order.total_amount,
                status="processing"
            )
        self.stdout.write(f'Payments seeded seeded for {len(orders)}')

    def seed_reviews(self, users, products):
        self.stdout.write('Seeding reviews...')
        created = 0
        for _ in range(20):

            try:
                Review.objects.create(
                    product=random.choice(products),
                    user=random.choice(users),
                    rating=random.randint(3,5),
                    comment=fake.sentence()
                )
                created += 1
            except:
                pass

        self.stdout.write(f'({created}/20) reviews created')

    def seed_otps(self, users, orders):
        self.stdout.write('Seeding otp...')
        for _ in range(10):

            OTPRecord.objects.create(
                otp=str(random.randint(100000,999999)),
                user=random.choice(users),
                order=random.choice(orders),
                event=random.choice(["verify","cancel"])
            )

        self.stdout.write('OTP seeded successfully')

    def seed_coupons(self):
        self.stdout.write('Seeding coupons...')
        for _ in range(5):

            Coupon.objects.create(
                code=fake.unique.lexify(text="SALE????"),
                discount_type="percent",
                discount_value=random.randint(5,20),
                valid_from=timezone.now(),
                valid_to=timezone.now() + timedelta(days=30),
                min_order_amount=1000
            )
        self.stdout.write('Coupons seeded successfully')

    def clear_database(self):

        OrderItem.objects.all().delete()
        Payment.objects.all().delete()
        Order.objects.all().delete()
        Dispatch.objects.all().delete()
        Vehicle.objects.all().delete()
        Product.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()


