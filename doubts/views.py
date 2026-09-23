from django.db.models import Count, Q, F
from django.utils import timezone
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.permissions import IsStudent, IsClassParticipant
from .models import Doubt, DoubtLike, DoubtMessageLike, DoubtMessage
from .serializers import DoubtCreateSerializer, DoubtListSerializer, DoubtDetailSerializer, DoubtMessageSerializer
from django.db.models import Prefetch

class DoubtViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):

    def get_serializer_class(self):
        if self.action == 'create':
            return DoubtCreateSerializer
        if self.action == 'list':
            return DoubtListSerializer
        return DoubtDetailSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsStudent()]
        return [IsClassParticipant()]

    def get_queryset(self):
        user = self.request.user
        qs = Doubt.objects.select_related('class_group', 'lecture', 'topic', 'raised_by', 'resolved_by')

        if self.action == 'list':
            qs = qs.annotate(reply_count=Count('messages', distinct=True))
        else:
            message_qs = DoubtMessage.objects.select_related('sender').annotate(
            like_count=Count('likes', distinct=True)
            )
            qs = qs.annotate(like_count=Count('likes', distinct=True)).prefetch_related(
                Prefetch('messages', queryset=message_qs)
            )

        if user.role == user.Role.DIRECTOR:
            qs = qs.filter(class_group__organization=user.organization)
        elif user.role == user.Role.TEACHER:
            qs = qs.filter(class_group__teacher_assignments__teacher=user)
        elif user.role == user.Role.STUDENT:
            qs = qs.filter(class_group__enrollments__student=user)
        else:
            return qs.none()

        class_group_id = self.request.query_params.get('class_group')
        if class_group_id:
            qs = qs.filter(class_group_id=class_group_id)   

        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param.upper())

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(question__icontains=search))

        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        doubt = serializer.save()
        detail = DoubtDetailSerializer(doubt, context={'request': request})
        return Response(detail.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Doubt.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        instance.refresh_from_db(fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        doubt = self.get_object()
        like, created = DoubtLike.objects.get_or_create(doubt=doubt, user=request.user)
        if not created:
            like.delete()
        return Response({"liked": created, "like_count": doubt.likes.count()})

    @action(detail=True, methods=['get','post'])
    def messages(self, request, pk=None):
        doubt = self.get_object()
        if request.method == 'GET':
            qs = doubt.messages.select_related('sender').annotate(like_count = Count('likes', distinct=True))
            serializer = DoubtMessageSerializer(qs, many=True, context = {'request' : request})
            return Response(serializer.data)

        serializer = DoubtMessageSerializer(data = request.data, context = {'request' : request})
        serializer.is_valid(raise_exception=True)
        serializer.save(doubt = doubt, sender = request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='messages/(?P<message_id>[^/.]+)/accept')
    def accept_message(self, request, pk=None, message_id = None):
        doubt = self.get_object()
        message = doubt.messages.filter(pk=message_id).first()
        if not message :
            return Response({"detail": "Message not found."}, status=404)

        message.is_accepted = True
        message.save()

        doubt.status = Doubt.Status.RESOLVED
        doubt.resolved_by = message.sender
        doubt.resolved_at = message.created_at
        doubt.save()

        return Response(DoubtDetailSerializer(doubt, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='messages/(?P<message_id>[^/.]+)/like')
    def like_message(self, request, pk=None, message_id=None):
        doubt = self.get_object()
        message = doubt.messages.filter(pk=message_id).first()

        if not message :
            return Response({"detail": "Message not found."}, status=404)

        like, created = DoubtMessageLike.objects.get_or_create(message=message, user=request.user)
        
        if not created:
            like.delete()
        
        return Response({"liked": created, "like_count": message.likes.count()})

