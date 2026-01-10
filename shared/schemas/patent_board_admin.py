from django.db import models
from django.contrib.auth.models import AbstractUser
import json
from typing import List, Optional


class User(AbstractUser):
    email = models.EmailField(unique=True)
    organization = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'


class ChatSession(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'chat_sessions'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Session {self.id} - {self.user.username}"


class ChatMessage(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    response = models.TextField()
    patent_ids = models.JSONField(default=list, blank=True)
    message_type = models.CharField(max_length=20, default='chat')  # chat, search, analysis
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['message_type']),
        ]
    
    def get_patent_ids(self) -> List[str]:
        if self.patent_ids and isinstance(self.patent_ids, str):
            return json.loads(self.patent_ids)
        return self.patent_ids if self.patent_ids else []
    
    def set_patent_ids(self, patent_id_list: List[str]):
        self.patent_ids = patent_id_list
        self.save()


class SearchHistory(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=500)
    filters = models.JSONField(default=dict, blank=True)
    result_count = models.IntegerField(default=0)
    patent_ids = models.JSONField(default=list, blank=True)
    search_type = models.CharField(max_length=20, default='simple')  # simple, advanced
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_history'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['search_type']),
            models.Index(fields=['created_at']),
        ]
    
    def get_patent_ids(self) -> List[str]:
        if self.patent_ids and isinstance(self.patent_ids, str):
            return json.loads(self.patent_ids)
        return self.patent_ids if self.patent_ids else []
    
    def set_patent_ids(self, patent_id_list: List[str]):
        self.patent_ids = patent_id_list
        self.save()


class Report(models.Model):
    REPORT_TYPES = [
        ('analysis', 'Analysis'),
        ('market', 'Market'),
        ('competitive', 'Competitive'),
        ('comprehensive', 'Comprehensive'),
        ('custom', 'Custom'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.CharField(max_length=50, primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=500)
    topic = models.CharField(max_length=500, db_index=True)
    content = models.TextField(null=True, blank=True)
    patent_ids = models.JSONField(default=list, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, default='analysis')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(null=True, blank=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reports'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['topic']),
            models.Index(fields=['report_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.id}: {self.title[:50]}..."
    
    def get_patent_ids(self) -> List[str]:
        if self.patent_ids and isinstance(self.patent_ids, str):
            return json.loads(self.patent_ids)
        return self.patent_ids if self.patent_ids else []
    
    def set_patent_ids(self, patent_id_list: List[str]):
        self.patent_ids = patent_id_list
        self.save()


class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    default_search_country = models.CharField(max_length=2, default='US')
    default_result_count = models.IntegerField(default=10)
    auto_save_searches = models.BooleanField(default=True)
    notification_enabled = models.BooleanField(default=True)
    preferred_language = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'


class PatentBookmark(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    patent_id = models.CharField(max_length=50)
    title = models.CharField(max_length=500)
    notes = models.TextField(null=True, blank=True)
    folder = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'patent_bookmarks'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['patent_id']),
            models.Index(fields=['folder']),
        ]
        unique_together = ['user', 'patent_id']


class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('search', 'Search'),
        ('chat', 'Chat'),
        ('report', 'Report'),
        ('bookmark', 'Bookmark'),
        ('export', 'Export'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=500)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['created_at']),
        ]