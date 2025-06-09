from app import app, mongo_client, users_collection, products_collection
from werkzeug.security import generate_password_hash

def init_db():
    try:
        # Get database
        db = mongo_client['esadabahar']
        
        # Drop existing collections
        db.users.drop()
        db.products.drop()
        
        # Check if admin user exists
        admin = users_collection.find_one({'username': 'admin'})
        if not admin:
            # Create admin user
            admin_user = {
                'username': 'admin',
                'password_hash': generate_password_hash('admin123'),
                'is_admin': True
            }
            users_collection.insert_one(admin_user)
            print("Admin user created successfully")
        else:
            print("Admin user already exists")
        
        # Sample products
        bouquets = [
            {
                'name': 'Red Rose Bouquet',
                'category': 'bouquet',
                'price': 499.00,
                'description': 'A stunning arrangement of 10 premium red roses, perfect for expressing love and romance.',
                'image_url': '/static/images/Bouquets/redrose.webp',
                'stock': 10
            },
            {
                'name': 'Mixed Flower Bouquet',
                'category': 'bouquet',
                'price': 759.00,
                'description': 'A vibrant mix of 12 flowers including roses, carnations, and gerberas, creating a colorful celebration of beauty.',
                'image_url': '/static/images/Bouquets/MixedFlower.webp',
                'stock': 10
            },
            {
                'name': 'White Lily Bouquet',
                'category': 'bouquet',
                'price': 1499.00,
                'description': 'An elegant arrangement of 5 pristine white lilies with complementary greenery, symbolizing purity and majesty.',
                'image_url': '/static/images/Bouquets/whitelilly.webp',
                'stock': 10
            },
            {
                'name': 'Orchid Bouquet',
                'category': 'bouquet',
                'price': 1299.00,
                'description': 'A sophisticated arrangement of 10 exotic orchids, perfect for special occasions and elegant celebrations.',
                'image_url': '/static/images/Bouquets/orchid.webp',
                'stock': 10
            },
            {
                'name': 'Carnation Bouquet',
                'category': 'bouquet',
                'price': 799.00,
                'description': 'A delightful bouquet of 12 sweet-smelling carnations, available in various colors to match your mood.',
                'image_url': '/static/images/Bouquets/carnation.webp',
                'stock': 10
            },
            {
                'name': 'Gerbera Bouquet',
                'category': 'bouquet',
                'price': 599.00,
                'description': 'A cheerful arrangement of 15 vibrant gerbera daisies, bringing joy and brightness to any occasion.',
                'image_url': '/static/images/Bouquets/gerbera.webp',
                'stock': 10
            },
            {
                'name': 'Rose and Lily Bouquet',
                'category': 'bouquet',
                'price': 1299.00,
                'description': 'A luxurious combination of premium roses and lilies, creating a perfect blend of romance and elegance.',
                'image_url': '/static/images/Bouquets/roseandlilly.webp',
                'stock': 10
            }
        ]

        cakes = [
            {
                'name': 'Chocolate Truffle Cake',
                'category': 'cake_500g',
                'price': 599.00,
                'description': 'Chocolate Truffle Cake..',
                'image_url': '/static/images/cakes/ctc.webpg',
                'stock': 10
            },
            {
                'name': 'Vanilla Cream Cake',
                'category': 'cake_500g',
                'price': 499.00,
                'description': 'Vanilla Cream Cake.',
                'image_url': '/static/images/products/vanilla-cream-cake.jpg',
                'stock': 10
            },
            {
                'name': 'Red Velvet Cake',
                'category': 'cake_500g',
                'price': 449.00,
                'description': 'Red Velvet Cake.',
                'image_url': '/static/images/products/red-velvet-cake.jpg',
                'stock': 10
            },
            {
                'name': 'Fruit Cake',
                'category': 'cake_500g',
                'price': 499.00,
                'description': 'Fruit Cake.',
                'image_url': '/static/images/products/fruit-cake.jpg',
                'stock': 10
            },
            {
                'name': 'Black Forest Cake',
                'category': 'cake_500g',
                'price': 599.00,
                'description': 'Black Forest Cake.',
                'image_url': '/static/images/products/black-forest-cake.jpg',
                'stock': 10
            }
        ]

        chocolates = [
            {
                'name': 'Ferrero Rocher Chocolate Gift Pack (4 Pieces)',
                'category': 'chocolate',
                'price': 189.00,
                'description': 'A premium gift pack containing 4 Ferrero Rocher chocolates, each featuring a whole hazelnut surrounded by chocolate and crispy wafer.',
                'image_url': '/static/images/products/dark-chocolate-box.jpg',
                'stock': 10
            },
            {
                'name': 'Ferrero Rocher Chocolate Gift Pack (16 Pieces)',
                'category': 'chocolate',
                'price': 629.00,
                'description': 'A deluxe gift pack with 16 Ferrero Rocher chocolates, perfect for sharing with family and friends on special occasions.',
                'image_url': '/static/images/products/milk-chocolate-box.jpg',
                'stock': 10
            },
            {
                'name': 'Ferrero Rocher Chocolate Gift Pack (24 Pieces)',
                'category': 'chocolate',
                'price': 979.00,
                'description': 'A grand gift pack featuring 24 Ferrero Rocher chocolates, ideal for corporate gifting or large family celebrations.',
                'image_url': '/static/images/products/white-chocolate-box.jpg',
                'stock': 10
            },
            {
                'name': 'Amul Chocominis chocolate Gift Pack',
                'category': 'chocolate',
                'price': 140.00,
                'description': 'A delightful assortment of Amul Chocominis.',
                'image_url': '/static/images/products/chocolate-truffles.jpg',
                'stock': 10
            },
            {
                'name': 'Cadbury celebrations Assorted Chocolate Gift Pack',
                'category': 'chocolate',
                'price': 499.00,
                'description': 'A premium assortment of Cadbury chocolates including Dairy Milk, 5 Star, Gems, and other popular variants.',
                'image_url': '/static/images/products/chocolate-assortment.jpg',
                'stock': 10
            }
        ]

        combos = [
            {
                'name': 'Romance Combo',
                'category': 'combo',
                'price': 1999.00,
                'description': 'A perfect romantic package featuring a red rose bouquet paired with a premium chocolate box, ideal for anniversaries and special dates.',
                'image_url': '/static/images/products/romance-combo.jpg',
                'stock': 10
            },
            {
                'name': 'Birthday Special',
                'category': 'combo',
                'price': 1499.00,
                'description': 'A complete birthday celebration package with a beautiful flower bouquet and a delicious cake, making birthdays extra special.',
                'image_url': '/static/images/products/birthday-combo.jpg',
                'stock': 10
            },
            {
                'name': 'Sweet Celebration',
                'category': 'combo',
                'price': 1299.00,
                'description': 'A delightful combination of a chocolate cake and a premium chocolate box, perfect for sweet celebrations.',
                'image_url': '/static/images/products/sweet-celebration.jpg',
                'stock': 10
            },
            {
                'name': 'Love & Sweetness',
                'category': 'combo',
                'price': 1799.00,
                'description': 'A comprehensive gift package featuring a rose bouquet, premium chocolates, and a delicious cake, perfect for expressing love.',
                'image_url': '/static/images/products/love-sweetness.jpg',
                'stock': 10
            },
            {
                'name': 'Premium Gift Set',
                'category': 'combo',
                'price': 2499.00,
                'description': 'Our most luxurious gift package combining premium flowers, an exquisite cake, and premium chocolates, perfect for grand celebrations.',
                'image_url': '/static/images/products/premium-gift-set.jpg',
                'stock': 10
            }
        ]

        # Add all products to database
        all_products = bouquets + cakes + chocolates + combos
        if all_products:
            products_collection.insert_many(all_products)
            print("Products added successfully")
        
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == '__main__':
    init_db() 