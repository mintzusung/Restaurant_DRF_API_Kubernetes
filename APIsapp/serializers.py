# from rest_framework import serializers
# from .models import *
# from django.contrib.auth.models import User

# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = '__all__'

# class MenuItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MenuItem
#         fields = '__all__'

# class CartSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Cart
#         fields = '__all__'

# class OrderItemSerializer(serializers.ModelSerializer)
#     class Meta:
#         model = OrderItem
#         fields = '__all__'

# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)

#     class Meta: 
#         model = Order
#         fields = '__all__'
#         read_only_fields = ['user', 'delivery_crew', 'status', 'total']

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id','username', 'email']


## new serializers.py
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'category', 'category_id']

class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        source='menuitem',
        write_only=True
    )

    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'menuitem_id', 'quantity']
        read_only_fields = ['user']   # user 自動帶入，不讓前端傳

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        source='menuitem',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'menuitem_id', 'quantity']
        read_only_fields = ['order']  # order 由系統生成，不允許手動指定


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)  # 只顯示 username
    delivery_crew = serializers.StringRelatedField(read_only=True)

    class Meta: 
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'items']
        read_only_fields = ['user', 'delivery_crew', 'status', 'total']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
