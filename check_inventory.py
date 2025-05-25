#!/usr/bin/env python3
from app import app, db
from models import ProductInventory

with app.app_context():
    total = ProductInventory.query.count()
    print(f'📊 Total products in inventory: {total}')
    
    print('\n🔥 Latest trending products in your inventory:')
    products = ProductInventory.query.order_by(ProductInventory.created_at.desc()).limit(10).all()
    for i, p in enumerate(products, 1):
        print(f'{i}. {p.product_title[:60]}... (${p.price}) - ASIN: {p.asin}')
        
    print('\n💎 Most popular categories:')
    categories = db.session.query(ProductInventory.category, db.func.count(ProductInventory.id)).group_by(ProductInventory.category).all()
    for cat, count in categories:
        print(f'- {cat}: {count} products')