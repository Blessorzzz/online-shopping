# ecommerce/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView
from django.db.models import Q, Avg, Count, F, ExpressionWrapper, FloatField
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .models import KeywordSearchHistory, Product, SynonymCache
from shoppingcart.models import ShoppingCart
from review.models import Review
from forums.models import ForumPost

import requests
import json
import re
import jieba
import jieba.analyse
import jieba.posseg as pseg
from bs4 import BeautifulSoup
from glob import escape

from matplotlib.lines import Line2D
from itertools import product
import matplotlib
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

matplotlib.use('Agg')

# 首页视图，显示商品列表
class HomePageView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'
    paginate_by = 8  # Number of products per page

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        # Retrieve search query
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(product_name__icontains=query)

        # Retrieve weights for the four metrics (using defaults from settings if not provided)
        default_mhi_weight = getattr(settings, 'MHI_WEIGHT', 25)
        default_acr_weight = getattr(settings, 'ACR_WEIGHT', 35)
        default_vhd_weight = getattr(settings, 'VHD_WEIGHT', 30)
        default_ics_weight = getattr(settings, 'ICS_WEIGHT', 10)
        
        # Get user-selected weights from request, or use defaults if not provided
        mhi_weight = int(self.request.GET.get('mhi_weight', default_mhi_weight))
        acr_weight = int(self.request.GET.get('acr_weight', default_acr_weight))
        vhd_weight = int(self.request.GET.get('vhd_weight', default_vhd_weight))
        ics_weight = int(self.request.GET.get('ics_weight', default_ics_weight))

        # Retrieve the child's age range
        child_min_age = self.request.GET.get('child_min_age')
        child_max_age = self.request.GET.get('child_max_age')

        # Filter based on child's age range if both are provided
        if child_min_age and child_max_age:
            queryset = queryset.filter(
                min_age__lte=child_max_age,
                max_age__gte=child_min_age
            )

        # Normalize weights to sum to 100%
        total_weight = mhi_weight + acr_weight + vhd_weight + ics_weight
        if total_weight > 0:
            # Calculate normalized weights (each as a percentage of the total)
            # Note: If all weights are already equal (e.g., all set to 25%), 
            # they will remain the same after normalization
            normalized_mhi_weight = (mhi_weight / total_weight) * 100
            normalized_acr_weight = (acr_weight / total_weight) * 100
            normalized_vhd_weight = (vhd_weight / total_weight) * 100
            normalized_ics_weight = (ics_weight / total_weight) * 100
        else:
            # Use the default weights from settings if total_weight is 0
            normalized_mhi_weight = default_mhi_weight
            normalized_acr_weight = default_acr_weight
            normalized_vhd_weight = default_vhd_weight
            normalized_ics_weight = default_ics_weight

        # Define a safe sorting function that handles None values
        def calculate_safety_score(product):
            # For virtual products, return a very low score or handle differently
            if product.product_type != 'tangible':
                # Return a value that will put virtual products at the end of the list
                # when sorting in reverse=True order
                return -1
            
            # For tangible products, safely calculate the weighted score
            mhi_score = product.get_mhi_score() or 0
            acr_score = product.get_acr_score() or 0
            vhd_score = product.get_vhd_score() or 0
            ics_score = product.get_ics_score() or 0
            
            return (
                mhi_score * normalized_mhi_weight / 100 +
                acr_score * normalized_acr_weight / 100 +
                vhd_score * normalized_vhd_weight / 100 +
                ics_score * normalized_ics_weight / 100
            )

        # Sort products using the safe calculation function
        queryset = sorted(queryset, key=calculate_safety_score, reverse=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = context['products']

        # Calculate average rating for each product
        for product in products:
            reviews = Review.objects.filter(product=product, is_approved=True)
            if reviews.exists():
                average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            else:
                average_rating = None
            product.average_rating = average_rating

        context['products'] = products

        # Pass the weights to the template, using default values if not provided in the request
        context['mhi_weight'] = self.request.GET.get('mhi_weight', 25)
        context['acr_weight'] = self.request.GET.get('acr_weight', 35)
        context['vhd_weight'] = self.request.GET.get('vhd_weight', 30)
        context['ics_weight'] = self.request.GET.get('ics_weight', 10)

        # Pass the child's age range values to the template
        context['child_min_age'] = self.request.GET.get('child_min_age', '')
        context['child_max_age'] = self.request.GET.get('child_max_age', '')

        return context
    
# Function to generate radar chart from safety factors
def generate_radar_chart(safety_data):
    import numpy as np
    from matplotlib.lines import Line2D

    # Safety categories (short forms for chart labels)
    categories = list(safety_data.keys())  # Ensure all keys are included
    values = list(safety_data.values())

    # Full forms for the legend
    full_forms = {
        'MHI': 'Material Hazard Index (MHI)',
        'ACR': 'Age Compatibility Risk (ACR)',
        'VHD': 'Visual Hazard Detection (VHD)',
        'ICS': 'Information Completeness Score (ICS)'
    }

    # Colors for each safety factor
    colors = {
        'MHI': 'blue',
        'ACR': 'green',
        'VHD': 'red',
        'ICS': 'orange'
    }

    print("Safety Data:", safety_data)
    print("Categories:", categories)
    print("Full Forms:", full_forms)

    # Create radar chart
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values += values[:1]  # To close the radar chart
    angles += angles[:1]  # To close the radar chart

    # Plot the filled area for all safety factors
    ax.fill(angles, values, color='blue', alpha=0.25, label='Safety Factors')
    ax.plot(angles, values, color='blue', linewidth=2)

    # Set the labels (short forms)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)

    # Add radial tick labels (score indicators)
    ax.set_yticks([20, 40, 60, 80, 100])  # Example tick values
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=10, color='gray')

    # Manually create legend handles
    legend_handles = [
        Line2D([0], [0], color='blue', lw=2, label='Material Hazard Index (MHI)'),
        Line2D([0], [0], color='blue', lw=2, label='Age Compatibility Risk (ACR)'),
        Line2D([0], [0], color='blue', lw=2, label='Visual Hazard Detection (VHD)'),
        Line2D([0], [0], color='blue', lw=2, label='Information Completeness Score (ICS)')
    ]

    # Add the custom legend
    ax.legend(handles=legend_handles, loc='upper right', bbox_to_anchor=(1.5, 1.1), fontsize=10)

    # Save the plot to a BytesIO object and convert to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')  # Use bbox_inches to avoid clipping
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)  # Close the figure to free memory

    return img_str


# 商品详情页视图
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        sort_by = self.request.GET.get('sort', 'recent')
        review_id = self.request.GET.get('review_id')  # Retrieve the review_id from query parameters

        # Always annotate with vote counts
        reviews = Review.objects.filter(product=product, is_approved=True).annotate(
            like_count=Count('votes', filter=Q(votes__vote_type=True)),
            dislike_count=Count('votes', filter=Q(votes__vote_type=False))
        )

        if sort_by == 'helpful':
            reviews = reviews.order_by('-like_count', '-created_at')
        else:
            reviews = reviews.order_by('-created_at')

        # Highlight the specific review if review_id is provided
        highlighted_review = None
        if review_id:
            try:
                highlighted_review = reviews.get(pk=review_id)
            except Review.DoesNotExist:
                highlighted_review = None

        # Fetch the top 2 forum threads with the most comments
        featured_forums = ForumPost.objects.filter(product=product).annotate(
            comment_count=Count('comments')
        ).order_by('-comment_count')[:2]

        # Use the Product model's methods to get safety factors and safety score
        safety_factors = {
            'MHI': product.get_mhi_score(),
            'ACR': product.get_acr_score(),
            'VHD': product.get_vhd_score(),
            'ICS': product.get_ics_score(),
        }

        # Use the Product model's safety score
        safety_score = product.safety_score

        # Ensure safety_score is not None before rounding
        if safety_score is not None:
            safety_score = round(safety_score, 2)
        else:
            safety_score = 0  # Default value if safety_score is None

        # Generate the radar chart using the safety factors
        radar_chart = generate_radar_chart(safety_factors)

 
        context['reviews'] = reviews
        context['current_sort'] = sort_by
        context['highlighted_review'] = highlighted_review  # Pass the highlighted review to the template
        context['featured_forums'] = featured_forums  # Pass featured forums to the template
        context['safety_factors'] = safety_factors
        context['safety_score'] = round(safety_score, 2)
        context['radar_chart'] = radar_chart
        return context

@require_http_methods(["POST"])
def apply_custom_safety_filters(request):
    """Handle the custom safety filter requests"""
    if request.method == 'POST' and request.content_type == 'application/json':
        try:
            # Extract the weight profile from the form data
            weight_profile = json.loads(request.POST.get('weight_profile', '{}'))
            min_safety_score = float(request.POST.get('min_safety_score', 0))
            critical_issue_filters = json.loads(request.POST.get('critical_issue_filters', '{}'))
            
            # Create the filter URL with parameters
            filter_params = {
                'mhi_weight': int(weight_profile.get('mhi', 0.25) * 100),
                'acr_weight': int(weight_profile.get('acr', 0.35) * 100),
                'vhd_weight': int(weight_profile.get('vhd', 0.30) * 100),
                'ics_weight': int(weight_profile.get('ics', 0.10) * 100),
            }
            
            # Add child age range if provided
            min_age = request.POST.get('min_age')
            max_age = request.POST.get('max_age')
            if min_age and max_age:
                filter_params['child_min_age'] = min_age
                filter_params['child_max_age'] = max_age
            
            # Build the redirect URL
            base_url = reverse('home')
            redirect_url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in filter_params.items()])}"
            
            return JsonResponse({
                'success': True,
                'redirect_url': redirect_url
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

# Function to generate radar chart from safety factors
def generate_radar_chart(safety_data):

    # Safety categories (short forms for chart labels)
    categories = list(safety_data.keys())  # Ensure all keys are included
    values = list(safety_data.values())

    # Full forms for the legend
    full_forms = {
        'MHI': 'Material Hazard Index (MHI)',
        'ACR': 'Age Compatibility Risk (ACR)',
        'VHD': 'Visual Hazard Detection (VHD)',
        'ICS': 'Information Completeness Score (ICS)'
    }

    # Colors for each safety factor
    colors = {
        'MHI': 'blue',
        'ACR': 'green',
        'VHD': 'red',
        'ICS': 'orange'
    }

    print("Safety Data:", safety_data)
    print("Categories:", categories)
    print("Full Forms:", full_forms)

    # Create radar chart
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values += values[:1]  # To close the radar chart
    angles += angles[:1]  # To close the radar chart

    # Plot the filled area for all safety factors
    ax.fill(angles, values, color='blue', alpha=0.25, label='Safety Factors')
    ax.plot(angles, values, color='blue', linewidth=2)

    # Set the labels (short forms)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)

    # Add radial tick labels (score indicators)
    ax.set_yticks([20, 40, 60, 80, 100])  # Example tick values
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=10, color='gray')

    # Manually create legend handles
    legend_handles = [
        Line2D([0], [0], color='blue', lw=2, label='Material Hazard Index (MHI)'),
        Line2D([0], [0], color='blue', lw=2, label='Age Compatibility Risk (ACR)'),
        Line2D([0], [0], color='blue', lw=2, label='Visual Hazard Detection (VHD)'),
        Line2D([0], [0], color='blue', lw=2, label='Information Completeness Score (ICS)')
    ]

    # Add the custom legend
    ax.legend(handles=legend_handles, loc='upper right', bbox_to_anchor=(1.5, 1.1), fontsize=10)

    # Save the plot to a BytesIO object and convert to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')  # Use bbox_inches to avoid clipping
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)  # Close the figure to free memory

    return img_str

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

def accessibility_info(request):
    return render(request, 'accessibility_info.html')