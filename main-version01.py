#coding=utf-8
from DBConnectionPool import pool

import numpy as np
import matplotlib.pyplot as plt
import numpy as np

import ConfigManager
from Logger_module import logger
import psycopg2
import pandas as pd

#from parse import *
from dateutil.parser import *
#from dateutil import parse
# 连接数据库
def connect_db():
    try:
        DBconfig_parameter = ConfigManager.ConfigPara  # 从配置文件DBconfig中读取参数
        conn = psycopg2.connect(database = DBconfig_parameter.database_name,
                                user = DBconfig_parameter.database_user_name,
                                password = DBconfig_parameter.database_password,
                                host = DBconfig_parameter.database_host,
                                port = DBconfig_parameter.database_port)
    except Exception as e:
        logger.error(e)
    else:
        return conn
    return None

# 将数据插入到数据库表中
def insert_data_to_order_line_source(csv_path,database_connection):
    csv_file = pd.read_csv(csv_path, keep_default_na=False, encoding='utf-8')
    sql_sentence_order_line ='insert into layer4_solution.order_line(order_info_id,item_id,quantity,created_timestamp) values (%s,%s,%s,%s);'
    cur = database_connection.cursor()
    for index, row in csv_file.iterrows():
        cur.executemany(sql_sentence_order_line, [(int(row.outer_code), row.material, row.quantity, parse(row.time))])
    database_connection.commit()

def insert_data_to_order_line_source1(csv_path,database_connection):
    csv_file = pd.read_csv(csv_path, keep_default_na=False, encoding='utf-8')
    sql_sentence_order_line ='insert into layer4_solution.order_line_source(order_info_id,item_id,quantity,created_timestamp,cut_off_time,k_point,region) values (%s,%s,%s,%s,%s,%s,%s);'
    cur = database_connection.cursor()
    for index, row in csv_file.iterrows():
        cur.executemany(sql_sentence_order_line, [(int(row.outer_code), row.material, row.quantity, parse(row.time), parse(row.cut_off_time), row.k_point,row.region)])
    database_connection.commit()


def insert_data_to_item(csv_path,database_connection):
    csv_file = pd.read_csv(csv_path, keep_default_na=False, encoding='utf-8')
    sql_sentence_order_line ='insert into layer3_sku.basic_iteam(id,length,width,height,weight,storagee,hits,quantity,med_cubing,best_cubing,storage_type) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
    cur = database_connection.cursor()
    for index, row in csv_file.iterrows():
        cur.executemany(sql_sentence_order_line, [(row.item, row.DimA,row.DimB, row.DimC, row.Weight,row.storage, row.Hits,row.Quantity,row.med_cubing,row.best_cubing,row.storagetype)])
    database_connection.commit()

##############计算分配后容量是否满足要求##################
def CalStorage(hits,HitsThreshold,med_cubing,best_cubing,storage):
    #############判断容量是否满足要求######
    SingleSku_pallet_no = 0
    MultipSku_pallet_no = 0
    print(1)
    for i in range(0, len(hits)):
        if hits[i] >= HitsThreshold or med_cubing[i] == 0.001:
            ####纯放#########
            # storage
            if storage[i] >= best_cubing[i]:
                SingleSku_pallet_no += (int(storage[i] / best_cubing[i]))
                # print(SingleSku_pallet_no)
            else:
                SingleSku_pallet_no += 1
        else:
            if storage[i] >= med_cubing[i]:
                #MultipSku_pallet_no += (int(storage[i] / med_cubing[i]))
                MultipSku_pallet_no += (int((storage[i] / med_cubing[i]) / 2))
                # print(MultipSku_pallet_no)
            else:
                MultipSku_pallet_no += 1
    print("纯放SKU需要的pallet数量：%d" % SingleSku_pallet_no)
    print("混放SKU需要的pallet数量：%d" % MultipSku_pallet_no)
    print("总需pallet数量：%d" % (SingleSku_pallet_no + MultipSku_pallet_no))
    if SingleSku_pallet_no + MultipSku_pallet_no < PalletNumber:
        print("could be assignmented！！！！")
    else:
        print("could not be assignmented!!!")

#######################计算订单中混放和纯放的比值###############
def Cal_SingleandMix_Rate(OrderItem,Itemid,hits,HitsThreshold):
    RateList = []
    for j in range(0, len(OrderItem)):
        for k in range(0, len(Itemid)):
            if OrderItem[j] == Itemid[k]:
                if hits[k] >= HitsThreshold:
                    RateList.append(0)
                    # print(0)
                    # a += 1
                else:
                    RateList.append(1)
                    # print(1)
                    # b += 1
            else:
                # RateList.append(2)
                continue
    count = 0  # 混拣数
    for k in RateList:
        count += k
    print(len(RateList))
    print(len(OrderItem))
    print(len(Itemid))
    print(count)
    rate = int(((len(RateList) - count) / len(RateList))*100)
    print("订单纯拣货比例为：%d" %rate)
    return rate

if __name__ == "__main__":

    #connect_db()
    try:
        ###########连接数据库####################
        #database_connection = pool.get_connection()
        database_connection =  connect_db()
        database_cursor = database_connection.cursor()
        ###########初始化数据库####################
        #insert_data_to_order_line_source1("D:\work\suning\suning_double11order.csv",database_connection)
        #insert_data_to_item("D:\work\suning\suning_item_basicdata-0801.csv",database_connection)
        hits = []              #频次
        #region = []            #picking区域
        storage = []           #库存

        med_cubing = []        #半箱
        best_cubing = []       #整箱
        cubing3 = []
        cubing4 = []
        cubing5 = []
        cubing6 = []
        dateSegment = [0.1,0.2,0.3,0.4] #10%有一个日期 20%有两个日期 30%有三个日期 40%有4个日
        percentage = 0.04      #阈值百分比
        HitsThreshold = 0       # 频次分割阈值

        SkuNumber = [1,2,3,4,5,6]      # 一个pallet所能放置的种类数组
        HitsPercentageList = [0.01,0.03,0.07,0.1,0.3]         # hits阈值分割比例区间
        HitsThresholdList = []           # hits阈值分割区间

        PalletNumber = 28392   #托盘容量
        SingleSku_pallet_no = 0 #纯放的托盘容量_
        MultipSku_pallet_no = 0 #混放置托盘容量

        #######频次#####
        sql = "select hits from layer3_sku.basic_iteam where storagee <> 0 and storage_type = 0 order by hits desc "
        database_cursor.execute(sql)
        hitsdata = database_cursor.fetchall()
        for h in hitsdata:
            hits.append(h[0])
        #print(hits)

        ####################库存######################
        sql = "select storagee from layer3_sku.basic_iteam where storagee <> 0 and storage_type = 0 order by hits desc"
        database_cursor.execute(sql)
        storagedata = database_cursor.fetchall()
        for s in storagedata:
            storage.append(s[0])
        #print(storage)
        #######################半箱###############
        sql = "select med_cubing from layer3_sku.basic_iteam where storagee <> 0 and storage_type = 0 order by hits desc"
        database_cursor.execute(sql)
        mcubdata = database_cursor.fetchall()
        for m in mcubdata:
            med_cubing.append(m[0])
        #print(med_cubing)

        #######################整箱############
        sql = "select best_cubing from layer3_sku.basic_iteam where storagee <> 0 and storage_type = 0 order by hits desc"
        database_cursor.execute(sql)
        bcubdata = database_cursor.fetchall()
        for b in bcubdata:
            best_cubing.append(b[0])
        #print(best_cubing)
        
        ############分为最多6个slot情况下的cubing值###############
        for c in range(0,len(best_cubing)):
            cubing3.append(int(best_cubing[c]/3))
            cubing4.append(int(best_cubing[c]/4))
            cubing5.append(int(best_cubing[c]/5))
            cubing6.append(int(best_cubing[c]/6))
        print(len(cubing6))
        #######################hits阈值############
        '''
        #HitsThreshold = hits[int(len(hits) * percentage)]
        #print(len(hits))    #不等于0 hits 的个数
        #print("hits阈值为:%d"%HitsThreshold)
        '''
        #for k in HitsPercentageList:
            #HitsThresholdList.append(hits[int(len(hits) * k)])
        #print(HitsThresholdList)
   
        ############# #item信息#############
        Itemid = []
        sql = "select id from layer3_sku.basic_iteam where storagee <> 0 and storage_type = 0  order by hits desc"
        database_cursor.execute(sql)
        iddata = database_cursor.fetchall()
        for i in iddata:
            Itemid.append(i[0])
        #print(Itemid)
        ##################### 订单信息#################
        OrderItem = []  # 订单信息
        sql = "select item_id from layer4_solution.order_line_source where region = 0 "
        database_cursor.execute(sql)
        Itemdata = database_cursor.fetchall()
        for i in Itemdata:
            OrderItem.append(i[0])
        # print(OrderItem)
        print(len(OrderItem))
        #############判断容量是否满足要求######
        #CalStorage(hits, HitsThreshold, med_cubing, best_cubing, storage)
        ################计算订单信息中SKU的纯放和混放比#################
        ##############计算订单# 纯放和混放的比值 0为纯放1为混放###########
        #Cal_SingleandMix_Rate(OrderItem, Itemid, hits, HitsThreshold)

        percentage=[0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,0.15,0.2,0.25,0.3]
        Rate = []
        Hits = []
        for i in range(0,len(percentage)):
            HitsThreshold = hits[int(len(hits) * percentage[i])]
            Hits.append(HitsThreshold)
            # print(len(hits))    #不等于0 hits 的个数
            print("hits阈值为:%d" % HitsThreshold)
            CalStorage(hits, HitsThreshold, med_cubing, best_cubing, storage)
            ################计算订单信息中SKU的纯放和混放比#################
            ##############计算订单# 纯放和混放的比值 0为纯放1为混放###########
            Rate.append(Cal_SingleandMix_Rate(OrderItem, Itemid, hits, HitsThreshold))
        print(Rate,Hits)
        # 创建一个点数为 8 x 6 的窗口, 并设置分辨率为 80像素/每英寸
        plt.figure(figsize=(8, 6), dpi=80)
        # 再创建一个规格为 1 x 1 的子图
        plt.subplot(1, 1, 1)
        # 柱子总数
        # 包含每个柱子对应值的序列
        values = Rate
        # 包含每个柱子下标的序列
        index = Hits
        # 柱子的宽度
        width = 0.8
        # 绘制柱状图, 每根柱子的颜色为紫罗兰色
        p2 = plt.bar(index, values, width, label="percentage of single&mix")
        # 设置横轴标签
        plt.xlabel('(hits)Threshold')
        # 设置纵轴标签
        plt.ylabel('single&mix_rate (%)')
        # 添加标题
        plt.title('rate of single&mix items')
        #plt.axhline(y=60, color='r', linestyle='-')
        # 添加纵横轴的刻度
        # plt.xticks(index, ('Jan', 'Fub', 'Mar', 'Apr', 'May', 'Jun'))
        # plt.yticks(np.arange(0, 81, 10))
        # 添加图例
        plt.legend(loc="upper right")
        plt.show()
    except Exception as e:
        print(str(e))
