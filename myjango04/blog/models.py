# blog/models.py
from django.conf import settings
from django.db import models
from core.model_fields import IPv4AddressIntegerField, BooleanYNField


class AccessLog(models.Model):
    ip_generic = models.GenericIPAddressField(protocol="IPv4")
    ip_int = IPv4AddressIntegerField()


class Article(models.Model):
    title = models.CharField(max_length=100)
    is_public_ch = models.CharField(
        max_length=1, choices=[("Y", "예"), ("N", "아니요")], default="N"
    )
    is_public_yn = BooleanYNField(default=False)


class Category(models.Model):
    name = models.CharField(max_length=50)


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Post.Status.PUBLISHED)

    def draft(self):
        return self.filter(status=Post.Status.DRAFT)

    def search(self, query: str):
        return self.filter(title__icontains=query)

    def create(self, **kwargs):
        kwargs.setdefault("status", Post.Status.PUBLISHED)
        return super().create(**kwargs)


class Post(models.Model):
    class Status(models.TextChoices):  # 문자열 선택지
        DRAFT = "D", "초안"  # 상수, 값, 레이블
        PUBLISHED = "P", "발행"

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    status = models.CharField(
        # 선택지 값 크기에 맞춰 최대 길이를 지정
        max_length=1,
        # choices 속성으로 사용할 수 있도록 2중 리스트로 반환
        # choices 속성은 모든 모델 필드에서 지원합니다.
        choices=Status.choices,
        # status 필드에 대한 모든 값 지정에는 상수로 지정하면 쿼리에 값으로 자동 변환
        default=Status.DRAFT,
    )
    content = models.TextField()

    # 추가
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default=1,  # 기본값을 설정
    )

    created_at = models.DateTimeField(auto_now_add=True)  # 최초 생성시각을 자동 저장
    updated_at = models.DateTimeField(auto_now=True)  # 매 수정시각을 자동 저장

    objects = PostQuerySet.as_manager()

    def __str__(self):
        # choices 속성을 사용한 필드는 get_필드명_display() 함수를 통해 레이블 조회를 지원합니다.
        return f"{self.title} ({self.get_status_display()})"
