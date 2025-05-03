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
                    'price': 999.00,
                    'description': 'Beautiful bouquet of fresh red roses',
                    'image_url': '/static/images/Bouquets/redrose.webp'
                },
                {
                    'name': 'Mixed Flower Bouquet',
                    'category': 'bouquet',
                    'price': 1299.00,
                    'description': 'Colorful mix of fresh seasonal flowers',
                    'image_url': '/static/images/Bouquets/MixedFlower.webp'
                },
                {
                    'name': 'White Lily Bouquet',
                    'category': 'bouquet',
                    'price': 1499.00,
                    'description': 'Elegant white lilies with greenery',
                    'image_url': '/static/images/Bouquets/whitelilly.webp'
                },
                {
                    'name': 'Sunflower Bouquet',
                    'category': 'bouquet',
                    'price': 899.00,
                    'description': 'Bright and cheerful sunflower arrangement',
                    'image_url': '/static/images/Bouquets/Sunflower.webp'
                },
                {
                    'name': 'Orchid Bouquet',
                    'category': 'bouquet',
                    'price': 1999.00,
                    'description': 'Exotic orchid flowers in a beautiful arrangement',
                    'image_url': '/static/images/Bouquets/orchid.webp'
                },
                {
                    'name': 'Carnation Bouquet',
                    'category': 'bouquet',
                    'price': 799.00,
                    'description': 'Sweet and fragrant carnation bouquet',
                    'image_url': '/static/images/Bouquets/carnation.webp'
                },
                {
                    'name': 'Gerbera Bouquet',
                    'category': 'bouquet',
                    'price': 899.00,
                    'description': 'Colorful gerbera daisies in a cheerful arrangement',
                    'image_url': '/static/images/Bouquets/gerbera.webp'
                },
                {
                    'name': 'Tulip Bouquet',
                    'category': 'bouquet',
                    'price': 1299.00,
                    'description': 'Fresh tulips in a spring-inspired arrangement',
                    'image_url': '/static/images/Bouquets/tulip.webp'
                },
                {
                    'name': 'Daisy Bouquet',
                    'category': 'bouquet',
                    'price': 699.00,
                    'description': 'Simple and charming daisy bouquet',
                    'image_url': '/static/images/Bouquets/Daisy.webp'
                },
                {
                    'name': 'Rose and Lily Bouquet',
                    'category': 'bouquet',
                    'price': 1699.00,
                    'description': 'Luxurious combination of roses and lilies',
                    'image_url': '/static/images/Bouquets/roseandlilly.webp'
                }
            ]

            cakes_500g = [
                {
                    'name': 'Chocolate Truffle Cake',
                    'category': 'cake_500g',
                    'price': 499.00,
                    'description': 'Rich chocolate cake with truffle ganache',
                    'image_url': '/static/images/cakes/ctc.webpg'
                },
                {
                    'name': 'Vanilla Cream Cake',
                    'category': 'cake_500g',
                    'price': 399.00,
                    'description': 'Classic vanilla cake with fresh cream',
                    'image_url': '/static/images/products/vanilla-cream-cake.jpg'
                },
                {
                    'name': 'Red Velvet Cake',
                    'category': 'cake_500g',
                    'price': 449.00,
                    'description': 'Moist red velvet cake with cream cheese frosting',
                    'image_url': '/static/images/products/red-velvet-cake.jpg'
                },
                {
                    'name': 'Fruit Cake',
                    'category': 'cake_500g',
                    'price': 399.00,
                    'description': 'Fresh fruit topped cake with whipped cream',
                    'image_url': '/static/images/products/fruit-cake.jpg'
                },
                {
                    'name': 'Black Forest Cake',
                    'category': 'cake_500g',
                    'price': 499.00,
                    'description': 'Classic black forest with cherries and chocolate',
                    'image_url': '/static/images/products/black-forest-cake.jpg'
                }
            ]

            cakes_1kg = [
                {
                    'name': 'Chocolate Truffle Cake',
                    'category': 'cake_1kg',
                    'price': 899.00,
                    'description': 'Rich chocolate cake with truffle ganache',
                    'image_url': '/static/images/products/chocolate-truffle-cake-1kg.jpg'
                },
                {
                    'name': 'Vanilla Cream Cake',
                    'category': 'cake_1kg',
                    'price': 799.00,
                    'description': 'Classic vanilla cake with fresh cream',
                    'image_url': '/static/images/products/vanilla-cream-cake-1kg.jpg'
                },
                {
                    'name': 'Red Velvet Cake',
                    'category': 'cake_1kg',
                    'price': 849.00,
                    'description': 'Moist red velvet cake with cream cheese frosting',
                    'image_url': '/static/images/products/red-velvet-cake-1kg.jpg'
                },
                {
                    'name': 'Fruit Cake',
                    'category': 'cake_1kg',
                    'price': 799.00,
                    'description': 'Fresh fruit topped cake with whipped cream',
                    'image_url': '/static/images/products/fruit-cake-1kg.jpg'
                },
                {
                    'name': 'Black Forest Cake',
                    'category': 'cake_1kg',
                    'price': 899.00,
                    'description': 'Classic black forest with cherries and chocolate',
                    'image_url': '/static/images/products/black-forest-cake-1kg.jpg'
                }
            ]

            chocolates = [
                {
                    'name': 'Dark Chocolate Box',
                    'category': 'chocolate',
                    'price': 299.00,
                    'description': 'Assorted dark chocolates in a gift box',
                    'image_url': '/static/images/products/dark-chocolate-box.jpg'
                },
                {
                    'name': 'Milk Chocolate Box',
                    'category': 'chocolate',
                    'price': 299.00,
                    'description': 'Assorted milk chocolates in a gift box',
                    'image_url': '/static/images/products/milk-chocolate-box.jpg'
                },
                {
                    'name': 'White Chocolate Box',
                    'category': 'chocolate',
                    'price': 299.00,
                    'description': 'Assorted white chocolates in a gift box',
                    'image_url': '/static/images/products/white-chocolate-box.jpg'
                },
                {
                    'name': 'Chocolate Truffles',
                    'category': 'chocolate',
                    'price': 399.00,
                    'description': 'Handcrafted chocolate truffles',
                    'image_url': '/static/images/products/chocolate-truffles.jpg'
                },
                {
                    'name': 'Chocolate Assortment',
                    'category': 'chocolate',
                    'price': 499.00,
                    'description': 'Premium chocolate assortment box',
                    'image_url': '/static/images/products/chocolate-assortment.jpg'
                },
                {
                    'name': 'Chocolate Hearts',
                    'category': 'chocolate',
                    'price': 199.00,
                    'description': 'Romantic chocolate hearts box',
                    'image_url': '/static/images/products/chocolate-hearts.jpg'
                },
                {
                    'name': 'Chocolate Bars Set',
                    'category': 'chocolate',
                    'price': 349.00,
                    'description': 'Set of premium chocolate bars',
                    'image_url': '/static/images/products/chocolate-bars.jpg'
                },
                {
                    'name': 'Chocolate Pralines',
                    'category': 'chocolate',
                    'price': 449.00,
                    'description': 'Luxury chocolate pralines box',
                    'image_url': '/static/images/products/chocolate-pralines.jpg'
                },
                {
                    'name': 'Chocolate Gift Hamper',
                    'category': 'chocolate',
                    'price': 599.00,
                    'description': 'Deluxe chocolate gift hamper',
                    'image_url': '/static/images/products/chocolate-hamper.jpg'
                },
                {
                    'name': 'Chocolate Dipped Fruits',
                    'category': 'chocolate',
                    'price': 399.00,
                    'description': 'Chocolate dipped fruits assortment',
                    'image_url': '/static/images/products/chocolate-fruits.jpg'
                }
            ]

            combos = [
                {
                    'name': 'Romance Combo',
                    'category': 'combo',
                    'price': 1999.00,
                    'description': 'Red roses bouquet with chocolate box',
                    'image_url': '/static/images/products/romance-combo.jpg'
                },
                {
                    'name': 'Birthday Special',
                    'category': 'combo',
                    'price': 1499.00,
                    'description': 'Cake with balloon bouquet',
                    'image_url': '/static/images/products/birthday-combo.jpg'
                },
                {
                    'name': 'Sweet Celebration',
                    'category': 'combo',
                    'price': 1299.00,
                    'description': 'Cake with chocolate box',
                    'image_url': '/static/images/products/sweet-celebration.jpg'
                },
                {
                    'name': 'Love & Sweetness',
                    'category': 'combo',
                    'price': 1799.00,
                    'description': 'Flowers with chocolates and cake',
                    'image_url': '/static/images/products/love-sweetness.jpg'
                },
                {
                    'name': 'Premium Gift Set',
                    'category': 'combo',
                    'price': 2499.00,
                    'description': 'Luxury combo of flowers, cake, and chocolates',
                    'image_url': '/static/images/products/premium-gift-set.jpg'
                }
            ]

            # Add all products to database
            all_products = bouquets + cakes_500g + cakes_1kg + chocolates + combos
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