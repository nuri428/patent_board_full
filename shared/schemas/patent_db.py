from django.db import models
import json
from typing import List, Optional


class PatentManager(models.Manager):
    def get_by_patent_id(self, patent_id: str):
        return self.get_queryset().filter(patent_id=patent_id).first()
    
    def search_patents(self, query: Optional[str] = None, title: Optional[str] = None, 
                      abstract: Optional[str] = None, assignee: Optional[str] = None, 
                      inventors: Optional[List[str]] = None, status: Optional[str] = None, 
                      filing_date_from=None, filing_date_to=None, sort_by: str = 'filing_date', 
                      sort_order: str = 'desc'):
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(title__icontains=query)
        
        if title:
            queryset = queryset.filter(title__icontains=title)
        
        if abstract:
            queryset = queryset.filter(abstract__icontains=abstract)
        
        if assignee:
            queryset = queryset.filter(assignee__icontains=assignee)
        
        if inventors:
            for inventor in inventors:
                queryset = queryset.filter(inventors__contains=[inventor])
        
        if status:
            queryset = queryset.filter(status=status)
        
        if filing_date_from:
            queryset = queryset.filter(filing_date__gte=filing_date_from)
        
        if filing_date_to:
            queryset = queryset.filter(filing_date__lte=filing_date_to)
        
        if sort_order.lower() == 'desc':
            queryset = queryset.order_by(f'-{sort_by}')
        else:
            queryset = queryset.order_by(sort_by)
        
        return queryset


class Patent(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('granted', 'Granted'),
        ('expired', 'Expired'),
        ('abandoned', 'Abandoned'),
        ('rejected', 'Rejected'),
    ]
    
    PATENT_TYPE_CHOICES = [
        ('utility', 'Utility Patent'),
        ('design', 'Design Patent'),
        ('plant', 'Plant Patent'),
    ]
    
    COUNTRY_CHOICES = [
        ('US', 'United States'),
        ('KR', 'Korea'),
        ('JP', 'Japan'),
        ('CN', 'China'),
        ('EP', 'European Patent'),
    ]
    
    patent_id = models.CharField(max_length=50, primary_key=True, unique=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, db_index=True)
    patent_type = models.CharField(max_length=10, choices=PATENT_TYPE_CHOICES, default='utility')
    title = models.CharField(max_length=1000, db_index=True)
    abstract = models.TextField()
    claims = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    filing_date = models.DateField(null=True, blank=True, db_index=True)
    publication_date = models.DateField(null=True, blank=True, db_index=True)
    grant_date = models.DateField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assignee = models.CharField(max_length=500, null=True, blank=True, db_index=True)
    inventors = models.JSONField(default=list, blank=True)
    applicants = models.JSONField(default=list, blank=True)
    ipc_classifications = models.JSONField(default=list, blank=True)
    uspc_classifications = models.JSONField(default=list, blank=True)
    priority_date = models.DateField(null=True, blank=True)
    family_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    citations = models.JSONField(default=list, blank=True)
    cited_by = models.JSONField(default=list, blank=True)
    legal_status = models.CharField(max_length=100, null=True, blank=True)
    renewal_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = PatentManager()
    
    class Meta:
        db_table = 'patents'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['assignee']),
            models.Index(fields=['filing_date']),
            models.Index(fields=['publication_date']),
            models.Index(fields=['grant_date']),
            models.Index(fields=['country']),
            models.Index(fields=['family_id']),
            models.Index(fields=['status', 'filing_date']),
        ]
    
    def __str__(self):
        return f"{self.patent_id}: {self.title[:50]}..."
    
    def get_inventor_names(self):
        if self.inventors and isinstance(self.inventors, str):
            return json.loads(self.inventors)
        return self.inventors if self.inventors else []
    
    def set_inventors(self, inventor_list: List[str]):
        self.inventors = inventor_list
        self.save()
    
    def is_us_patent(self):
        return self.country == 'US'
    
    def is_korean_patent(self):
        return self.country == 'KR'


class PatentFamily(models.Model):
    family_id = models.CharField(max_length=100, primary_key=True, unique=True)
    title = models.CharField(max_length=1000)
    abstract = models.TextField(null=True, blank=True)
    earliest_filing_date = models.DateField(null=True, blank=True)
    office_of_first_filing = models.CharField(max_length=2)
    total_members = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patent_families'
        indexes = [
            models.Index(fields=['family_id']),
            models.Index(fields=['earliest_filing_date']),
        ]


class PatentClassification(models.Model):
    id = models.AutoField(primary_key=True)
    patent = models.ForeignKey(Patent, on_delete=models.CASCADE, related_name='classifications')
    classification_system = models.CharField(max_length=10)
    classification_code = models.CharField(max_length=50)
    classification_title = models.CharField(max_length=500, null=True, blank=True)
    main_classification = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'patent_classifications'
        indexes = [
            models.Index(fields=['patent', 'classification_system']),
            models.Index(fields=['classification_code']),
            models.Index(fields=['main_classification']),
        ]