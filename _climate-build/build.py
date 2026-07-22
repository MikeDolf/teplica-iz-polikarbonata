# -*- coding: utf-8 -*-
"""Пересборка климат-страниц (item/, catalog/) с расширенным контентом.
Запуск: python3 _climate-build/build.py
"""
import os, sys, json, html
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE,"data"))
from jinja2 import Environment, FileSystemLoader, select_autoescape
from families import FAMILIES
from pages import PAGES, SPECS
D="https://fanline.su/"
env=Environment(loader=FileSystemLoader(os.path.join(HERE,"templates")), autoescape=select_autoescape(["html"]))

def esc(s): return html.escape(str(s), quote=True)

# для «Похожих товаров» — по семейству
by_fam={}
for url,kind,fam,name,model,affil,canon in PAGES:
    if kind=="product": by_fam.setdefault(fam,[]).append((url,name))

def build_schema(kind, h1, desc, self_url, faq, breadcrumb2, specs_rows=None):
    graph=[{"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Главная","item":D},
        {"@type":"ListItem","position":2,"name":breadcrumb2,"item":self_url},
        {"@type":"ListItem","position":3,"name":h1,"item":self_url}]}]
    if kind!="category":
        prod={"@type":"Product","name":h1,"description":desc,"category":"Климатическая техника",
              "brand":{"@type":"Brand","name":"Fanline"},"url":self_url}
        if specs_rows:
            prod["additionalProperty"]=[{"@type":"PropertyValue","name":k,"value":v} for k,v in specs_rows]
        graph.append(prod)
    if faq:
        graph.append({"@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]})
    return json.dumps({"@context":"https://schema.org","@graph":graph}, ensure_ascii=False, indent=2)

def render(url,kind,fam,name,model,affil,canon):
    F=FAMILIES[fam]
    self_url=D+url+"/"
    canonical=canon or self_url
    spec=SPECS.get(url)
    if kind=="product" and spec:
        # де-канонизированная модель: уникальный контент из реальных ТТХ, self-canonical
        h1=name
        canonical=self_url
        intro=spec["lead"]
        title=name.replace("«","").replace("»","")
        if len(title)>52: title=model.replace("«","").replace("»","")+", характеристики и цена"
        else: title=name+", характеристики"
        desc=spec["lead"][:165]
        # уникальные секции: параграфы про модель + одна общая секция «как выбрать» для контекста
        sections=[{"h":"Особенности модели "+model,"p":spec["paras"]}]
        choose=[s for s in F["sections"] if s["h"].startswith("Как выбрать")]
        sections+=choose
        faq=F["faq"]
        specs_rows=spec["specs"]
        rel=[{"url":"/"+u+"/","text":n} for u,n in by_fam.get(fam,[]) if u!=url][:6]
    elif kind=="product":
        h1=name
        intro=("Это конкретная модель, "+model+". ") if model else ""
        intro+=F["intro"]
        title=name+", цены и характеристики"
        desc=F["intro"][:150]
        sections=F["sections"]; faq=F["faq"]
        specs_rows=None
        rel=[{"url":"/"+u+"/","text":n} for u,n in by_fam.get(fam,[]) if u!=url][:6]
    elif kind=="category":
        h1=name
        intro=F["intro"]
        title=name+", как выбрать и цены"
        desc=(name+". "+F["intro"])[:155]
        sections=F["sections"]; faq=F["faq"]
        specs_rows=None
        rel=[{"url":"/"+u+"/","text":n} for u,n in by_fam.get(fam,[])][:6]
    else: # accessory: короткий контент, canonical на категорию
        h1=name
        intro=("Это аксессуар к дачному душу и мойке воздуха Fanline. " if fam=="dush" else "Это расходник к мойке воздуха Fanline Aqua. ")+"Подбирается под конкретную модель, актуальные варианты и цены удобно смотреть в каталоге на маркетплейсе."
        title=name+", цена и наличие"
        desc=intro[:155]
        sections=[]; faq=[]
        specs_rows=None
        rel=[{"url":"/"+u+"/","text":n} for u,n in by_fam.get(fam,[])][:4]
    bc2="Климатическая техника"
    schema=build_schema(kind,h1,desc,self_url,faq,bc2,specs_rows)
    out=env.get_template("product.html").render(
        title=title, description=desc, h1=h1, intro=intro, canonical=canonical, self_url=self_url,
        affil=affil, cta_text=F["cta_text"], sections=sections, faq=faq, related=rel, kind=kind,
        specs_rows=specs_rows, schema_json=schema)
    d=os.path.join(ROOT,url); os.makedirs(d,exist_ok=True)
    open(os.path.join(d,"index.html"),"w",encoding="utf-8").write(out)
    return url, (canonical==self_url)

if __name__=="__main__":
    idx=0
    for row in PAGES:
        u,indexable=render(*row)
        if indexable: idx+=1
    print(f"Собрано {len(PAGES)} страниц | self-canonical (в индекс): {idx}")
