from typing import Any
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from blog.models import Post, Page
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic import ListView, DetailView

PER_PAGE = 9

class PostListView(ListView):
    template_name = 'blog/pages/index.html'
    context_object_name = 'posts'
    paginate_by = PER_PAGE
    queryset = Post.objects.get_published() # type: ignore

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     queryset = queryset.filter(is_published=True)
    #     return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Home | '
        return context



class CreatedByListView(PostListView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._temp_context: dict[str, Any] = {}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self._temp_context['user']
        user_full_name = user.username

        if user.first_name:
            user_full_name = f'{user.first_name} {user.last_name}'
        page_title = user_full_name + ' | '

        ctx['page_title'] = page_title

        return ctx
    
    def get(self, request, *args, **kwargs):
        author_pk = self.kwargs.get('author_pk')
        user = User.objects.filter(pk=author_pk).first()

        if user is None:
            raise Http404()
        
        self._temp_context.update({
            'author_pk': author_pk,
            'user': user
        })
                
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        qs = qs.filter(created_by__pk=self._temp_context['user'].pk)

        return qs 


class CategoryListView(PostListView):
    allow_empty = False

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(category__slug=self.kwargs.get('slug'))
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        page_title = f'{self.object_list[0].category.name}' + ' | ' # type: ignore
        ctx['page_title'] = page_title

        return ctx



class PageDetailView(DetailView):
    model = Page
    template_name = 'blog/pages/page.html'
    slug_field = 'slug'
    context_object_name = 'page'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_object()
        context['page_title'] = page.title + ' | ' # type: ignore
        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(is_published=True)
    

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/pages/post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['page_title'] = post.title + ' | ' # type: ignore
        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(is_published=True)
      


class TagListView(PostListView):
    allow_empty = False

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(tags__slug=self.kwargs.get('slug'))
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        page_title = f'{self.object_list[0].tags.first().name}' + ' | ' # type: ignore
        ctx['page_title'] = page_title

        return ctx


class SearchListView(PostListView):
    def __init__(self, **args): 
        super().__init__(**args)
        self._search_value = ''

    def setup(self, request, *args, **kwargs):
        self._search_value = request.GET.get('search', '').strip()
        return super().setup(request, *args, **kwargs)
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(
            Q(title__icontains=self._search_value) | 
            Q(excerpt__icontains=self._search_value) | 
            Q(content__icontains=self._search_value)
        )[:PER_PAGE]
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        search_value = self._search_value
        ctx.update({
            'search_value': search_value,
            'page_title': 'Search results for ' + search_value[:30] + ' | ',
        })
        return ctx
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not self._search_value:
            return redirect('blog:index')
        return response
