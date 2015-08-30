__author__ = 'ZhangYubin'
# coding=utf-8
import datetime

import MySQLdb
from pandas import Series
import numpy as np
import matplotlib.pyplot as plt
from pyexcelerate import *

from financeTools import financeT as ft
startPoint = '20060101'
endPoint = '20160101'
el=1
try:
    conn = MySQLdb.connect(host='localhost', user='root', passwd='', port=3306, charset='utf8')
    cur = conn.cursor()
    conn.select_db('funddata')
    #funds=[912]
    #funds = [912,231,377,902,330,2172]
    funds = [912,231,377,1300,902]
    wb = Workbook()
    ws = wb.new_sheet("portfolio")
    ws.set_cell_value(el, 2,"return" )
    ws.set_cell_value(el, 3,"std" )
    ws.set_cell_value(el, 4,"sharpRatio" )
    ws.set_cell_value(el, 5,"sortinoatio" )
    ws.set_cell_value(el, 6,"maxDown" )
    ws.set_cell_value(el, 7,"period" )


    def dayProfit(valueYuan):
        valueYuand = [1]
        tt = [x + 1 for x in valueYuan]
        valueYuand.extend(tt)
        i = 0
        valueYuanP = []
        for i in range(0, len(valueYuand) - 1, 1):
            valueYuanP.append((valueYuand[i + 1] - valueYuand[i]) / valueYuand[i])
        return valueYuanP


    def sharpRatio(valueYuanP):
        return np.sqrt(12) * ((np.mean(valueYuanP) - 0.0325 / 12) / np.std(valueYuanP))


    def profitYearMean(valuet):
        #return np.mean(valuet)
        return (np.power((np.mean(valuet) + 1), 12) - 1)


    def profitYearStd(valuet):
        return np.sqrt(12) *np.std(valuet)


    def printResult(name,period, valueYuanP):
        global el
        el=el+1
        ws.set_cell_value(el, 1,name )
        mean=round(profitYearMean(valueYuanP),2)
        std=round(profitYearStd(valueYuanP),2)
        sharp=round(sharpRatio(valueYuanP),2)
        sortino=round(np.sqrt(12) *ft.sortino_ratio(np.mean(valueYuanP),valueYuanP,0.0325/12),2)
        maxdd=round(ft.max_dd(valueYuanP),2)
        print("|mean:" + str(mean)),
        ws.set_cell_value(el, 2,mean )
        print("|std:" + str(std)),
        ws.set_cell_value(el, 3,std )
        print("|sharpRatio: " + str(sharp)),
        ws.set_cell_value(el, 4,sharp )
        print("|sortino_ratio: " + str(sortino)),
        ws.set_cell_value(el, 5,sortino )
        print("|Max Drawdown(Monthly): " + str(maxdd))
        ws.set_cell_value(el, 6,maxdd )
        ws.set_cell_value(el, 7,period )
        #print(str(id) +"VaR(0.05) :"+str(ft.var(valueYuanP, 0.05)))
        #print(str(id) +"CVaR(0.05) "+ str(ft.cvar(valueYuanP, 0.05)))

    def dayMove(day, move):
        endTime = day
        endTimePlusOne = endTime + datetime.timedelta(days=move)
        endTimeStr = endTimePlusOne.strftime('%Y-%m-%d')
        endTimeStr = endTimeStr.split('-')[0] + endTimeStr.split('-')[1] + endTimeStr.split('-')[2]
        return endTimeStr


    def getFund(id):
        count = cur.execute('SELECT * FROM profit where id = ' + str(id))
        results = cur.fetchall()
        valueYuan = []
        valueYuanP = []
        dateYuan = []
        for r1 in results:
            name=r1[1]
            valueYuan.append(r1[2]/100)
            dateYuan.append(datetime.datetime(int(str(r1[4]).split('-')[0]), int(str(r1[4]).split('-')[1]),
                                              int(str(r1[4]).split('-')[2])))

        tsYuan = Series(valueYuan, index=dateYuan)
        tsfYuanm=tsYuan.asfreq('M',method='pad')
        print  str(id)+": " + str((len(tsfYuanm)))+"months ",
        dateP=[]
        for (k, d) in tsfYuanm.iteritems():
            #print k, d
            valueYuanP.append(d)
            dateP.append(str(k).split(" ")[0])
        valueYuanP = dayProfit(valueYuanP)
        print "start from: "+dateP[0]+"  to :"+dateP[len(dateP)-1]
        print name+":  ",
        period=dateP[0]+" to "+dateP[len(dateP)-1]
        printResult(name,period, valueYuanP)
        tsfYuanmP= Series(valueYuanP, index=dateP)
        valueYuanPrice=[x + 1 for x in valueYuan]
        '''plot full period
        plt.plot(dateYuan,valueYuanPrice)
        plt.title(str(id))
        fname=str(id)+'.png'
        plt.savefig(fname, dpi=75)
        #plt.show()
        '''
        return tsfYuanmP


    def prices(r):
        s = []
        a=1
        for i in r:
            a=a*(1+i)
            s.append(a)
        return s
    datas = {}
    mom = {}
    s = Series()
    tt= []

    tta = []
    for id in funds:
        datas[id] = getFund(id)
        tt=[]
        for (t, v) in datas[id].iteritems():
            tt.append(t)
        tta.append(tt)
    momValue = []
    momDayValue = []
    dateQuan = []


    #print tta

    a = reduce(set.intersection,map(set, tta))
    b = sorted(a)
    print "start:  "+b[0]+"   to: "+b[len(b)-1]
    datem=[]
    for mm in b:
        datem.append(datetime.datetime(int(str(mm).split('-')[0]),int(str(mm).split('-')[1]),int(str(mm).split('-')[2])))
        momDayValue=[]
        numFund=0
        for id1 in funds:
            v=datas[id1][str(mm)] #  +00:00 for read dic tsf
            momDayValue.append(v)

        momValue.append(np.mean(momDayValue))
    singleFund=[]
    for id2 in funds:
         singleFund=[]
         for mm1 in b:
            v=datas[id2][str(mm1)]
            singleFund.append(v)
         singleFund=prices(singleFund)
         plt.plot(datem,singleFund)
    print  "mom: " + str(len(momValue))+"months"

    momDayValueP=prices(momValue)
    print "MOM-Portfolio:",
    period=b[0]+" to "+b[len(b)-1]
    printResult("Portfolio",period, momValue)
    excelName = reduce(lambda c, d: c+"-"+d,map(str,funds))
    wb.save("Portfolio"+excelName+".xlsx")

    plt.plot(datem, momDayValueP,"*",label="Portfolio",color="red",linewidth=2)
    plt.title('Portfolio')
    fname = "Portfolio"+excelName+'.png'
    plt.savefig(fname, dpi=75)
    plt.show()



    conn.commit()
    cur.close()
    conn.close()
except MySQLdb.Error, e:
    print "Mysql Error %d: %s" % (e.args[0], e.args[1])
