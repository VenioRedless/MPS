from django.db import models

# Create your models here.

class Article(models.Model):
    article_id = models.IntegerField(primary_key=True) #文章（段落）ID
    article_year = models.IntegerField()  #文章の発行年度
    article_category = models.CharField(max_length=100) # 文章の区分
    article_city = models.CharField(max_length=50) # 文章の都市名
    article_text = models.TextField() # 文章のテキスト内容
    
    def __str__(self):
        return self.article_text

class Keyword(models.Model):
    keyword_text = models.CharField(max_length=100) #キーワード名
    article_id = models.IntegerField() #　キーワードが含まれる文章のID
    article_year = models.IntegerField() # キーワードが含まれる文章の発行年度
    article_category = models.CharField(max_length=100) # キーワードが含まれる文章の区分
    article_city = models.CharField(max_length=50) # キーワードが含まれる文章の都市名

    def __str__(self):
        return str(self.article_id) + self.keyword_text


