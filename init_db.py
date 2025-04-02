from app import app, db, Product, User
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Clear existing products
        Product.query.delete()
        
        # Sample products
        bouquets = [
            {
                'name': 'Red Rose Bouquet',
                'category': 'bouquet',
                'price': 999.00,
                'description': 'Beautiful bouquet of fresh red roses',
                'image_url': '/static/images/products/red-rose-bouquet.jpg',
                'stock': 10
            },
            {
                'name': 'Mixed Flower Bouquet',
                'category': 'bouquet',
                'price': 1299.00,
                'description': 'Colorful mix of fresh seasonal flowers',
                'image_url': '/static/images/products/mixed-flower-bouquet.jpg',
                'stock': 15
            },
            {
                'name': 'White Lily Bouquet',
                'category': 'bouquet',
                'price': 1499.00,
                'description': 'Elegant white lilies with greenery',
                'image_url': '/static/images/products/white-lily-bouquet.jpg',
                'stock': 8
            },
            {
                'name': 'Sunflower Bouquet',
                'category': 'bouquet',
                'price': 899.00,
                'description': 'Bright and cheerful sunflower arrangement',
                'image_url': '/static/images/products/sunflower-bouquet.jpg',
                'stock': 12
            },
            {
                'name': 'Orchid Bouquet',
                'category': 'bouquet',
                'price': 1999.00,
                'description': 'Exotic orchid flowers in a beautiful arrangement',
                'image_url': '/static/images/products/orchid-bouquet.jpg',
                'stock': 5
            },
            {
                'name': 'Carnation Bouquet',
                'category': 'bouquet',
                'price': 799.00,
                'description': 'Sweet and fragrant carnation bouquet',
                'image_url': '/static/images/products/carnation-bouquet.jpg',
                'stock': 20
            },
            {
                'name': 'Gerbera Bouquet',
                'category': 'bouquet',
                'price': 899.00,
                'description': 'Colorful gerbera daisies in a cheerful arrangement',
                'image_url': '/static/images/products/gerbera-bouquet.jpg',
                'stock': 15
            },
            {
                'name': 'Tulip Bouquet',
                'category': 'bouquet',
                'price': 1299.00,
                'description': 'Fresh tulips in a spring-inspired arrangement',
                'image_url': '/static/images/products/tulip-bouquet.jpg',
                'stock': 10
            },
            {
                'name': 'Daisy Bouquet',
                'category': 'bouquet',
                'price': 699.00,
                'description': 'Simple and charming daisy bouquet',
                'image_url': '/static/images/products/daisy-bouquet.jpg',
                'stock': 25
            },
            {
                'name': 'Rose and Lily Bouquet',
                'category': 'bouquet',
                'price': 1699.00,
                'description': 'Luxurious combination of roses and lilies',
                'image_url': '/static/images/products/rose-lily-bouquet.jpg',
                'stock': 8
            }
        ]

        cakes_500g = [
            {
                'name': 'Chocolate Truffle Cake',
                'category': 'cake_500g',
                'price': 499.00,
                'description': 'Rich chocolate cake with truffle ganache',
                'image_url': '/static/images/products/chocolate-truffle-cake.jpg',
                'stock': 10
            },
            {
                'name': 'Vanilla Cream Cake',
                'category': 'cake_500g',
                'price': 399.00,
                'description': 'Classic vanilla cake with fresh cream',
                'image_url': '/static/images/products/vanilla-cream-cake.jpg',
                'stock': 15
            },
            {
                'name': 'Red Velvet Cake',
                'category': 'cake_500g',
                'price': 449.00,
                'description': 'Moist red velvet cake with cream cheese frosting',
                'image_url': '/static/images/products/red-velvet-cake.jpg',
                'stock': 12
            },
            {
                'name': 'Fruit Cake',
                'category': 'cake_500g',
                'price': 399.00,
                'description': 'Fresh fruit topped cake with whipped cream',
                'image_url': '/static/images/products/fruit-cake.jpg',
                'stock': 8
            },
            {
                'name': 'Black Forest Cake',
                'category': 'cake_500g',
                'price': 499.00,
                'description': 'Classic black forest with cherries and chocolate',
                'image_url': '/static/images/products/black-forest-cake.jpg',
                'stock': 10
            }
        ]

        cakes_1kg = [
            {
                'name': 'Chocolate Truffle Cake',
                'category': 'cake_1kg',
                'price': 899.00,
                'description': 'Rich chocolate cake with truffle ganache',
                'image_url': '/static/images/products/chocolate-truffle-cake-1kg.jpg',
                'stock': 8
            },
            {
                'name': 'Vanilla Cream Cake',
                'category': 'cake_1kg',
                'price': 799.00,
                'description': 'Classic vanilla cake with fresh cream',
                'image_url': '/static/images/products/vanilla-cream-cake-1kg.jpg',
                'stock': 12
            },
            {
                'name': 'Red Velvet Cake',
                'category': 'cake_1kg',
                'price': 849.00,
                'description': 'Moist red velvet cake with cream cheese frosting',
                'image_url': '/static/images/products/red-velvet-cake-1kg.jpg',
                'stock': 10
            },
            {
                'name': 'Fruit Cake',
                'category': 'cake_1kg',
                'price': 799.00,
                'description': 'Fresh fruit topped cake with whipped cream',
                'image_url': '/static/images/products/fruit-cake-1kg.jpg',
                'stock': 6
            },
            {
                'name': 'Black Forest Cake',
                'category': 'cake_1kg',
                'price': 899.00,
                'description': 'Classic black forest with cherries and chocolate',
                'image_url': '/static/images/products/black-forest-cake-1kg.jpg',
                'stock': 8
            }
        ]

        chocolates = [
            {
                'name': 'Dark Chocolate Box',
                'category': 'chocolate',
                'price': 299.00,
                'description': 'Assorted dark chocolates in a gift box',
                'image_url': '/static/images/products/dark-chocolate-box.jpg',
                'stock': 20
            },
            {
                'name': 'Milk Chocolate Box',
                'category': 'chocolate',
                'price': 299.00,
                'description': 'Assorted milk chocolates in a gift box',
                'image_url': '/static/images/products/milk-chocolate-box.jpg',
                'stock': 25
            },
            {
                'name': 'White Chocolate Box',
                'category': 'chocolate',
                'price': 299.00,
                'description': 'Assorted white chocolates in a gift box',
                'image_url': '/static/images/products/white-chocolate-box.jpg',
                'stock': 15
            },
            {
                'name': 'Chocolate Truffles',
                'category': 'chocolate',
                'price': 399.00,
                'description': 'Handcrafted chocolate truffles',
                'image_url': '/static/images/products/chocolate-truffles.jpg',
                'stock': 18
            },
            {
                'name': 'Chocolate Assortment',
                'category': 'chocolate',
                'price': 499.00,
                'description': 'Premium chocolate assortment box',
                'image_url': '/static/images/products/chocolate-assortment.jpg',
                'stock': 12
            },
            {
                'name': 'Chocolate Hearts',
                'category': 'chocolate',
                'price': 199.00,
                'description': 'Romantic chocolate hearts box',
                'image_url': '/static/images/products/chocolate-hearts.jpg',
                'stock': 30
            },
            {
                'name': 'Chocolate Bars Set',
                'category': 'chocolate',
                'price': 349.00,
                'description': 'Set of premium chocolate bars',
                'image_url': '/static/images/products/chocolate-bars.jpg',
                'stock': 15
            },
            {
                'name': 'Chocolate Pralines',
                'category': 'chocolate',
                'price': 449.00,
                'description': 'Luxury chocolate pralines box',
                'image_url': '/static/images/products/chocolate-pralines.jpg',
                'stock': 10
            },
            {
                'name': 'Chocolate Gift Hamper',
                'category': 'chocolate',
                'price': 599.00,
                'description': 'Deluxe chocolate gift hamper',
                'image_url': '/static/images/products/chocolate-hamper.jpg',
                'stock': 8
            },
            {
                'name': 'Chocolate Dipped Fruits',
                'category': 'chocolate',
                'price': 399.00,
                'description': 'Chocolate dipped fruits assortment',
                'image_url': '/static/images/products/chocolate-fruits.jpg',
                'stock': 12
            }
        ]

        combos = [
            {
                'name': 'Romance Combo',
                'category': 'combo',
                'price': 1999.00,
                'description': 'Red roses bouquet with chocolate box',
                'image_url': '/static/images/products/romance-combo.jpg',
                'stock': 5
            },
            {
                'name': 'Birthday Special',
                'category': 'combo',
                'price': 1499.00,
                'description': 'Cake with balloon bouquet',
                'image_url': '/static/images/products/birthday-combo.jpg',
                'stock': 8
            },
            {
                'name': 'Sweet Celebration',
                'category': 'combo',
                'price': 1299.00,
                'description': 'Cake with chocolate box',
                'image_url': '/static/images/products/sweet-celebration.jpg',
                'stock': 10
            },
            {
                'name': 'Love & Sweetness',
                'category': 'combo',
                'price': 1799.00,
                'description': 'Flowers with chocolates and cake',
                'image_url': '/static/images/products/love-sweetness.jpg',
                'stock': 6
            },
            {
                'name': 'Premium Gift Set',
                'category': 'combo',
                'price': 2499.00,
                'description': 'Luxury combo of flowers, cake, and chocolates',
                'image_url': '/static/images/products/premium-gift-set.jpg',
                'stock': 4
            }
        ]

        # Add all products to database
        all_products = bouquets + cakes_500g + cakes_1kg + chocolates + combos
        for product_data in all_products:
            product = Product(**product_data)
            db.session.add(product)

        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password='admin123',  # In production, use proper password hashing
                is_admin=True
            )
            db.session.add(admin)

        # Commit all changes
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db() 