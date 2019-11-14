# -*- coding: utf-8 -*-
{
    'name': "小规模核算方案",

    'summary': """
        AccountCore模块的小规模纳税人核算方案。安装Accourcore后，安装该模块，
        卸载该模块,需要手动删除加载的科目，核算项目，报表等数据""",

    'description': """
        在AccountCore模块的预设科目上，添加适合小规模纳税人的明细科目，核算项目，相关会计报表等。
        注意：解决方案之间可能有冲突
    """,
    'author': "黄虎",
    'website': "http://www.baidu.com",
    'category': 'accountcore/solution',
    'version': '0.1',
    'depends': ['accountcore'],
    'application': False,
    'auto_install': False,
    'images': ['static/description/icon.png'],
    'data': [
        'data/glob_tag.xml',
        'data/users.xml',
        'data/org.xml',
        'data/items_wang_lai.xml',
        'data/items_bu_men.xml',
        'data/items_yuan_gong.xml',
        'data/items_yuan_cai_liao.xml',
        'data/items_ku_cun_shang_pin.xml',
        'data/items_yuan_cai_liao.xml',
        'data/items_yuan_cai_liao.xml',
        'data/items_cheng_ben_fei_yong.xml',
        'data/items_di_zhi_yi_hao.xml',
        'data/items_gu_ding_zi_chan.xml',
        'data/items_wu_xing_zi_chan.xml',
        'data/items_cheng_ben_dui_xiang.xml',
        'data/items_zai_jian_gong_chen.xml',
        'data/items_zhou_zhuan_cai_liao.xml',
        'data/report_model.xml',
    ],
    'demo': [
        'demo/glob_tag.xml',
        'demo/users.xml',
        'demo/org.xml',
        'demo/items_wang_lai.xml',
        'demo/items_bu_men.xml',
        'demo/items_yuan_gong.xml',
        'demo/items_yuan_cai_liao.xml',
        'demo/items_ku_cun_shang_pin.xml',
        'demo/items_yuan_cai_liao.xml',
        'demo/items_yuan_cai_liao.xml',
        'demo/items_cheng_ben_fei_yong.xml',
        'demo/items_di_zhi_yi_hao.xml',
        'demo/items_gu_ding_zi_chan.xml',
        'demo/items_wu_xing_zi_chan.xml',
        'demo/items_cheng_ben_dui_xiang.xml',
        'demo/items_zai_jian_gong_chen.xml',
        'demo/items_zhou_zhuan_cai_liao.xml',
        'demo/report_model.xml',
    ],
    'post_init_hook': '_load',
    'uninstall_hook': '_uninstall',
}