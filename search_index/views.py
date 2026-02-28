from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import *
from .async_elastic import *
from .models import Book
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from custom_users.models import  *




@login_required
def book_detail(request, book_id):
    # 根据书籍 ID 查找书籍，若不存在则返回 404 错误
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'search_index/book_detail.html', {
        'book': book,
    })

def index(request):
    img_url=img()
    return render(request,'search_index/index.html', {'img_url': img_url})
# def search(request):
#     return render(request,'search_index/search.html')
def get_client_ip(request):
    """获取用户的 IP 地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def simple_search(request):
    query = None
    results = None
    client_ip = get_client_ip(request)  # 获取用户 IP
    page = int(request.GET.get("page", 1))  # 获取当前页码，默认第 1 页
    size = 10  # 每页结果数量

    if request.method == "GET":
        form = SimpleSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            if request.user.is_authenticated:
                SearchHistory.objects.create(user=request.user, query=query)
            es_helper = ElasticsearchHelper()
            search_result = es_helper.simple_search(query=query, page=page, size=size)

            results = search_result.get("results", [])
            if request.user.is_authenticated:
                for result in results[:10]:
                    if result["category"] is not None:
                        SearchHistory.objects.create(user=request.user, query=result["category"])
                    if result["tag"] is not None:
                        SearchHistory.objects.create(user=request.user, query=result["tag"])
            total = search_result.get("total", 0)
            pages = (total // size) + (1 if total % size > 0 else 0)  # 计算总页数

            # 限制分页范围，显示当前页前后 5 页
            start_page = max(1, page - 5)
            end_page = min(pages, page + 5)
            pagination_range = range(start_page, end_page + 1)

            return render(request, 'search_index/search.html', {
                'form': form,
                'query': query,
                'results': results,
                'client_ip': client_ip,
                'total': total,
                'pages': pages,
                'current_page': page,
                'pagination_range': pagination_range,  # 传递到模板
            })
    else:
        form = SimpleSearchForm()

    return render(request, 'search_index/search.html', {
        'form': form,
        'query': query,
        'results': results,
        'client_ip': client_ip,
    })

def advanced_search(request):
    form = AdvancedSearchForm(request.GET)
    ip = get_client_ip(request)
    results = None
    page = int(request.GET.get("page", 1))
    size = 10  # 每页显示的数量

    if form.is_valid():

        es_helper = ElasticsearchHelper()

        # 获取表单字段
        query = form.cleaned_data.get("query")
        authors = form.cleaned_data.get("authors")
        tags = form.cleaned_data.get("tags")
        click_min = form.cleaned_data.get("click_min")
        click_max = form.cleaned_data.get("click_max")
        char_min = form.cleaned_data.get("char_min")
        char_max = form.cleaned_data.get("char_max")

        # 构造范围
        click_range = (click_min, click_max) if click_min or click_max else None
        char_range = (char_min, char_max) if char_min or char_max else None

        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, query=query)
        search_result = es_helper.advanced_search(
            query=query, authors=authors, tags=tags,
            click_range=click_range, char_range=char_range,
            page=page, size=size
        )

        results = search_result.get("results", [])
        total = search_result.get("total", 0)
        pages = (total // size) + (1 if total % size > 0 else 0)

        # 动态调整分页范围
        start_page = max(1, page - 5)
        end_page = min(pages, page + 5)
        pagination_range = range(start_page, end_page + 1)

        return render(request, 'search_index/advanced_search.html', {
            'form': form,
            'client_ip': ip,
            'results': results,
            'total': total,
            'current_page': page,
            'pages': pages,
            'pagination_range': pagination_range,
        })

    return render(request, 'search_index/advanced_search.html', {'form': form})


# def book_recommend(request):
#     try:
#         user = request.user
#         word = recommend_search_term(user)
#         book_id = recommend_book(word)
#         if not book_id:
#             return HttpResponse("No recommended book found.")
#         return redirect('search_index:book_detail', book_id=book_id)
#     except ValueError as e:
#         # 捕获到错误，渲染一个定制的错误页面
#         return render(request, 'search_index/not_found.html', {'error_message': str(e)})

@login_required
def book_recommend(request):
    try:
        user = request.user
        word = recommend_search_term(user)
        book_id = recommend_book(word)

        if not book_id:
            # 如果没有推荐书籍，可以做一些处理
            return HttpResponse("No recommended book found.")

        return redirect('search_index:book_detail', book_id=book_id)
    except ValueError as e:
        return render(request, 'search_index/not_found.html', {'error_message': str(e)})

