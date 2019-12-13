# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal
import random
from . import controllers
import os
from odoo import fields, api, SUPERUSER_ID, exceptions
from odoo.addons.accountcore import models
from odoo.addons.accountcore import wizard
from odoo.addons.accountcore import report
from odoo.addons.accountcore.models.ac_obj import ACTools
from odoo.addons.accountcore.models.ac_period import Period, VoucherPeriod
from odoo.exceptions import UserError


# 是否执行卸载模块函数
ac_do_uninstall = False
# 安装模块时执行
# csv格式的文件的完全路径
org_csv_path = os.path.join(
    os.path.dirname(__file__)+"/demo/begin/orgs.csv")
accounts_csv_path = os.path.join(
    os.path.dirname(__file__)+"/data/accounts.csv")
items_csv_path = os.path.join(
    os.path.dirname(__file__)+"/demo/begin/items.csv")


def _load(cr, registry):
    '''加载用于演示的明细科目,期初和凭证等,模块安装后执行'''
    env = api.Environment(cr, SUPERUSER_ID, {})

    # 启为核算项目类别前n个项目添加期初
    itemclassesDict = {}
    with open(items_csv_path, mode='rb') as f:
        itemclass = ACTools.readCsvFile(f, True)
    for i in itemclass:
        one = {i[0]: int(i[1])}
        itemclassesDict.update(one)

    # 机构名称,用于产生期初和凭证
    org_names = []
    with open(org_csv_path, mode='rb') as f:
        orgs = ACTools.readCsvFile(f, True)
        for org in orgs:
            org_names.append(org[0])
    # 明细科目
    accounts = []
    with open(accounts_csv_path, mode='rb') as f:
        accounts = ACTools.readCsvFile(f, True)
    # 添加明细科目和科目关联的核算项目
    add_accounts(env, accounts)
    # 添加启用期初
    add_beginData(env, org_names, itemclassesDict)
    # 添加凭证
    add_vouchers(env)


# 卸载模块时执行
def _uninstall(cr, registry):
    '''卸载演示模块,删除凭证数据'''
    if not ac_do_uninstall:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    # 删除全部凭证
    t_voucher = env['accountcore.voucher'].sudo()
    vouchers = t_voucher.search([])
    if vouchers.exists():
        vouchers.write({'state': 'creating', 'reviewer': None})
    vouchers.unlink()
    # 再次清空科目余额表
    t_balance = env['accountcore.accounts_balance'].sudo()
    t_balance.search([])
    t_balance.unlink()
    # 删除全部核算统计项目
    t_items = env['accountcore.item'].sudo()
    t_items.search([])
    t_items.unlink()
    # 全局标签：演示数据
    modelName = os.path.basename(os.path.dirname(__file__))
    glob_tag_id = env.ref(modelName+'.glob_tag_1').id
    # 删除带演示标签的会计科目
    t_account = env['accountcore.account'].sudo()
    accounts = t_account.search([('glob_tag', 'in', glob_tag_id)])
    accounts.unlink()

# 添加科目


def add_accounts(env, rows):
    '''添加明细科目'''
    # 全局标签：演示数据的外部标识.glob_tag_1
    modelName = os.path.basename(os.path.dirname(__file__))
    glob_tag_id = env.ref(modelName+'.glob_tag_1').id
    # 科目表
    t_account = env['accountcore.account'].sudo()
    t_itemClass = env['accountcore.itemclass'].sudo()
    # 添加明细科目和核算项目-开始
    errorRows = []
    for row in rows:
        father = getObjByName(t_account, row[0])
        if father:
            itemclassName = row[3].split("/")
            ids = []
            id_ = False
            for itemName in itemclassName:
                itemClass = getObjByName(t_itemClass, itemName)
                if itemClass:
                    ids.append(itemClass.id)
            if row[2]:
                accountItemClass = getObjByName(t_itemClass, row[2])
                if accountItemClass:
                    id_ = accountItemClass.id
                    ids.append(id_)
            newAccount = None
            if row[1] and len(row[1]) > 0:
                newAccount = add_account(glob_tag_id,
                                         t_account,
                                         father,
                                         row[1],
                                         itemClasses_ids=ids,
                                         accountItemClass_id=id_)
            else:
                # 没有指定科目,添加核算项目到father科目
                newAccount = add_items(father, ids, id_)
            if not newAccount:
                errorRows.append(row)
        else:
            errorRows.append(row)
    if len(errorRows) > 0:
        rl = ['_'.join(e) for e in errorRows]
        raise UserError('以下科目出错,不能完成任务,可能是因为没有上级科目,重复导入或已经存在\n'+'\n'.join(rl))
        # 添加明细科目和核算项目-结束

        # 添加期初记录


def add_beginData(env, org_names=[], itemclasses={}):
    '''添加启用期初'''
    # 取安装当天为启用期初
    date = fields.Date.today()
    date_str = date.strftime('%Y-%m-%d')
    year = date.year
    month = date.month

    t_balance = env['accountcore.accounts_balance'].sudo()
    t_account = env['accountcore.account'].sudo()
    # 要添加期初的机构ID列表
    org_ids = env['accountcore.org'].sudo().search(
        [('name', 'in', org_names)]).mapped('id')
    # 期初
    qichus = []
    all_accounts = t_account.search([('id', '!=', 0)])
    for account in all_accounts:
        if account.childs_ids:
            continue
        if account.accountItemClass:
            # 科目的必选核算项目类别名称
            name_key = account.accountItemClass.name
            print(name_key)
            # 取该核算项目类别的前n个项目
            value_n = itemclasses.get(name_key)
            print(value_n)
            if value_n:
                item_ids = (env['accountcore.item'].sudo().search(
                    [('itemClass', '=', account.accountItemClass.id)], limit=value_n)).mapped('id')
                for org_id in org_ids:
                    for item_id in item_ids:
                        qichus.append(buildOneBalance(
                            org_id, account, date_str, year, month, item_id))
        else:
            for org_id in org_ids:
                qichus.append(buildOneBalance(
                    org_id, account, date_str, year, month))

    # 添加启用期初
    for q in qichus:
        t_balance.create(q)


# 添加记账凭证
def add_vouchers(env):
    '''添加会计凭证'''
    # t_voucher.create({})


def add_items(account, itemClasses_ids=[], accountItemClass_id=False):
    '''为科目添加核算统计项目'''
    if accountItemClass_id:
        if account.isUsedInBalance():
            if account.accountItemClass.id == accountItemClass_id:
                return account
            else:
                return None
    account.write({'itemClasses':  [(6, 0, itemClasses_ids)],
                   'accountItemClass': accountItemClass_id, })
    return account


def add_account(glob_tag_id, t_account, father,  name, org_id=False,  itemClasses_ids=[], accountItemClass_id=False):
    '''添加一个科目'''
    accountName = father.name+'---'+name
    old_account = t_account.search([('name', '=', accountName)])
    if old_account.exists():
        return None
    account = t_account.create({'org': org_id,
                                'accountsArch': father.accountsArch.id,
                                'accountClass': father.accountClass.id,
                                'number': father.number + '.' + str(father.currentChildNumber),
                                'name': accountName,
                                'direction': father.direction,
                                'cashFlowControl': father.cashFlowControl,
                                'itemClasses':  [(6, 0, itemClasses_ids)],
                                'accountItemClass': accountItemClass_id,
                                'fatherAccountId': father.id,
                                'glob_tag': [(6, 0, [glob_tag_id])],
                                })
    father.currentChildNumber = father.currentChildNumber+1
    return account


def getObjByName(t, name):
    '''根据名称获得对象'''
    obj = t.search([('name', '=', name)], limit=1)
    return obj


def buildOneBalance(org_id, account,  date_str, year, month, item_id=False):
    '''创建一条期初'''
    if account.direction == '1':
        beginingDamount = ACTools.TranslateToDecimal(random.random()*30000)
        beginingCamount = 0
    else:
        beginingDamount = 0
        beginingCamount = ACTools.TranslateToDecimal(random.random()*30000)
    damount = ACTools.TranslateToDecimal(random.random()*30000)
    camount = ACTools.TranslateToDecimal(random.random()*30000)
    if month == 1:
        beginCumulativeDamount = 0
        beginCumulativeCamount = 0
    elif account.accountClass.name == '损益类':
        # 损益类借贷方累计发生额一般相等
        beginCumulativeDamount = ACTools.TranslateToDecimal(
            random.random()*30000)
        beginCumulativeCamount = beginCumulativeDamount
    else:
        beginCumulativeDamount = ACTools.TranslateToDecimal(
            random.random()*30000)
        beginCumulativeCamount = ACTools.TranslateToDecimal(
            random.random()*30000)

    b = {'org': org_id,
         'createDate': date_str,
         'year': year,
         'month': month,
         'account': account.id,
         'items': item_id,
         'beginingDamount': beginingDamount,
         'beginingCamount': beginingCamount,
         'damount': damount,
         'camount': camount,
         'beginCumulativeCamount': beginCumulativeCamount,
         'beginCumulativeDamount': beginCumulativeDamount,
         'isbegining': True},
    return b
