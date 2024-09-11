import backtrader as bt
import pandas as pd
import datetime
import csv #用来存储参数

#Involve to use plot infomation
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bt_rsi_strategy import MyRSIStrategy
from bt_rsi_strategy import MyAddationalAnalyzer
from bt_rsi_strategy import BN_UM_Futures_RSIStrategy

# from bn_trade_rate import Bn_UM_Futures_FundingRate

from data_sorting import DataCollector
from bn_data_process import Process_bn_data
from bn_trade_rate import FundingFeeAnalyzer
# from bt_ma_strategy import DMAStrategy

# 打印策略参数
def collect_and_export_parameters(results,csv_filename = 'debug/strategy_parameters.csv', isprint = True):
    strat = results[0]
    params = strat.params._getkwargs()
    if isprint:
        for param, value in params.items():
            print(f"{param}: {value}")
    
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Parameter', 'Value'])
        for param, value in params.items():
            writer.writerow([param, value])

# 打印整体统计结果
def collect_and_export_results(results, top_n=3, primary_key='最终盈利', secondary_key='最大亏损', primary_ascending=False, secondary_ascending=True, csv_filename='debug/results.csv', NeedDetail = False):
    collector = DataCollector()
    formatters = {
    '最大回撤': lambda x: f"{x:.2f}%" if x is not None else None,
    '胜率': lambda x: f"{x:.2f}" if x is not None else None,
    '期望收益': lambda x: f"{x:.2f}" if x is not None else None,
    '回报回撤': lambda x: f"{x:.2f}" if x is not None else None,
    '总盈亏比': lambda x: f"{x:.2f}" if x is not None else None,
    '平均盈亏': lambda x: f"{x:.2f}" if x is not None else None
    }
    if not isinstance(results, (list, tuple)):
        results = [results]  # Ensure results is iterable
    for run in results:
        if not isinstance(run, (list, tuple)):
            run = [run]
        for substrategy in run:
            if hasattr(substrategy, 'params'):
                collector.append(
                    # RSI = substrategy.params.rsi_period,
                    # 超买 = substrategy.params.rsi_lower,
                    # 超买Deltea = substrategy.params.rsi_lower_deltha,
                    # ATR = substrategy.params.atr_period,
                    # 下影线百分比 = substrategy.params.stop_loss_pct,
                    # 前值数 = substrategy.params.shadown_list_len,
                    # 均线 = substrategy.params.ma_slow_period,
                    # 获取均线 = substrategy.params.ma_fast_period,

                    # 前值最低范围 = substrategy.p.lowerest_period,
                    # 最低止损百分比 = substrategy.p.max_loss_pct,
                    # 最大持有时间 = substrategy.p.max_duration,

                    # 初始均线下止损 = substrategy.params.init_stop_los_par,
                    # 初始均线下止盈  = substrategy.params.init_stop_profit_par,
                    # 初始均线上止损 = substrategy.params.init_stop_los_par_plus,
                    # 初始均线上止盈 = substrategy.params.init_stop_profit_par_plus,  
                    
                    # 均线下止损 = substrategy.params.stop_los_par,
                    # 均线下止盈  = substrategy.params.stop_profit_par,
                    # 均线上止损 = substrategy.params.stop_los_par_plus,
                    # 均线上止盈 = substrategy.params.stop_profit_par_plus,  

                     
                    # KDJ_Period = substrategy.params.kdj_period,
                    # KDJ_Smooth_k = substrategy.params.kdj_smooth_k,
                    # KDJ_Smotth_d = substrategy.params.kdj_smooth_d,

                    # init_profit_pct = substrategy.params.init_profit_pct,
                    # init_loss_pct   = substrategy.params.init_loss_pct,
                    # profit_pct_plus = substrategy.params.profit_pct_plus,
                    # loss_pct_plus   = substrategy.params.loss_pct_plus,

                    # 杠杆 = 50,
                    费率 = substrategy.analyzers.funding_fee_analyzer.get_analysis()["funding_fees"],

                    最终盈利 = substrategy.analyzers.tradeanalyzer.get_analysis().pnl.net.total,
                    最大盈利 = substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['max_profit'],
                    平均盈利 = substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['avg_profit'],
                    最大亏损 = substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['max_loss'],
                    平均亏损 = substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['avg_loss'],
                    期望收益 = substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['expected_return'],
                    总盈亏比 = float('inf') if substrategy.analyzers.tradeanalyzer.get_analysis().lost.pnl.total == 0\
                              else substrategy.analyzers.tradeanalyzer.get_analysis().won.pnl.total / abs(substrategy.analyzers.tradeanalyzer.get_analysis().lost.pnl.total),
                    
                    平均盈亏 = float('inf') if substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['avg_loss'] == 0\
                              else  substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['avg_profit'] / abs(substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['avg_loss']),

                    最大回撤 = substrategy.analyzers.drawdown.get_analysis().max.drawdown,
                    回撤时间 = substrategy.analyzers.drawdown.get_analysis().max.len,
                    回报回撤 = substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['total_return_rate']/substrategy.analyzers.drawdown.get_analysis().max.drawdown,
                    # 卡玛指数 = substrategy.analyzers.calmar.get_analysis().calmar,
    
                    交易总数 = substrategy.analyzers.tradeanalyzer.get_analysis().total.closed,
                    胜率 = substrategy.analyzers.tradeanalyzer.get_analysis().won.total / substrategy.analyzers.tradeanalyzer.get_analysis().total.closed,


                    formatters=formatters
                )
    collector.print_top_n(top_n, primary_key, secondary_key, primary_ascending, secondary_ascending)
    collector.to_csv(csv_filename, primary_key, secondary_key, primary_ascending, secondary_ascending)

    if NeedDetail == True:
        # 作为analyzer的测试实验代码
        # print(substrategy.analyzers.returns.get_analysis())
        # print(substrategy.analyzers.sharpratio.get_analysis())
        # print(substrategy.analyzers.sqn.get_analysis())
        substrategy.analyzers.MyAddationalAnalyzer.print_results()

if __name__ == '__main__':
    #Create one cerebro
    cerebro = bt.Cerebro()
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer,_name='tradeanalyzer')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    # cerebro.addanalyzer(bt.analyzers.SQN,_name='sqn')  # SQN算法
    # cerebro.addanalyzer(bt.analyzers.Returns,_name='returns')  #h回报率
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio,_name='sharpratio',timeframe=bt.TimeFrame.Days)  # compression=5) #夏普比率
    # cerebro.addanalyzer(bt.analyzers.Calmar, _name='calmar', timeframe=bt.TimeFrame.Months,period = 3)  # 卡尔玛比率
    cerebro.addanalyzer(FundingFeeAnalyzer, _name='funding_fee_analyzer')  #资金费率观察统计
    cerebro.addanalyzer(MyAddationalAnalyzer, _name='MyAddationalAnalyzer') #自建观察器，统计自己关注信息
    # 添加观察器
    cerebro.addobserver(bt.observers.DrawDown)  #增加回撤百分比观察曲线 
    
 
    # 设置初始投入
    inputcash = 5000000
    cerebro.broker.setcash(inputcash)
    cerebro.broker.setcommission(commission = 0.0005, commtype = bt.CommInfoBase.COMM_PERC,leverage = 50)
    print('初始投入资金:%2f' %cerebro.broker.getvalue())

    # 准备数据
    csv_file = 'data/BTCUSDT-2024-5m.csv'
    # 无日期
    from_dt  = None
    to_dt    = None
    # 经典数据:
    # 持续亏损日期
    # from_dt  = datetime.datetime(2024, 1, 12, 0, 0, 0) 
    # to_dt    = datetime.datetime(2024, 1, 13, 0, 0, 0) 
        
    # 盈利点检日期
    # from_dt  = datetime(2024, 6, 24, 18, 0, 0) 
    # to_dt    = datetime(2024, 6, 25, 18, 0, 0)

    # 特定设置日期
    # from_dt  = datetime.datetime(2024, 6, 1, 0, 0, 0)  
    # to_dt    = datetime.datetime(2024, 7, 1, 0, 0, 0) 
    
    p_start  = None #3000 #4000 #60
    p_length = None #3000 #3000 #200 #300

    #Get data via panda from csv
    bndata = Process_bn_data(filename=csv_file,from_date=from_dt,to_date = to_dt, start=p_start, length=p_length)
    # print(bndata.p.dataname)

    # Optimize Switch 优化开关
    optimize  = False 
    # Add data to cerbro
    cerebro.adddata(bndata)

    #优化参数操作
    if optimize == True:
        cerebro.optstrategy(BN_UM_Futures_RSIStrategy,
                            # rsi_period = range(3,4),  # 参数就是5，6       
                            # rsi_lower_deltha = [x / 10.0 for x in range(0, 101)],
                            # rsi_lower = [x / 10.0 for x in range(400, 601)], #range(10,40),
                            # stop_loss_pct = range(5, 800), #[x / 100000.0 for x in range(1, 201)],
                            # atr_period = range(1,100), 
                            # shadown_list_len = range(1,15),
                            # ma_slow_period = range(40,300),
                            # ma_fast_period = range(800,1500),
                            lowerest_period = range(1000,1001),
                            # max_loss_pct = [x/1000.0 for x in range(970, 999)],
                            # max_duration = range(120,600),
                            # init_stop_los_par = [x / 10.0 for x in range(3, 50)], 
                            # init_stop_profit_par = [x / 10.0 for x in range(3, 50)],
                            # stop_los_par_plus = [x / 10.0 for x in range(3, 50)],
                            # stop_profit_par_plus = [x / 10.0 for x in range(3, 50)]
                            # init_profit_pct_plus = [x/100.0 for x in range(100, 110)],
                            # init_loss_pct_plus =   [x/100.0 for x in range(90, 99)],
                            # init_stop_los_par_plus = [x / 10.0 for x in range(3, 50)],
                            # init_stop_profit_par_plus = [x / 10.0 for x in range(3, 50)],
                            # kdj_period = range(3,31),         
                            # kdj_smooth_k = range(2,21),
                            # kdj_smooth_d = range(2,21),
                            # profit_pct_plus = [x/100.0 for x in range(100, 111)],
                            # loss_pct_plus =   [x/100.0 for x in range(90, 100)],
                            # profit_pct = [x/10.0 for x in range(20, 51)],
                            # loss_pct =   [x/10.0 for x in range(20, 51)],
                            # init_profit_pct = [x/100.0 for x in range(100, 110)],
                            # init_loss_pct =   [x/100.0 for x in range(90, 100)],
                            # stop_los_par = [x / 10.0 for x in range(3, 50)],
                            # stop_profit_par = [x / 10.0 for x in range(3, 50)],
                            )
        results = cerebro.run(maxcpus = 14) #maxcpus=1
        print('打印交易分析结果:')
        collect_and_export_results(results=results) 
    #单独运行策略操作 
    else:
        
        # print('Start:%2f' %cerebro.broker.getvalue())
        cerebro.addstrategy(BN_UM_Futures_RSIStrategy)
        results = cerebro.run(volume=False) #单线程运行 maxcpus=1 
        print('最终获得资金:%2f' %cerebro.broker.getvalue())

        # Save pig to use analysis
        print("保存图片:")
        fig = cerebro.plot(volume=False,style = 'candle',start=datetime.datetime(2024, 1, 1, 0, 0, 0), end=datetime.datetime(2024, 1, 3, 0, 0, 0))[-1][0]  # style = 'candle'
        fig.set_size_inches(30, 10)
        # fig.savefig('debug/output.svg',format='svg')
        fig.savefig('debug/output.png')
        
        print("保存策略参数：")
        collect_and_export_parameters(results=results, isprint= False)

        print('打印交易分析结果:')
        collect_and_export_results(results=results,NeedDetail = True) 

        
       
        

        