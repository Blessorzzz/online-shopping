# ecommerce/views.py
from glob import escape
from itertools import product
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView
from django.db.models import Q, Avg
import requests
from .models import KeywordSearchHistory, Product, SynonymCache
from shoppingcart.models import ShoppingCart  # 引用购物车模型
from review.models import Review

# 首页视图，显示商品列表
class HomePageView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'
    paginate_by = 8  # 每页显示的商品数

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(product_name__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = context['products']
        
        # Calculate average rating for each product
        for product in products:
            # Get reviews for the product
            reviews = Review.objects.filter(product=product, is_approved=True)
            # Calculate the average rating for the product
            if reviews.exists():
                average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            else:
                average_rating = None
            # Add the average rating to the product object for template use
            product.average_rating = average_rating
        
        context['products'] = products
        return context


# 商品详情页视图
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        reviews = Review.objects.filter(product=product, is_approved=True).order_by("-created_at")
        context['reviews'] = reviews
        return context


# 购物车页面视图
class CartView(ListView):
    model = ShoppingCart
    template_name = 'view_cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        # 获取当前用户的购物车项
        return ShoppingCart.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 计算购物车总金额
        cart_items = context['cart_items']
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        context['total_amount'] = total_amount
        return context


# 更新购物车商品数量视图
class UpdateCartView(UpdateView):
    model = ShoppingCart
    fields = ['quantity']
    template_name = 'update_cart.html'

    def form_valid(self, form):
        cart_item = form.save(commit=False)
        cart_item.user = self.request.user  # 确保是当前用户的购物车项
        cart_item.save()
        return redirect('view_cart')  # 更新成功后重定向到购物车页面


# 删除购物车商品视图
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(ShoppingCart, id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('view_cart')  # 删除后重定向到购物车页面


# 产品搜索视图函数
def search_products(request):
    query = request.GET.get('q', '')
    is_sequential_search = request.GET.get('sequential_search') == 'true'
    current_search_index = int(request.GET.get('search_index', 0))
    all_search_terms_json = request.GET.get('all_search_terms', '[]')
    
    # 初始化
    
    search_context = {
        'query': query,
        'products': [],
        'no_results': False
    }
    
    # 如果有搜索查询
    if query:
        # 执行搜索
        search_results = product.filter(
            Q(product_name__icontains=query) | 
            Q(description__icontains=query)
        ).distinct()
        
        # 添加到上下文
        search_context['products'] = search_results
        search_context['no_results'] = not search_results.exists()
        
        # 处理序列搜索
        if is_sequential_search:
            try:
                all_search_terms = json.loads(all_search_terms_json)
                search_context['is_sequential_search'] = True
                search_context['current_search_index'] = current_search_index
                search_context['all_search_terms'] = all_search_terms
                search_context['all_search_terms_json'] = all_search_terms_json  # 保存原始JSON
                search_context['total_terms'] = len(all_search_terms)
                
                # 计算前一个和后一个索引
                search_context['prev_index'] = max(0, current_search_index - 1)
                search_context['next_index'] = min(len(all_search_terms) - 1, current_search_index + 1)
                
                # 检查是否是第一个或最后一个
                search_context['is_first'] = current_search_index == 0
                search_context['is_last'] = current_search_index == len(all_search_terms) - 1
                
                # 构建前一个和后一个查询的URL
                base_url = reverse('search_products')
                all_terms_escaped = escape(all_search_terms_json)
                
                if not search_context['is_first']:
                    prev_term = all_search_terms[search_context['prev_index']]['term']
                    search_context['prev_url'] = f"{base_url}?q={prev_term}&sequential_search=true&search_index={search_context['prev_index']}&all_search_terms={all_terms_escaped}"
                
                if not search_context['is_last']:
                    next_term = all_search_terms[search_context['next_index']]['term']
                    search_context['next_url'] = f"{base_url}?q={next_term}&sequential_search=true&search_index={search_context['next_index']}&all_search_terms={all_terms_escaped}"
            
            except Exception as e:
                print(f"序列搜索处理错误: {e}")
    
    return render(request, 'search_results.html', search_context)

import requests
from bs4 import BeautifulSoup
import json
import re
import jieba
import jieba.analyse
import jieba.posseg as pseg  # 导入词性标注模块
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# 确保jieba加载完成
jieba.initialize()
print("Jieba已初始化")

# 从kmcha.com获取近义词
def get_online_synonyms(word):
    """
    从kmcha.com获取词语的近义词
    """
    try:
        # 构建URL
        url = f'https://kmcha.com/similar/{word}'
        
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        
        # 发送请求
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()  # 如果状态码不是200，抛出异常
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有包含近义词的span标签
        # 多种选择器尝试
        synonym_spans = soup.select('.word-list span') or soup.select('.similar-word-item') or soup.select('span.word')
        
        # 如果上面的选择器都没找到，尝试查找所有可能的span标签
        if not synonym_spans:
            all_spans = soup.find_all('span')
            # 过滤出可能包含近义词的span
            synonym_spans = [span for span in all_spans if len(span.text.strip()) > 0 and not span.find_all()]
        
        # 提取近义词
        synonyms = []
        for span in synonym_spans:
            text = span.text.strip()
            if text and text != word and text not in synonyms:
                synonyms.append(text)
        
        print(f"从网络获取到 {word} 的近义词: {synonyms}")
        return synonyms[:5]  # 返回前5个近义词
        
    except Exception as e:
        print(f"获取 {word} 的近义词出错: {str(e)}")
        return []  # 如果出错，返回空列表

# 简单的内存缓存
synonym_cache = {}

@csrf_exempt
@require_http_methods(["POST"])
def extract_keywords(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        
        # 清理文本，移除标点符号等
        cleaned_text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        
        # 调试信息
        print(f"原始文本: '{text}'")
        print(f"清理后文本: '{cleaned_text}'")
        
        # 使用jieba进行词性标注
        words_with_pos = pseg.cut(cleaned_text)
        
        # 提取名词类词语（n开头的词性表示名词，包括：n, nr, ns, nt, nz等）
        nouns = []
        for word, flag in words_with_pos:
            print(f"分词: {word}, 词性: {flag}")
            if flag.startswith('n') or flag.startswith('t'):  # 名词且长度大于1
                nouns.append(word)
        
        print("提取的名词:", nouns)
        
        # 如果名词为空，尝试使用TF-IDF提取关键词
        if not nouns:
            keywords = jieba.analyse.extract_tags(
                cleaned_text, 
                topK=5,
                withWeight=False
            )
            print("TF-IDF关键词 (备选):", keywords)
        else:
            # 优先使用名词作为关键词，但也可以使用TF-IDF进行排序
            keywords = jieba.analyse.extract_tags(
                cleaned_text, 
                topK=10,  # 先提取多一些关键词
                withWeight=True
            )
            
            # 转换为字典，方便查找权重
            keyword_weights = {word: weight for word, weight in keywords}
            
            # 按TF-IDF权重给名词排序
            nouns_with_weights = [(noun, keyword_weights.get(noun, 0)) for noun in nouns]
            nouns_with_weights.sort(key=lambda x: x[1], reverse=True)
            
            # 最终关键词：优先选择名词，按权重排序
            keywords = [noun for noun, _ in nouns_with_weights]
            
            # 如果名词太少，添加一些其他高权重词
            if len(keywords) < 3:
                # 添加非名词的高权重词
                for word, _ in sorted(keyword_weights.items(), key=lambda x: x[1], reverse=True):
                    if word not in keywords and len(keywords) < 3:
                        keywords.append(word)
        
        print("最终选择的关键词:", keywords)
        
        # 特殊处理：判断特定关键词
        special_keywords = ["小马宝莉", "机器人", "玩偶"]
        for special in special_keywords:
            if special in text and special not in keywords:
                keywords.insert(0, special)
                print(f"添加特殊关键词: {special}")
        
        # 为关键词获取近义词
        expanded_words = []
        
        # 预定义的同义词字典作为备选
        backup_dict = {
            '机器人': ['玩具机器人', '智能机器人', '遥控机器人', '机器玩具'],
            '小马宝莉': ['彩虹小马', '小马公主', '儿童玩具', '女孩玩具'],
            '玩偶': ['洋娃娃', '布娃娃', '毛绒玩具', '公仔', '玩具娃娃'],
            '玩具': ['积木', '毛绒玩具', '拼图', '益智玩具', '玩偶'],
            '娃娃': ['洋娃娃', '布娃娃', '芭比娃娃', '玩偶'],
            '游戏': ['电子游戏', '手机游戏', '游戏机', '益智游戏'],
            '手柄': ['游戏手柄', '控制器', '游戏配件', '无线手柄'],
            '游戏手柄': ['手柄', '无线手柄', 'PS手柄', 'Xbox手柄', '手游手柄']
        }
        
        # 为每个关键词获取近义词 - 不仅仅是第一个关键词
        for keyword in keywords:
            if len(keyword) <= 1:  # 跳过单字词
                continue
                
            print(f"为关键词 '{keyword}' 获取近义词")
            
            # 查看缓存
            if keyword in synonym_cache:
                online_synonyms = synonym_cache[keyword]
                print(f"从缓存获取近义词: {online_synonyms}")
            else:
                # 从网络获取近义词
                online_synonyms = get_online_synonyms(keyword)
                # 保存到缓存
                synonym_cache[keyword] = online_synonyms
            
            # 如果网络获取成功
            if online_synonyms:
                for syn in online_synonyms:
                    if syn not in expanded_words and syn not in keywords:
                        expanded_words.append(syn)
                        print(f"添加网络近义词: {syn}")
            else:
                # 备选：使用预定义字典
                print(f"网络获取失败，使用备选字典")
                if keyword in backup_dict:
                    for syn in backup_dict[keyword]:
                        if syn not in expanded_words and syn not in keywords:
                            expanded_words.append(syn)
                            print(f"添加备选近义词: {syn}")
                # 部分匹配
                else:
                    for key in backup_dict:
                        if key in keyword or keyword in key:
                            for syn in backup_dict[key]:
                                if syn not in expanded_words and syn not in keywords:
                                    expanded_words.append(syn)
                                    print(f"添加部分匹配备选近义词: {syn}")
        
        # 限制扩展关键词数量
        expanded_words = expanded_words[:5]
        print("最终扩展关键词:", expanded_words)
        
        # 返回结果
        return JsonResponse({
            'success': True,
            'keywords': keywords,
            'expanded_keywords': expanded_words
        })
        
    except Exception as e:
        import traceback
        print(f"关键词提取错误: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from .models import Product  
def ajax_search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(description__icontains=query) 
        ).distinct()
    else:
        products = Product.objects.none()

    # 渲染产品列表的 HTML 片段
    html = render_to_string('product_list_partial.html', {'products': products}, request=request)
    return JsonResponse({'html': html})