from app import app, db, Product, User
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        try:
            # Drop all existing tables
            db.drop_all()
            
            # Create all tables
            db.create_all()
            
            # Check if admin user exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                # Create admin user
                admin = User(
                    username='admin',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully")
            else:
                print("Admin user already exists")
            
            # Clear existing products
            Product.query.delete()
            
            # Sample products
            bouquets = [
                {
                    'name': 'Red Rose Bouquet',
                    'category': 'bouquet',
                    'price': 499.00,
                    'description': 'A stunning arrangement of 10 premium red roses, perfect for expressing love and romance.',
                    'image_url': '/static/images/Bouquets/redrose.webp'
                },
                {
                    'name': 'Mixed Flower Bouquet',
                    'category': 'bouquet',
                    'price': 759.00,
                    'description': 'A vibrant mix of 12 flowers including roses, carnations, and gerberas, creating a colorful celebration of beauty.',
                    'image_url': '/static/images/Bouquets/MixedFlower.webp'
                },
                {
                    'name': 'White Lily Bouquet',
                    'category': 'bouquet',
                    'price': 1499.00,
                    'description': 'An elegant arrangement of 5 pristine white lilies with complementary greenery, symbolizing purity and majesty.',
                    'image_url': '/static/images/Bouquets/whitelilly.webp'
                },
                # {
                #     'name': 'Sunflower Bouquet',
                #     'category': 'bouquet',
                #     'price': 899.00,
                #     'description': 'Bright and cheerful sunflower arrangement',
                #     'image_url': '/static/images/Bouquets/Sunflower.webp'
                # },
                {
                    'name': 'Orchid Bouquet',
                    'category': 'bouquet',
                    'price': 1299.00,
                    'description': 'A sophisticated arrangement of 10 exotic orchids, perfect for special occasions and elegant celebrations.',
                    'image_url': '/static/images/Bouquets/orchid.webp'
                },
                {
                    'name': 'Carnation Bouquet',
                    'category': 'bouquet',
                    'price': 799.00,
                    'description': 'A delightful bouquet of 12 sweet-smelling carnations, available in various colors to match your mood.',
                    'image_url': '/static/images/Bouquets/carnation.webp'
                },
                {
                    'name': 'Gerbera Bouquet',
                    'category': 'bouquet',
                    'price': 599.00,
                    'description': 'A cheerful arrangement of 15 vibrant gerbera daisies, bringing joy and brightness to any occasion.',
                    'image_url': '/static/images/Bouquets/gerbera.webp'
                },
                # {
                #     'name': 'Tulip Bouquet',
                #     'category': 'bouquet',
                #     'price': 1299.00,
                #     'description': 'Fresh tulips in a spring-inspired arrangement',
                #     'image_url': '/static/images/Bouquets/tulip.webp'
                # },
                # {
                #     'name': 'Daisy Bouquet',
                #     'category': 'bouquet',
                #     'price': 699.00,
                #     'description': 'Simple and charming daisy bouquet',
                #     'image_url': '/static/images/Bouquets/Daisy.webp'
                # },
                {
                    'name': 'Rose and Lily Bouquet',
                    'category': 'bouquet',
                    'price': 1299.00,
                    'description': 'A luxurious combination of premium roses and lilies, creating a perfect blend of romance and elegance.',
                    'image_url': '/static/images/Bouquets/roseandlilly.webp'
                }
            ]

            cakes = [
                {
                    'name': 'Chocolate Truffle Cake',
                    'category': 'cake_500g',
                    'price': 599.00,
                    'description': 'Chocolate Truffle Cake..',
                    'image_url': '/static/images/cakes/ctc.webpg'
                },
                {
                    'name': 'Vanilla Cream Cake',
                    'category': 'cake_500g',
                    'price': 499.00,
                    'description': 'Vanilla Cream Cake.',
                    'image_url': '/static/images/products/vanilla-cream-cake.jpg'
                },
                {
                    'name': 'Red Velvet Cake',
                    'category': 'cake_500g',
                    'price': 449.00,
                    'description': 'Red Velvet Cake.',
                    'image_url': '/static/images/products/red-velvet-cake.jpg'
                },
                {
                    'name': 'Fruit Cake',
                    'category': 'cake_500g',
                    'price': 499.00,
                    'description': 'Fruit Cake.',
                    'image_url': '/static/images/products/fruit-cake.jpg'
                },
                {
                    'name': 'Black Forest Cake',
                    'category': 'cake_500g',
                    'price': 599.00,
                    'description': 'Black Forest Cake.',
                    'image_url': '/static/images/products/black-forest-cake.jpg'
                }
            ]

            chocolates = [
                {
                    'name': 'Ferrero Rocher Chocolate Gift Pack (4 Pieces)',
                    'category': 'chocolate',
                    'price': 189.00,
                    'description': 'A premium gift pack containing 4 Ferrero Rocher chocolates, each featuring a whole hazelnut surrounded by chocolate and crispy wafer.',
                    'image_url': '/static/images/products/dark-chocolate-box.jpg'
                },
                {
                    'name': 'Ferrero Rocher Chocolate Gift Pack (16 Pieces)',
                    'category': 'chocolate',
                    'price': 629.00,
                    'description': 'A deluxe gift pack with 16 Ferrero Rocher chocolates, perfect for sharing with family and friends on special occasions.',
                    'image_url': '/static/images/products/milk-chocolate-box.jpg'
                },
                {
                    'name': 'Ferrero Rocher Chocolate Gift Pack (24 Pieces)',
                    'category': 'chocolate',
                    'price': 979.00,
                    'description': 'A grand gift pack featuring 24 Ferrero Rocher chocolates, ideal for corporate gifting or large family celebrations.',
                    'image_url': '/static/images/products/white-chocolate-box.jpg'
                },
                {
                    'name': 'Amul Chocominis chocolate Gift Pack',
                    'category': 'chocolate',
                    'price': 140.00,
                    'description': 'A delightful assortment of Amul Chocominis.',
                    'image_url': '/static/images/products/chocolate-truffles.jpg'
                },
                {
                    'name': 'Cadbury celebrations Assorted Chocolate Gift Pack',
                    'category': 'chocolate',
                    'price': 499.00,
                    'description': 'A premium assortment of Cadbury chocolates including Dairy Milk, 5 Star, Gems, and other popular variants.',
                    'image_url': '/static/images/products/chocolate-assortment.jpg'
                },
                # {
                #     'name': 'Chocolate Hearts',
                #     'category': 'chocolate',
                #     'price': 199.00,
                #     'description': 'Romantic chocolate hearts box',
                #     'image_url': '/static/images/products/chocolate-hearts.jpg'
                # },
                # {
                #     'name': 'Chocolate Bars Set',
                #     'category': 'chocolate',
                #     'price': 349.00,
                #     'description': 'Set of premium chocolate bars',
                #     'image_url': '/static/images/products/chocolate-bars.jpg'
                # },
                # {
                #     'name': 'Chocolate Pralines',
                #     'category': 'chocolate',
                #     'price': 449.00,
                #     'description': 'Luxury chocolate pralines box',
                #     'image_url': '/static/images/products/chocolate-pralines.jpg'
                # },
                # {
                #     'name': 'Chocolate Gift Hamper',
                #     'category': 'chocolate',
                #     'price': 599.00,
                #     'description': 'Deluxe chocolate gift hamper',
                #     'image_url': '/static/images/products/chocolate-hamper.jpg'
                # },
                # {
                #     'name': 'Chocolate Dipped Fruits',
                #     'category': 'chocolate',
                #     'price': 399.00,
                #     'description': 'Chocolate dipped fruits assortment',
                #     'image_url': '/static/images/products/chocolate-fruits.jpg'
                # }
            ]

            combos = [
                {
                    'name': 'Romance Combo',
                    'category': 'combo',
                    'price': 1999.00,
                    'description': 'A perfect romantic package featuring a red rose bouquet paired with a premium chocolate box, ideal for anniversaries and special dates.',
                    'image_url': '/static/images/products/romance-combo.jpg'
                },
                {
                    'name': 'Birthday Special',
                    'category': 'combo',
                    'price': 1499.00,
                    'description': 'A complete birthday celebration package with a beautiful flower bouquet and a delicious cake, making birthdays extra special.',
                    'image_url': '/static/images/products/birthday-combo.jpg'
                },
                {
                    'name': 'Sweet Celebration',
                    'category': 'combo',
                    'price': 1299.00,
                    'description': 'A delightful combination of a chocolate cake and a premium chocolate box, perfect for sweet celebrations.',
                    'image_url': '/static/images/products/sweet-celebration.jpg'
                },
                {
                    'name': 'Love & Sweetness',
                    'category': 'combo',
                    'price': 1799.00,
                    'description': 'A comprehensive gift package featuring a rose bouquet, premium chocolates, and a delicious cake, perfect for expressing love.',
                    'image_url': '/static/images/products/love-sweetness.jpg'
                },
                {
                    'name': 'Premium Gift Set',
                    'category': 'combo',
                    'price': 2499.00,
                    'description': 'Our most luxurious gift package combining premium flowers, an exquisite cake, and premium chocolates, perfect for grand celebrations.',
                    'image_url': '/static/images/products/premium-gift-set.jpg'
                }
            ]

            # Add all products to database
            all_products = bouquets + cakes + chocolates + combos
            for product_data in all_products:
                product = Product(**product_data)
                db.session.add(product)

            # Commit changes
            db.session.commit()
            print("Database initialized successfully")
            
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    init_db() 