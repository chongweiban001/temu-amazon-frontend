"""
Amazon区域配置模块

管理不同国家/地区的Amazon站点配置，包括域名、语言和市场特性。
"""
from typing import Dict, Any, List

# 支持的地区定义
SUPPORTED_REGIONS = {
    # 美国站点 (默认)
    "us": {
        "name": "美国",
        "domain": "amazon.com",
        "language": "en_US",
        "currency": "USD",
        "currency_symbol": "$",
        "review_threshold": 10,  # 最小评论数
        "main_marketplace": True,
        "iso_code": "US",
        "special_features": {
            "seasonal_events": ["感恩节", "黑色星期五", "圣诞节", "超级碗"],
            "preferences": ["轻小件", "高性价比", "功能性强"],
            "regulations": ["FCC认证", "UL认证", "CPC认证"]
        }
    },
    
    # 加拿大站点
    "ca": {
        "name": "加拿大",
        "domain": "amazon.ca",
        "language": "en_CA",
        "currency": "CAD",
        "currency_symbol": "C$",
        "review_threshold": 8,
        "main_marketplace": False,
        "iso_code": "CA",
        "special_features": {
            "seasonal_events": ["加拿大日", "黑色星期五", "拳击节"],
            "preferences": ["实用性", "耐寒", "户外活动"],
            "regulations": ["CSA认证"]
        }
    },
    
    # 英国站点
    "uk": {
        "name": "英国",
        "domain": "amazon.co.uk",
        "language": "en_GB",
        "currency": "GBP",
        "currency_symbol": "£",
        "review_threshold": 10,
        "main_marketplace": True,
        "iso_code": "GB",
        "special_features": {
            "seasonal_events": ["英国夏季银行假日", "黑色星期五", "圣诞节", "拳击节"],
            "preferences": ["品质感", "精致包装", "环保材质"],
            "regulations": ["CE/UKCA认证"]
        }
    },
    
    # 德国站点
    "de": {
        "name": "德国",
        "domain": "amazon.de",
        "language": "de_DE",
        "currency": "EUR",
        "currency_symbol": "€",
        "review_threshold": 8,
        "main_marketplace": True,
        "iso_code": "DE",
        "special_features": {
            "seasonal_events": ["啤酒节", "圣诞市场"],
            "preferences": ["环保认证", "工具类", "高品质"],
            "regulations": ["CE认证", "GS标志"],
            "avoid_packaging": ["过度塑料包装"]
        }
    },
    
    # 法国站点
    "fr": {
        "name": "法国",
        "domain": "amazon.fr",
        "language": "fr_FR",
        "currency": "EUR",
        "currency_symbol": "€",
        "review_threshold": 8,
        "main_marketplace": False,
        "iso_code": "FR",
        "special_features": {
            "seasonal_events": ["法国国庆日", "时尚周"],
            "preferences": ["设计感", "时尚元素", "艺术气息"],
            "regulations": ["CE认证"]
        }
    },
    
    # 意大利站点
    "it": {
        "name": "意大利",
        "domain": "amazon.it",
        "language": "it_IT",
        "currency": "EUR",
        "currency_symbol": "€",
        "review_threshold": 5,
        "main_marketplace": False,
        "iso_code": "IT",
        "special_features": {
            "seasonal_events": ["威尼斯电影节", "米兰时装周"],
            "preferences": ["设计感", "家居类", "厨房用品"],
            "regulations": ["CE认证"]
        }
    },
    
    # 西班牙站点
    "es": {
        "name": "西班牙",
        "domain": "amazon.es",
        "language": "es_ES",
        "currency": "EUR",
        "currency_symbol": "€",
        "review_threshold": 5,
        "main_marketplace": False,
        "iso_code": "ES",
        "special_features": {
            "seasonal_events": ["圣诞彩票", "斗牛节"],
            "preferences": ["休闲用品", "户外活动", "海滩用品"],
            "regulations": ["CE认证"]
        }
    },
    
    # 日本站点
    "jp": {
        "name": "日本",
        "domain": "amazon.co.jp",
        "language": "ja_JP",
        "currency": "JPY",
        "currency_symbol": "¥",
        "review_threshold": 8,
        "main_marketplace": True,
        "iso_code": "JP",
        "special_features": {
            "seasonal_events": ["黄金周", "夏日祭", "御盆节"],
            "preferences": ["精致细分", "包装美观", "微型设计"],
            "regulations": ["PSE认证"]
        }
    },
    
    # 澳大利亚站点
    "au": {
        "name": "澳大利亚",
        "domain": "amazon.com.au",
        "language": "en_AU",
        "currency": "AUD",
        "currency_symbol": "A$",
        "review_threshold": 5,
        "main_marketplace": False,
        "iso_code": "AU",
        "special_features": {
            "seasonal_events": ["澳洲国庆日", "墨尔本杯"],
            "preferences": ["户外用品", "防晒产品", "海滩用品"],
            "regulations": ["RCM标志"]
        }
    },

    # 墨西哥站点
    "mx": {
        "name": "墨西哥",
        "domain": "amazon.com.mx",
        "language": "es_MX",
        "currency": "MXN",
        "currency_symbol": "MX$",
        "review_threshold": 5,  # 最小评论数
        "main_marketplace": False,
        "iso_code": "MX",
        "special_features": {
            "seasonal_events": ["亡灵节", "独立日", "瓜达卢佩圣母日"],
            "preferences": ["色彩鲜艳", "手工艺品", "家庭用品"],
            "payment_methods": ["分期付款选项"]
        }
    },
    
    # 巴西站点
    "br": {
        "name": "巴西",
        "domain": "amazon.com.br",
        "language": "pt_BR",
        "currency": "BRL",
        "currency_symbol": "R$",
        "review_threshold": 5,
        "main_marketplace": False,
        "iso_code": "BR",
        "special_features": {
            "seasonal_events": ["狂欢节", "6月派对", "黑色意识日"],
            "preferences": ["明亮色彩", "户外活动", "足球相关"],
            "payment_methods": ["分期付款选项", "Boleto支付"]
        }
    },
    
    # 印度站点
    "in": {
        "name": "印度",
        "domain": "amazon.in",
        "language": "en_IN",
        "currency": "INR",
        "currency_symbol": "₹",
        "review_threshold": 8,
        "main_marketplace": True,
        "iso_code": "IN",
        "special_features": {
            "seasonal_events": ["排灯节", "胜利节", "洒红节"],
            "preferences": ["低价商品", "COD支付", "色彩鲜艳"],
            "cultural_taboos": ["牛皮制品"],
            "payment_methods": ["货到付款"]
        }
    },
    
    # 阿联酋站点
    "ae": {
        "name": "阿联酋",
        "domain": "amazon.ae",
        "language": "en_AE",
        "currency": "AED",
        "currency_symbol": "د.إ",
        "review_threshold": 5,
        "main_marketplace": True,
        "iso_code": "AE",
        "special_features": {
            "seasonal_events": ["斋月", "开斋节", "朝觐节"],
            "preferences": ["奢侈品外观", "节日装饰", "家庭用品"],
            "cultural_taboos": ["猪肉制品", "酒精饮料"],
            "ramadan_season": [8, 9]  # 伊斯兰历的斋月前月份(公历大约变化)
        }
    },
    
    # 沙特站点
    "sa": {
        "name": "沙特",
        "domain": "amazon.sa",
        "language": "ar_SA",
        "currency": "SAR",
        "currency_symbol": "ر.س",
        "review_threshold": 5,
        "main_marketplace": False,
        "iso_code": "SA",
        "special_features": {
            "seasonal_events": ["斋月", "朝觐节"],
            "preferences": ["家庭用品", "保守设计"],
            "cultural_taboos": ["猪肉制品", "酒精饮料", "暴露服装"],
            "ramadan_season": [8, 9]  # 伊斯兰历的斋月前月份(公历大约变化)
        }
    },
    
    # 新加坡站点
    "sg": {
        "name": "新加坡",
        "domain": "amazon.sg",
        "language": "en_SG",
        "currency": "SGD",
        "currency_symbol": "S$",
        "review_threshold": 5,
        "main_marketplace": False,
        "iso_code": "SG",
        "special_features": {
            "seasonal_events": ["农历新年", "国庆日", "屠妖节"],
            "preferences": ["小型家电", "电子产品", "厨房用品"],
            "regulations": ["IMDA认证"]
        }
    },
    
    # 土耳其站点
    "tr": {
        "name": "土耳其",
        "domain": "amazon.com.tr",
        "language": "tr_TR",
        "currency": "TRY",
        "currency_symbol": "₺",
        "review_threshold": 5,
        "main_marketplace": False,
        "iso_code": "TR",
        "special_features": {
            "seasonal_events": ["开斋节", "牺牲节", "共和国日"],
            "preferences": ["家居用品", "传统元素"],
            "cultural_significance": ["茶具", "地毯", "手工艺品"]
        }
    },
    
    # 荷兰站点
    "nl": {
        "name": "荷兰",
        "domain": "amazon.nl",
        "language": "nl_NL",
        "currency": "EUR",
        "currency_symbol": "€",
        "review_threshold": 5,
        "main_marketplace": False,
        "iso_code": "NL",
        "special_features": {
            "seasonal_events": ["国王日", "圣尼古拉斯节"],
            "preferences": ["自行车配件", "户外活动", "简约设计"],
            "regulations": ["CE认证"]
        }
    }
}

# 每个地区的畅销榜分类路径映射
CATEGORY_PATH_MAPPING = {
    "default": {
        "cell-phones-accessories": "wireless",           # 手机及配件
        "arts-crafts-sewing": "arts-crafts",             # 艺术、工艺与缝纫
        "automotive": "automotive",                      # 汽车用品
        "beauty-personal-care": "beauty-personal-care",  # 美容与个人护理用品
        "home": "home-garden",                           # 家居用品
        "kitchen": "kitchen",                            # 厨房用品
        "office-products": "office-products",            # 办公用品
        "fashion": "fashion",                            # 时尚/服饰
        "beauty": "beauty",                              # 美妆
        "sports-outdoors": "sports-outdoors",            # 运动户外
        "patio-lawn-garden": "lawngarden",               # 露台、草坪和花园
        "pet-supplies": "pet-supplies",                  # 宠物用品
        "tools-home-improvement": "tools"                # 工具和家居装修
    },
    
    # 英国站点 (uk)
    "uk": {
        "cell-phones-accessories": "mobile-phones",      # 手机及配件
        "arts-crafts-sewing": "arts-crafts",             # 艺术、工艺与缝纫
        "automotive": "automotive",                      # 汽车用品
        "beauty-personal-care": "beauty",                # 美容与个人护理用品
        "home": "home-garden",                           # 家居用品
        "kitchen": "kitchen",                            # 厨房用品
        "office-products": "office-products",            # 办公用品
        "fashion": "fashion",                            # 时尚/服饰
        "beauty": "beauty",                              # 美妆
        "sports-outdoors": "sports",                     # 运动户外
        "patio-lawn-garden": "garden",                   # 露台、草坪和花园
        "pet-supplies": "pets",                          # 宠物用品
        "tools-home-improvement": "diy"                  # 工具和家居装修
    },
    
    # 德国站点 (de)
    "de": {
        "cell-phones-accessories": "elektronik-foto",    # 手机及配件
        "arts-crafts-sewing": "kuenste-handwerk",        # 艺术、工艺与缝纫
        "automotive": "auto-motorrad",                   # 汽车用品
        "beauty-personal-care": "beauty",                # 美容与个人护理用品
        "home": "haus-garten",                           # 家居用品
        "kitchen": "kuche-haushalt-wohnen",              # 厨房用品
        "office-products": "burobedarf-schreibwaren",    # 办公用品
        "fashion": "fashion",                            # 时尚/服饰
        "beauty": "drogerie-korperpflege",               # 美妆
        "sports-outdoors": "sport-freizeit",             # 运动户外
        "patio-lawn-garden": "garten",                   # 露台、草坪和花园
        "pet-supplies": "haustier",                      # 宠物用品
        "tools-home-improvement": "baumarkt"             # 工具和家居装修
    },
    
    # 法国站点 (fr)
    "fr": {
        "cell-phones-accessories": "telephonie",         # 手机及配件
        "arts-crafts-sewing": "bricolage",               # 艺术、工艺与缝纫
        "automotive": "auto-moto",                       # 汽车用品
        "beauty-personal-care": "beaute-hygiene-sante",  # 美容与个人护理用品
        "home": "cuisine-maison",                        # 家居用品
        "kitchen": "cuisine",                            # 厨房用品
        "office-products": "fournitures-bureau",         # 办公用品
        "fashion": "mode",                               # 时尚/服饰
        "beauty": "beaute-prestige",                     # 美妆
        "sports-outdoors": "sports-loisirs",             # 运动户外
        "patio-lawn-garden": "jardin",                   # 露台、草坪和花园
        "pet-supplies": "animalerie",                    # 宠物用品
        "tools-home-improvement": "bricolage-outillage"  # 工具和家居装修
    },
    
    # 日本站点 (jp)
    "jp": {
        "cell-phones-accessories": "mobile-phones",      # 手机及配件
        "arts-crafts-sewing": "hobby",                   # 艺术、工艺与缝纫
        "automotive": "automotive",                      # 汽车用品
        "beauty-personal-care": "beauty",                # 美容与个人护理用品
        "home": "kitchen",                               # 家居用品
        "kitchen": "kitchen",                            # 厨房用品
        "office-products": "office-products",            # 办公用品
        "fashion": "fashion",                            # 时尚/服饰
        "beauty": "beauty",                              # 美妆
        "sports-outdoors": "sports",                     # 运动户外
        "patio-lawn-garden": "garden",                   # 露台、草坪和花园
        "pet-supplies": "pet-supplies",                  # 宠物用品
        "tools-home-improvement": "diy"                  # 工具和家居装修
    },
    
    # 加拿大站点 (ca)
    "ca": {
        "cell-phones-accessories": "wireless",           # 手机及配件
        "arts-crafts-sewing": "arts-crafts",             # 艺术、工艺与缝纫
        "automotive": "automotive",                      # 汽车用品
        "beauty-personal-care": "beauty",                # 美容与个人护理用品
        "home": "home-garden",                           # 家居用品
        "kitchen": "kitchen",                            # 厨房用品
        "office-products": "office-products",            # 办公用品
        "fashion": "fashion",                            # 时尚/服饰
        "beauty": "luxury-beauty",                       # 美妆
        "sports-outdoors": "sports",                     # 运动户外
        "patio-lawn-garden": "lawngarden",               # 露台、草坪和花园
        "pet-supplies": "pet-supplies",                  # 宠物用品
        "tools-home-improvement": "tools"                # 工具和家居装修
    },
    
    # 意大利站点 (it)
    "it": {
        "cell-phones-accessories": "elettronica",        # 手机及配件
        "arts-crafts-sewing": "casa-e-cucina",           # 艺术、工艺与缝纫
        "automotive": "auto-e-moto",                     # 汽车用品
        "beauty-personal-care": "bellezza",              # 美容与个人护理用品
        "home": "casa-e-cucina",                         # 家居用品
        "kitchen": "casa-e-cucina",                      # 厨房用品
        "office-products": "cancelleria",                # 办公用品
        "fashion": "moda",                               # 时尚/服饰
        "beauty": "bellezza",                            # 美妆
        "sports-outdoors": "sport-e-tempo-libero",       # 运动户外
        "patio-lawn-garden": "giardino-giardinaggio",    # 露台、草坪和花园
        "pet-supplies": "animali",                       # 宠物用品
        "tools-home-improvement": "fai-da-te"            # 工具和家居装修
    },
    
    # 西班牙站点 (es)
    "es": {
        "cell-phones-accessories": "electronica",        # 手机及配件
        "arts-crafts-sewing": "hogar",                   # 艺术、工艺与缝纫
        "automotive": "coche-moto",                      # 汽车用品
        "beauty-personal-care": "belleza",               # 美容与个人护理用品
        "home": "hogar",                                 # 家居用品
        "kitchen": "hogar-cocina",                       # 厨房用品
        "office-products": "oficina",                    # 办公用品
        "fashion": "moda",                               # 时尚/服饰
        "beauty": "belleza",                             # 美妆
        "sports-outdoors": "deportes",                   # 运动户外
        "patio-lawn-garden": "jardin",                   # 露台、草坪和花园
        "pet-supplies": "mascotas",                      # 宠物用品
        "tools-home-improvement": "bricolaje"            # 工具和家居装修
    },
    
    # 印度站点 (in)
    "in": {
        "cell-phones-accessories": "electronics",        # 手机及配件
        "arts-crafts-sewing": "arts-crafts",             # 艺术、工艺与缝纫
        "automotive": "automotive",                      # 汽车用品
        "beauty-personal-care": "beauty",                # 美容与个人护理用品
        "home": "home-kitchen",                          # 家居用品
        "kitchen": "kitchen",                            # 厨房用品
        "office-products": "office-products",            # 办公用品
        "fashion": "fashion",                            # 时尚/服饰
        "beauty": "beauty",                              # 美妆
        "sports-outdoors": "sports",                     # 运动户外
        "patio-lawn-garden": "lawngarden",               # 露台、草坪和花园
        "pet-supplies": "pets",                          # 宠物用品
        "tools-home-improvement": "home-improvement"     # 工具和家居装修
    },
    
    # 阿联酋站点 (ae)
    "ae": {
        "cell-phones-accessories": "electronics-mobiles", # 手机及配件
        "arts-crafts-sewing": "arts-crafts",             # 艺术、工艺与缝纫
        "automotive": "automotive",                      # 汽车用品
        "beauty-personal-care": "beauty",                # 美容与个人护理用品
        "home": "home",                                  # 家居用品
        "kitchen": "kitchen",                            # 厨房用品
        "office-products": "office-products",            # 办公用品
        "fashion": "fashion",                            # 时尚/服饰
        "beauty": "beauty",                              # 美妆
        "sports-outdoors": "sports",                     # 运动户外
        "patio-lawn-garden": "garden",                   # 露台、草坪和花园
        "pet-supplies": "pet-supplies",                  # 宠物用品
        "tools-home-improvement": "tools"                # 工具和家居装修
    },
    
    # 沙特站点 (sa)
    "sa": {
        "cell-phones-accessories": "electronics-mobiles", # 手机及配件
        "arts-crafts-sewing": "arts-crafts",             # 艺术、工艺与缝纫
        "automotive": "automotive",                      # 汽车用品
        "beauty-personal-care": "beauty",                # 美容与个人护理用品
        "home": "home",                                  # 家居用品
        "kitchen": "kitchen",                            # 厨房用品
        "office-products": "office-products",            # 办公用品
        "fashion": "fashion",                            # 时尚/服饰
        "beauty": "beauty",                              # 美妆
        "sports-outdoors": "sports",                     # 运动户外
        "patio-lawn-garden": "garden",                   # 露台、草坪和花园
        "pet-supplies": "pet-supplies",                  # 宠物用品
        "tools-home-improvement": "tools"                # 工具和家居装修
    },
    
    # 墨西哥站点 (mx)
    "mx": {
        "cell-phones-accessories": "electronics",        # 手机及配件
        "arts-crafts-sewing": "arts-crafts",             # 艺术、工艺与缝纫
        "automotive": "automotive",                      # 汽车用品
        "beauty-personal-care": "beauty",                # 美容与个人护理用品
        "home": "home",                                  # 家居用品
        "kitchen": "kitchen",                            # 厨房用品
        "office-products": "office-products",            # 办公用品
        "fashion": "fashion",                            # 时尚/服饰
        "beauty": "beauty",                              # 美妆
        "sports-outdoors": "sports",                     # 运动户外
        "patio-lawn-garden": "lawn-garden",              # 露台、草坪和花园
        "pet-supplies": "pet-supplies",                  # 宠物用品
        "tools-home-improvement": "tools"                # 工具和家居装修
    },
    
    # 巴西站点 (br)
    "br": {
        "cell-phones-accessories": "celulares-comunicacao", # 手机及配件
        "arts-crafts-sewing": "papelaria",               # 艺术、工艺与缝纫
        "automotive": "automotivos",                     # 汽车用品
        "beauty-personal-care": "beleza",                # 美容与个人护理用品
        "home": "casa",                                  # 家居用品
        "kitchen": "cozinha",                            # 厨房用品
        "office-products": "papelaria",                  # 办公用品
        "fashion": "moda",                               # 时尚/服饰
        "beauty": "beleza",                              # 美妆
        "sports-outdoors": "esportes",                   # 运动户外
        "patio-lawn-garden": "jardim",                   # 露台、草坪和花园
        "pet-supplies": "pet-shop",                      # 宠物用品
        "tools-home-improvement": "ferramentas"          # 工具和家居装修
    },
    
    # 澳大利亚站点 (au)
    "au": {
        "cell-phones-accessories": "electronics",        # 手机及配件
        "arts-crafts-sewing": "arts-crafts",             # 艺术、工艺与缝纫
        "automotive": "automotive",                      # 汽车用品
        "beauty-personal-care": "beauty",                # 美容与个人护理用品
        "home": "home",                                  # 家居用品
        "kitchen": "kitchen",                            # 厨房用品
        "office-products": "office-products",            # 办公用品
        "fashion": "fashion",                            # 时尚/服饰
        "beauty": "beauty",                              # 美妆
        "sports-outdoors": "sports",                     # 运动户外
        "patio-lawn-garden": "garden",                   # 露台、草坪和花园
        "pet-supplies": "pet-supplies",                  # 宠物用品
        "tools-home-improvement": "home-improvement"     # 工具和家居装修
    },
    
    # 新加坡站点 (sg)
    "sg": {
        "cell-phones-accessories": "electronics",        # 手机及配件
        "arts-crafts-sewing": "arts-crafts",             # 艺术、工艺与缝纫
        "automotive": "automotive",                      # 汽车用品
        "beauty-personal-care": "beauty",                # 美容与个人护理用品
        "home": "home",                                  # 家居用品
        "kitchen": "kitchen",                            # 厨房用品
        "office-products": "office-products",            # 办公用品
        "fashion": "fashion",                            # 时尚/服饰
        "beauty": "beauty",                              # 美妆
        "sports-outdoors": "sports",                     # 运动户外
        "patio-lawn-garden": "garden",                   # 露台、草坪和花园
        "pet-supplies": "pet-supplies",                  # 宠物用品
        "tools-home-improvement": "tools"                # 工具和家居装修
    },
    
    # 土耳其站点 (tr)
    "tr": {
        "cell-phones-accessories": "elektronik",         # 手机及配件
        "arts-crafts-sewing": "ev-yasam",                # 艺术、工艺与缝纫
        "automotive": "otomotiv",                        # 汽车用品
        "beauty-personal-care": "kisisel-bakim",         # 美容与个人护理用品
        "home": "ev-yasam",                              # 家居用品
        "kitchen": "mutfak",                             # 厨房用品
        "office-products": "ofis-urunleri",              # 办公用品
        "fashion": "moda",                               # 时尚/服饰
        "beauty": "guzellik",                            # 美妆
        "sports-outdoors": "spor",                       # 运动户外
        "patio-lawn-garden": "bahce",                    # 露台、草坪和花园
        "pet-supplies": "evcil-hayvanlar",               # 宠物用品
        "tools-home-improvement": "yapi-market"          # 工具和家居装修
    },
    
    # 荷兰站点 (nl)
    "nl": {
        "cell-phones-accessories": "elektronica",        # 手机及配件
        "arts-crafts-sewing": "knutselen-handwerk",      # 艺术、工艺与缝纫
        "automotive": "auto-motor",                      # 汽车用品
        "beauty-personal-care": "beauty",                # 美容与个人护理用品
        "home": "huis-keuken",                           # 家居用品
        "kitchen": "keuken",                             # 厨房用品
        "office-products": "kantoorartikelen",           # 办公用品
        "fashion": "mode",                               # 时尚/服饰
        "beauty": "beauty",                              # 美妆
        "sports-outdoors": "sport",                      # 运动户外
        "patio-lawn-garden": "tuin",                     # 露台、草坪和花园
        "pet-supplies": "huisdieren",                    # 宠物用品
        "tools-home-improvement": "klussen"              # 工具和家居装修
    }
}

# 地区排序 - 按照重要性和市场规模
TOP_REGIONS = ["us", "uk", "de", "jp", "ca", "fr", "in", "ae", "br", "mx"]

def get_region_config(region_code: str) -> Dict[str, Any]:
    """
    获取指定地区的配置信息
    
    参数:
        region_code: 地区代码 (如 'us', 'uk', 'de')
        
    返回:
        地区配置字典，如果未找到则返回美国站点配置
    """
    if region_code.lower() in SUPPORTED_REGIONS:
        return SUPPORTED_REGIONS[region_code.lower()]
    return SUPPORTED_REGIONS["us"]  # 默认返回美国站点配置

def get_domain(region_code: str) -> str:
    """
    获取指定地区的Amazon域名
    
    参数:
        region_code: 地区代码
        
    返回:
        完整的域名（如 'amazon.com'）
    """
    region = get_region_config(region_code)
    return region["domain"]

def get_base_url(region_code: str) -> str:
    """
    获取指定地区的Amazon基础URL
    
    参数:
        region_code: 地区代码
        
    返回:
        基础URL（如 'https://www.amazon.com'）
    """
    return f"https://www.{get_domain(region_code)}"

def get_category_path(region_code: str, category: str) -> str:
    """
    获取指定地区和类别的路径
    
    参数:
        region_code: 地区代码
        category: 类别名称
        
    返回:
        类别路径
    """
    # 检查是否有地区特定的映射
    if region_code in CATEGORY_PATH_MAPPING:
        mapping = CATEGORY_PATH_MAPPING[region_code]
    else:
        mapping = CATEGORY_PATH_MAPPING["default"]
    
    # 检查类别是否存在，否则返回electronics作为默认值
    if category in mapping:
        return mapping[category]
    return mapping.get("electronics", "electronics")

def get_search_url(region_code: str, query: str, page: int = 1) -> str:
    """
    构建搜索URL
    
    参数:
        region_code: 地区代码
        query: 搜索查询词
        page: 页码
        
    返回:
        完整的搜索URL
    """
    base_url = get_base_url(region_code)
    encoded_query = query.replace(' ', '+')
    
    return f"{base_url}/s?k={encoded_query}&page={page}"

def get_product_url(region_code: str, asin: str) -> str:
    """
    构建产品详情页URL
    
    参数:
        region_code: 地区代码
        asin: 产品ASIN码
        
    返回:
        完整的产品详情页URL
    """
    base_url = get_base_url(region_code)
    return f"{base_url}/dp/{asin}/"

def get_best_sellers_url(region_code: str, category: str) -> str:
    """
    构建畅销榜URL
    
    参数:
        region_code: 地区代码
        category: 类别名称
        
    返回:
        完整的畅销榜URL
    """
    base_url = get_base_url(region_code)
    category_path = get_category_path(region_code, category)
    
    # 日本站点和其他一些站点有特殊格式
    if region_code == "jp":
        return f"{base_url}/gp/bestsellers/{category_path}/ref=zg_bs_nav_0"
    
    # 通用格式
    return f"{base_url}/Best-Sellers-{category_path.capitalize()}/zgbs/{category_path}/ref=zg_bs_nav_0"

def get_movers_shakers_url(region_code: str, category: str) -> str:
    """
    构建涨幅榜URL
    
    参数:
        region_code: 地区代码
        category: 类别名称
        
    返回:
        完整的涨幅榜URL
    """
    base_url = get_base_url(region_code)
    category_path = get_category_path(region_code, category)
    
    return f"{base_url}/gp/movers-and-shakers/{category_path}/ref=zg_bs_tab"

def get_new_releases_url(region_code: str, category: str) -> str:
    """
    构建新品榜URL
    
    参数:
        region_code: 地区代码
        category: 类别名称
        
    返回:
        完整的新品榜URL
    """
    base_url = get_base_url(region_code)
    category_path = get_category_path(region_code, category)
    
    return f"{base_url}/gp/new-releases/{category_path}/ref=zg_bs_tab"

def get_outlet_url(region_code: str, category: str) -> str:
    """
    构建折扣商品URL
    
    参数:
        region_code: 地区代码
        category: 类别名称
        
    返回:
        完整的折扣商品URL
    """
    base_url = get_base_url(region_code)
    category_path = get_category_path(region_code, category)
    
    # 某些地区可能没有Outlet页面，这里使用通用格式
    return f"{base_url}/s?i=outlet&rh=n%3A{category_path}"

def get_warehouse_url(region_code: str, category: str) -> str:
    """
    构建二手商品URL
    
    参数:
        region_code: 地区代码
        category: 类别名称
        
    返回:
        完整的二手商品URL
    """
    base_url = get_base_url(region_code)
    category_path = get_category_path(region_code, category)
    
    return f"{base_url}/s?i=warehouse-deals&rh=n%3A{category_path}"

def get_language_header(region_code: str) -> str:
    """
    获取适合该地区的语言请求头
    
    参数:
        region_code: 地区代码
        
    返回:
        语言请求头值
    """
    region = get_region_config(region_code)
    lang_code = region["language"].split('_')[0]
    
    # 返回主要语言和英语作为备选
    if lang_code == "en":
        return f"{region['language']},en;q=0.9"
    return f"{region['language']},{lang_code};q=0.9,en;q=0.8"

def format_price(price: float, region_code: str) -> str:
    """
    格式化价格显示
    
    参数:
        price: 价格数值
        region_code: 地区代码
        
    返回:
        格式化的价格字符串
    """
    if price is None:
        return ""
        
    region = get_region_config(region_code)
    symbol = region["currency_symbol"]
    
    # 日元等不使用小数点的货币
    if region["currency"] == "JPY":
        return f"{symbol}{int(price):,}"
    
    # 标准格式化
    return f"{symbol}{price:,.2f}"

def get_region_special_features(region_code: str) -> Dict[str, Any]:
    """
    获取区域特殊特性（文化、法规等）
    
    参数:
        region_code: 地区代码
        
    返回:
        特殊特性字典
    """
    region = get_region_config(region_code)
    return region.get("special_features", {})

def is_ramadan_season(region_code: str, current_month: int = None) -> bool:
    """
    判断当前是否是指定地区的斋月季节
    
    参数:
        region_code: 地区代码
        current_month: 当前月份，默认为None（使用系统当前月份）
        
    返回:
        是否是斋月季节
    """
    import datetime
    
    if current_month is None:
        current_month = datetime.datetime.now().month
        
    special_features = get_region_special_features(region_code)
    ramadan_months = special_features.get("ramadan_season", [])
    
    return current_month in ramadan_months

def get_region_taboos(region_code: str) -> List[str]:
    """
    获取区域文化禁忌产品列表
    
    参数:
        region_code: 地区代码
        
    返回:
        文化禁忌产品列表
    """
    special_features = get_region_special_features(region_code)
    return special_features.get("cultural_taboos", [])

def get_region_specific_regulations(region_code: str) -> List[str]:
    """
    获取区域特定法规要求
    
    参数:
        region_code: 地区代码
        
    返回:
        法规要求列表
    """
    special_features = get_region_special_features(region_code)
    return special_features.get("regulations", [])

def get_region_payment_methods(region_code: str) -> List[str]:
    """
    获取区域特殊支付方式
    
    参数:
        region_code: 地区代码
        
    返回:
        特殊支付方式列表
    """
    special_features = get_region_special_features(region_code)
    return special_features.get("payment_methods", [])

def get_region_events(region_code: str) -> List[str]:
    """
    获取区域特殊节日/活动
    
    参数:
        region_code: 地区代码
        
    返回:
        节日/活动列表
    """
    special_features = get_region_special_features(region_code)
    return special_features.get("seasonal_events", [])

def get_all_supported_regions() -> List[Dict[str, Any]]:
    """
    获取所有支持的区域信息列表
    
    返回:
        区域信息列表
    """
    regions_list = []
    for code, details in SUPPORTED_REGIONS.items():
        regions_list.append({
            "code": code,
            "name": details["name"],
            "domain": details["domain"],
            "currency": details["currency"],
            "main_marketplace": details["main_marketplace"]
        })
    return regions_list 