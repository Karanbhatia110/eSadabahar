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
        admin = users_collection.find_one({'username': 'esadabahar'})
        if not admin:
            # Create admin user
            admin_user = {
                'username': 'esadabahar',
                'password_hash': generate_password_hash('9780444970', method='pbkdf2:sha256'),
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
                'image_url': 'https://imgs.search.brave.com/SxnUBb53DVX_aqEdkjMHqnMZdQrrH4idaHf3_MesXZ0/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9mbG93/ZXJhdXJhLWJsb2ct/aW1nLnMzLmFwLXNv/dXRoLTEuYW1hem9u/YXdzLmNvbS9jaG9j/b2xhdGUrdHJ1ZmZs/ZStjYWtlK2Rlc2ln/bi9DaG9jb2xhdGUt/VHJ1ZmZsZS1DYWtl/LmpwZw',
                'stock': 10
            },
            {
                'name': 'Vanilla Cream Cake',
                'category': 'cake_500g',
                'price': 499.00,
                'description': 'Vanilla Cream Cake.',
                'image_url': 'https://imgs.search.brave.com/BDCZww8G6XDJRBdX0IiOL3TzagOkABXVg3tZrNsDkAk/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly93d3cu/Z2lmdGFjcm9zc2lu/ZGlhLmNvbS9tZWRp/YS9jYXRhbG9nL3Rp/bWFnZXMvOGI2Y2Vl/NGIzZmU1YmQxMjJh/ZTliYjA5ODI4ZmFm/NjYuanBn',
                'stock': 10
            },
            {
                'name': 'Red Velvet Cake',
                'category': 'cake_500g',
                'price': 449.00,
                'description': 'Red Velvet Cake.',
                'image_url': 'https://imgs.search.brave.com/r-seiKTcQvpdYdR6WjlZvcfvyxbBDfGHxMzoXHb5IU4/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9ia21l/ZGlhLmJha2luZ28u/Y29tL3NxLXJlZC12/ZWx2ZXQtY2FrZS1j/YWtlMTYzMXJlZHYt/QV8wLmpwZw',
                'stock': 10
            },
            {
                'name': 'Fruit Cake',
                'category': 'cake_500g',
                'price': 499.00,
                'description': 'Fruit Cake.',
                'image_url': 'https://imgs.search.brave.com/pfb7KfrwJjEFMb07hcQl4f9tq07TpxEOR_-9IXQ23Qs/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9kM2Np/ZjJodTk1czg4di5j/bG91ZGZyb250Lm5l/dC9saXZlLXNpdGUt/MjAxNi9wcm9kdWN0/LWltYWdlLzIwMjMv/MTY5NDcwOTAwNDIt/MzUweDM1MC5qcGc',
                'stock': 10
            },
            {
                'name': 'Black Forest Cake',
                'category': 'cake_500g',
                'price': 599.00,
                'description': 'Black Forest Cake.',
                'image_url': 'https://imgs.search.brave.com/EDxF7EHiguqSh9h6AGHMzT2ue95ioNuifBoSiooOJVI/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly93d3cu/dGhlZmxvd2Vyc3Bv/aW50LmNvbS9kYXRh/L2NhY2hlL2ltYWdl/cy9jYWtlcy9jYWtl/JTIwYnklMjBmbGF2/b3VyL2JsYWNrJTIw/Zm9yZXN0JTIwY2Fr/ZS9IZWF2eV9ibGFj/a19mb3Jlc3QtMzI4/eDMyOC5wbmc',
                'stock': 10
            }
        ]

        chocolates = [
            {
                'name': 'Ferrero Rocher Chocolate Gift Pack (4 Pieces)',
                'category': 'chocolate',
                'price': 189.00,
                'description': 'A premium gift pack containing 4 Ferrero Rocher chocolates, each featuring a whole hazelnut surrounded by chocolate and crispy wafer.',
                'image_url': 'https://imgs.search.brave.com/v-4KLYTcfjxvDcEiMnR9MoPW_VBiahx7oprF2AIg9sk/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9jZG4u/Z3JvZmVycy5jb20v/Y2RuLWNnaS9pbWFn/ZS9mPWF1dG8sZml0/PXNjYWxlLWRvd24s/cT04NSxtZXRhZGF0/YT1ub25lLHc9NDgw/LGg9NDgwL2RhL2Nt/cy1hc3NldHMvY21z/L3Byb2R1Y3QvMjhh/NDdmY2YtMTMwMS00/Y2QyLWE2NWYtOWUy/ZjQwMmQ5ZDEzLmpw/Zz90cz0xNzI5MjUy/Mzkx',
                'stock': 10
            },
            {
                'name': 'Ferrero Rocher Chocolate Gift Pack (16 Pieces)',
                'category': 'chocolate',
                'price': 629.00,
                'description': 'A deluxe gift pack with 16 Ferrero Rocher chocolates, perfect for sharing with family and friends on special occasions.',
                'image_url': 'https://imgs.search.brave.com/PQP3MxCuXew-P0Ec24EbWPrF9ogy0plTUopPXVOIXNQ/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly93d3cu/dGhld2FyZWhvdXNl/LmNvLm56L2R3L2lt/YWdlL3YyL0JETUdf/UFJEL29uL2RlbWFu/ZHdhcmUuc3RhdGlj/Ly0vU2l0ZXMtdHds/LW1hc3Rlci1jYXRh/bG9nL2RlZmF1bHQv/ZHc0NzQ2YjhmMi9p/bWFnZXMvaGktcmVz/LzY1LzhBL1IzMzU4/NjNfMzAuanBnP3N3/PTc2NSZzaD03NjU',
                'stock': 10
            },
            {
                'name': 'Ferrero Rocher Chocolate Gift Pack (24 Pieces)',
                'category': 'chocolate',
                'price': 979.00,
                'description': 'A grand gift pack featuring 24 Ferrero Rocher chocolates, ideal for corporate gifting or large family celebrations.',
                'image_url': 'https://imgs.search.brave.com/9y-QMICjX1Wr0NfYJ3O2PDYf2PN6bNaOG2On03VmhsQ/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tLm1l/ZGlhLWFtYXpvbi5j/b20vaW1hZ2VzL0kv/NzEtcmJHdGFGa0wu/anBn',
                'stock': 10
            },
            {
                'name': 'Amul Chocominis chocolate Gift Pack',
                'category': 'chocolate',
                'price': 140.00,
                'description': 'A delightful assortment of Amul Chocominis.',
                'image_url': 'https://imgs.search.brave.com/k0q9elRxW8-sWcpbyFxdyu5CSxJ-SuLR8IO1qXNCFls/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9jZG4u/Z3JvZmVycy5jb20v/Y2RuLWNnaS9pbWFn/ZS9mPWF1dG8sZml0/PXNjYWxlLWRvd24s/cT04NSxtZXRhZGF0/YT1ub25lLHc9NDgw/LGg9NDgwL2FwcC9p/bWFnZXMvcHJvZHVj/dHMvc2xpZGluZ19p/bWFnZS8yMzc1MmEu/anBnP3RzPTE3MjI4/NDA4OTM',
                'stock': 10
            },
            {
                'name': 'Cadbury celebrations Assorted Chocolate Gift Pack',
                'category': 'chocolate',
                'price': 499.00,
                'description': 'A premium assortment of Cadbury chocolates including Dairy Milk, 5 Star, Gems, and other popular variants.',
                'image_url': 'https://imgs.search.brave.com/JIQ19hlhgGoSbOr85MTCrTic-HFOmEByJlR6hb8LUho/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9jZG4u/Z3JvZmVycy5jb20v/Y2RuLWNnaS9pbWFn/ZS9mPWF1dG8sZml0/PXNjYWxlLWRvd24s/cT04NSxtZXRhZGF0/YT1ub25lLHc9NDgw/LGg9NDgwL2RhL2Nt/cy1hc3NldHMvY21z/L3Byb2R1Y3QvODI1/MmM2MzQtMWQ5Zi00/Mzg5LTkwNmEtMWEy/Mzg2M2Y1MjgzLmpw/Zz90cz0xNzI5MDY5/MDUz',
                'stock': 10
            }
        ]

        combos = [
            # {
            #     'name': 'Romance Combo',
            #     'category': 'combo',
            #     'price': 1999.00,
            #     'description': 'A perfect romantic package featuring a red rose bouquet paired with a premium chocolate box, ideal for anniversaries and special dates.',
            #     'image_url': 'https://sdmntpreastus2.oaiusercontent.com/files/00000000-4cdc-61f6-bf7b-d66cefeb4df7/raw?se=2025-06-26T12%3A48%3A48Z&sp=r&sv=2024-08-04&sr=b&scid=a62cf746-9d54-5007-a11c-9d258b3ab36d&skoid=b0fd38cc-3d33-418f-920e-4798de4acdd1&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-06-26T10%3A47%3A11Z&ske=2025-06-27T10%3A47%3A11Z&sks=b&skv=2024-08-04&sig=5cA71SykmnJgehfA6U8mAt5YJmeLBjlMzetS3pi1THY%3D',
            #     'stock': 10
            # },
            {
                'name': 'Birthday Special',
                'category': 'combo',
                'price': 1499.00,
                'description': 'A complete birthday celebration package with a beautiful flower bouquet and a delicious cake, making birthdays extra special.',
                'image_url': 'https://imgs.search.brave.com/eHDLXIMLHzdJRjQv9XcaES0a7aj_j_rzuIiZEDESj6M/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pbWdj/ZG4uZmxvd2VyYXVy/YS5jb20va2l0a2F0/LWNha2Utd2l0aC1y/b3Nlcy1ib3VxdWV0/LTk4MDc4OTBjby1B/XzAuanBn',
                'stock': 10
            },
            # {
            #     'name': 'Sweet Celebration',
            #     'category': 'combo',
            #     'price': 1299.00,
            #     'description': 'A delightful combination of a chocolate cake and a premium chocolate box, perfect for sweet celebrations.',
            #     'image_url': '\static\images\combos\sweet_celebration.png',
            #     'stock': 10
            # },
            # {
            #     'name': 'Love & Sweetness',
            #     'category': 'combo',
            #     'price': 1799.00,
            #     'description': 'A comprehensive gift package featuring a rose bouquet, premium chocolates, and a delicious cake, perfect for expressing love.',
            #     'image_url': '/static/images/products/love-sweetness.jpg',
            #     'stock': 10
            # },
            # {
            #     'name': 'Premium Gift Set',
            #     'category': 'combo',
            #     'price': 2499.00,
            #     'description': 'Our most luxurious gift package combining premium flowers, an exquisite cake, and premium chocolates, perfect for grand celebrations.',
            #     'image_url': '/static/images/products/premium-gift-set.jpg',
            #     'stock': 10
            # }
        ]

        Plants = [
            {
                'name': 'Lucky Bamboo',
                'category': 'plant',
                'price': 499.00,
                'description': 'A beautiful Lucky Bamboo plant, perfect for your home or office.',
                'image_url': '/static/images/plants/lucky-bamboo.jpg',
                'stock': 10
            }
        ]

        # Add all products to database
        all_products = bouquets + cakes + chocolates + combos + Plants
        if all_products:
            products_collection.insert_many(all_products)
            print("Products added successfully")
        
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == '__main__':
    init_db() 
