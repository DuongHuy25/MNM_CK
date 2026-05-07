from django.core.management.base import BaseCommand
from dashboard.models import Product


class Command(BaseCommand):
    help = 'Cập nhật ảnh sản phẩm bị lỗi (Unsplash cũ) thành ảnh mặc định cục bộ'

    def add_arguments(self, parser):
        parser.add_argument(
            '--image',
            type=str,
            default='products/default.jpg',
            help='Đường dẫn file ảnh mặc định (mặc định: products/default.jpg)'
        )

    def handle(self, *args, **options):
        default_image = options['image']
        
        self.stdout.write(self.style.WARNING('🔍 Đang tìm sản phẩm cần fix...'))
        
        # Tìm sản phẩm có link Unsplash cũ
        bad_products = Product.objects.filter(image__icontains='unsplash')
        
        # Nếu không tìm thấy, kiểm tra link http external
        if bad_products.count() == 0:
            bad_products = Product.objects.filter(image__icontains='http')
        
        count = bad_products.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✨ Không có sản phẩm nào cần fix!'))
            return
        
        self.stdout.write(
            self.style.WARNING(f'\n🔍 Tìm thấy {count} sản phẩm cần cập nhật\n')
        )
        
        for product in bad_products:
            old_image = product.image.name
            product.image.name = default_image
            product.save()
            
            self.stdout.write(
                f'  ✏️  {product.name}\n'
                f'     {old_image} → {default_image}\n'
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Đã cập nhật thành công {count} sản phẩm!')
        )
