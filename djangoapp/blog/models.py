from django.db import models
from utils.rands import slugify_unique
from django.contrib.auth.models import User
from utils.res_images import resize_image
from django.urls import reverse 
from django_summernote.models import AbstractAttachment # type: ignore

class PostAttachment(AbstractAttachment):
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.file.name
            
        current_file_name = str(self.file.name)
        super_save = super().save(*args, **kwargs)
        file_changed = False

        if self.file:
            file_changed = current_file_name != str(self.file.name)

        if file_changed:
            print('Cover changed')
            resize_image(self.file, new_width=900, optimize=True)
        
        return super_save

class Tag(models.Model):
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    name = models.CharField(max_length=80)
    slug = models.SlugField(
        max_length=155, 
        unique=True, 
        default= None,
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_unique(self.name)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name



class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=80)
    slug = models.SlugField(
        max_length=155, 
        unique=True, 
        default= None,
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_unique(self.name)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Page(models.Model):
    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'

    title = models.CharField(max_length=65)
    slug = models.SlugField(
        unique=True,
        default='',
        blank=True,
        null=False,
        max_length=155
    )

    is_published = models.BooleanField(
        default=False,
        help_text='Este campo precisa ser marcado para que a página seja publicada.'
        )
    content = models.TextField()

    def get_absolute_url(self):
        if not self.is_published:
            return reverse('blog:index')
        return reverse('blog:page', args=(self.slug,))    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_unique(self.title)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    

class PostManager(models.Manager):
    def get_published(self):
        return self.filter(is_published=True).order_by('-pk')

class Post(models.Model):
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    objects = PostManager()
    
    title = models.CharField(max_length=65)
    slug = models.SlugField(
        unique=True,
        default='',
        blank=True,
        null=False,
        max_length=155
    )

    excerpt = models.CharField(max_length=155)
    is_published = models.BooleanField(
        default=False,
        help_text='Este campo precisa ser marcado para que o post seja publicado.'
        )
    
    content = models.TextField()
    cover = models.ImageField(upload_to='posts/%Y/%m/', blank=True, default='')
    cover_in_post_content = models.BooleanField(
        default=True,
        help_text='Se marcado, exibe a imagem de capa no conteúdo do post.'
        )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='post_created_by',
        )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='post_updated_by',
        )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None
    )
    tags = models.ManyToManyField(Tag, blank=True, default='')

    def __str__(self):
        return self.title
    
    
    def get_absolute_url(self):
        if not self.is_published:
            return reverse('blog:index')
        return reverse('blog:post', args=(self.slug,))
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_unique(self.title)
        
        current_cover_name = str(self.cover.name)
        super_save = super().save(*args, **kwargs)
        cover_changed = False

        if self.cover:
            cover_changed = current_cover_name != str(self.cover.name)

        if cover_changed:
            print('Cover changed')
            resize_image(self.cover, new_width=900, optimize=True)
        
        return super_save
