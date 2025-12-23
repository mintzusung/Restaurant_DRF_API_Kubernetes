from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User, Group
from .models import *
from .serializers import *
from .permissions import *
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = MenuItem.objects.all()
        category = self.request.query_params.get('category')
        sort = self.request.query_params.get('sort')
        if category:
            queryset = queryset.filter(category__id=category) 
        if sort == 'price':
            queryset = queryset.order_by('price')
        return queryset
    
class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({'status': 'cart cleared'})

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        """依使用者角色回傳不同範圍的訂單"""
        user = self.request.user

        if user.groups.filter(name='Manager').exists() or user.is_staff:
            # Manager 或 Admin 可以看到所有訂單
            return Order.objects.all()
        elif user.groups.filter(name='Delivery crew').exists():
            # 配送員只能看到被指派給自己的訂單
            return Order.objects.filter(delivery_crew=user)
        else:
            # 一般使用者只看到自己建立的訂單
            return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        """建立訂單時自動綁定使用者"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        """從購物車自動生成訂單"""
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=400)

        # 建立新訂單
        order = Order.objects.create(user=user)
        total = 0

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity
            )
            total += item.menuitem.price * item.quantity

        order.total = total
        order.save()
        cart_items.delete()

        serializer = OrderSerializer(order)
        return Response({'status': 'order created', 'order': serializer.data}, status=201)

    @action(detail=True, methods=['post'], permission_classes=[IsManager])
    def assign_order(self, request, pk=None):
        """由 Manager 指派訂單給配送員"""
        order = self.get_object()
        delivery_user_id = request.data.get('delivery_crew_id')

        if not delivery_user_id:
            return Response({'error': 'delivery_crew_id is required'}, status=400)

        try:
            delivery_user = User.objects.get(pk=delivery_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        if order.delivery_crew:
            return Response({'error': 'Order already assigned'}, status=400)

        if not delivery_user.groups.filter(name='Delivery crew').exists():
            return Response({'error': 'User is not in Delivery crew group'}, status=400)

        if delivery_user == request.user:
            return Response({'error': 'Manager cannot assign order to self'}, status=400)

        order.delivery_crew = delivery_user
        order.save()

        serializer = OrderSerializer(order)
        return Response({
            'status': 'order assigned',
            'order': serializer.data
        }, status=202)

    @action(detail=True, methods=['patch','post'], permission_classes=[IsDeliveryCrew])
    def mark_delivered(self, request, pk=None):
        """配送員標記訂單已送達"""
        order = self.get_object()

        if order.status:
            return Response({'warning': 'Order already delivered'}, status=400)

        order.status = True
        order.save()
        return Response({'status': 'Order marked as delivered'}, status=200)
    
class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        if not request.user.groups.filter(name__in=['Admin', 'Manager']).exists():
            return Response({'detail': 'Not authorized'}, status=403)

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def set_manager(self, request, pk=None):
        user = User.objects.get(pk=pk)
        group = Group.objects.get(name='Manager')
        user.groups.add(group)
        return Response({'status': 'manager added'})
 
    @action(detail=True, methods=['post'], permission_classes=[IsManager])
    def set_delivery(self, request, pk=None):
        user = User.objects.get(pk=pk)
        group = Group.objects.get(name='Delivery crew')
        user.groups.add(group)
        return Response({'status': 'delivery crew added'})

    @action(detail=True, methods=['post'], permission_classes=[IsManager]) 
    def assign_order(self, request, pk=None):
        order_id = request.data.get('order_id')
        order = Order.objects.get(id=order_id)
        user = User.objects.get(pk=pk)
        order.delivery_crew = user
        order.save()
        return Response({'status': 'order assigned'})
    

    

    
    