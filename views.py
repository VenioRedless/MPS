from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from nlp.models import Article, Keyword
import os
import zipfile
import collections
from glob import glob
from gensim.models.doc2vec import Doc2Vec
from nlp.embedrank import EmbedRank
from nlp.nlp_uitl import tokenize
from pathlib import Path
from typing import List

UPLOADE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/txt/'

def index(request):
    return render(request,'nlp/index.html')

def article_list(request):
    articles = Article.objects.all()
    return render(request,'nlp/article_list.html',{'articles': articles})

def search_form(request):
    return render(request,'nlp/search_form.html')

# データベースから資料を検索
def search_city_form(request):
    citys = Article.objects.all().values_list('article_city',flat=True).order_by('article_city').distinct()
    return render(request,'nlp/search_city_form.html',{'citys': citys})

# ######
def search_city(request):
    if len(request.POST.getlist("city_name[]")):
        if request.POST['t_start'] and request.POST['t_end']:
            results = Keyword.objects.filter(article_city__in = request.POST.getlist('city_name[]'), article_year__range=(request.POST['t_start'],request.POST['t_end']))
            results_data = results.values_list("keyword_text",flat=True)
            results_list = list(results_data)
            c = collections.Counter(results_list)
            keyword_array = c.most_common()
        else:
            return HttpResponse("年度を入力してください。")
    else:
        return HttpResponse("都市名を選んでください。")
    return render(request,'nlp/keyword_list_city.html',{'cityname':request.POST.getlist("city_name[]"), 't_start':request.POST['t_start'], 't_end':request.POST['t_end'], 'keyword_array': keyword_array})

def search_city_q(request):
    if 'q' in request.GET:
        keywords = Keyword.objects.filter(keyword_text=request.GET['q']).values_list('article_id',flat=True)
        articles = Article.objects.filter(pk__in=list(keywords),article_city__in = request.GET.getlist('cityname'), article_year__range=(request.GET['t_start'],request.GET['t_end']))
    else:
        articles = 'You submitted an empty form.'
    return render(request,'nlp/article_result.html',{'articles': articles})


def search(request):
    if 'q' in request.GET:
        keywords = Keyword.objects.filter(keyword_text=request.GET['q']).values_list('article_id',flat=True)
        articles = Article.objects.filter(pk__in=list(keywords))
    else:
        articles = 'You submitted an empty form.'
    return render(request,'nlp/article_result.html',{'articles': articles})

def manage(request):
    return render(request,'nlp/manage.html')


# ####
def input(request):
    Article.objects.all().delete()
    Keyword.objects.all().delete()
    model = Doc2Vec.load('C:/Users/weake/Desktop/KIC/jawiki.doc2vec.dbow300d/jawiki.doc2vec.dbow300d.model')  # model
    embedrank = EmbedRank(model=model, tokenize=tokenize)

    file_list = glob('C:/Users/weake/Desktop/KIC/mps/mps/nsr_sourcecode/nsr/nlp/txt/*.txt')
    keywords = []
    id = 0
    for file in file_list:
        with open(file) as f:
            text_list = f.readlines()
        
        year = file[29:33]
        category= file[34:36]
        city_name = file[37:-4]

        for text in text_list:
            if text.isspace() == False and len(text)>20:
                tmp_article = Article(article_id=id,article_year=int(year),article_category=category,article_city=city_name,article_text=text)
                tmp_article.save()
                
                results = embedrank.extract_keyword(text)  # キーワードリスト
                for result in results:
                    tmp_keyword = Keyword(keyword_text=result[0],article_id=id,article_year=int(year),article_category=category,article_city=city_name)
                    tmp_keyword.save()
                id += 1
    return HttpResponse("<p>処理完了!</p><p><a href=\"/nlp/\">前に戻る</a></p>")

def count(request):
    keywords = []
    results = Keyword.objects.all()
    results_data = results.values_list("keyword_text",flat=True)
    results_list = list(results_data)
    c = collections.Counter(results_list)
    keyword_array = c.most_common()

    return render(request,'nlp/keyword_list.html',{'keyword_array': keyword_array})

def count_q(request):
    if len(request.POST.getlist("cate[]")):
        if request.POST['t_start'] and request.POST['t_end']:
            results = Keyword.objects.filter(article_category__in = request.POST.getlist('cate[]'), article_year__range=(request.POST['t_start'],request.POST['t_end']))
            results_data = results.values_list("keyword_text",flat=True)
            results_list = list(results_data)
            c = collections.Counter(results_list)
            keyword_array = c.most_common()
        else:
            return HttpResponse("年度を入力してください。")
    else:
        return HttpResponse("種類を選んでください。")
    return render(request,'nlp/keyword_list_q.html',{'cate':request.POST.getlist("cate[]"), 't_start':request.POST['t_start'], 't_end':request.POST['t_end'], 'keyword_array': keyword_array})

def search_cate(request):
    if 'q' in request.GET:
        keywords = Keyword.objects.filter(keyword_text=request.GET['q']).values_list('article_id',flat=True)
        articles = Article.objects.filter(pk__in=list(keywords),article_category__in = request.GET.getlist('cate'), article_year__range=(request.GET['t_start'],request.GET['t_end']))
    else:
        articles = 'You submitted an empty form.'
    return render(request,'nlp/article_result.html',{'articles': articles})

def zip_upload(request):
    if request.method != 'POST':
        return render(request, 'nlp/zip_upload.html')

    file = request.FILES['file']
    path = os.path.join(UPLOADE_DIR, file.name)
    destination = open(path, 'wb+')

    for chunk in file.chunks():
        destination.write(chunk)
    
    return redirect('/nlp/zip_exact?filename='+file.name)

def zip_exact(request):
    path =UPLOADE_DIR + request.GET.get('filename')
    file_list = glob('C:/Users/weake/Desktop/KIC/mps/mps/nsr_sourcecode/nsr/nlp/txt/*.txt')
    for file in file_list:
        if os.path.isfile(file):
            os.remove(file)
    with zipfile.ZipFile(path) as zfile:
        for info in zfile.infolist():
            _rename(info)
            zfile.extract(info, path=UPLOADE_DIR)
    return HttpResponse("<p>Upload finished!</p><p><a href=\"/nlp/manage/\">前に戻る</a></p>")

def list_sjis_zip(src_zip: str) -> List[zipfile.ZipInfo]:
    """SJIS の zip ファイルの中身をファイル名の文字化けを避けてリストアップする"""
    info_all = []
    with zipfile.ZipFile(src_zip) as zfile:
        for info in zfile.infolist():
            _rename(info)
            info_all.append(info)
    return info_all

def _rename(info: zipfile.ZipInfo) -> None:
    """ヘルパー: `ZipInfo` のファイル名を SJIS でデコードし直す"""
    LANG_ENC_FLAG = 0x800
    encoding = 'utf-8' if info.flag_bits & LANG_ENC_FLAG else 'cp437'
    info.filename = info.filename.encode(encoding).decode('cp932')
    





# def get_queryset(request):
#     q_word = request.POST.get('query')

#     if q_word:
#         keywords = Keyword.objects.filter(keyword_text=q_word)
#         for keyword in keywords:
#             articles.append(Article.objects.filter(article_id=str(keyword)))
#     else:
#         articles = Article.objects.all()
#     return HttpResponse(q_word)
