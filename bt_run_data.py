import backtrader as bt
import pandas as pd
import datetime

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

def collect_and_export_results(results, top_n=3, primary_key='最终盈利', secondary_key='最大亏损', primary_ascending=False, secondary_ascending=True, csv_filename='debug/results.csv', excel_filename='debug/results.xlsx'):
    collector = DataCollector()
    formatters = {
    '最大回撤': lambda x: f"{x:.2f}%" if x is not None else None,
    '胜率': lambda x: f"{x:.2f}" if x is not None else None,
    '期望收益': lambda x: f"{x:.2f}" if x is not None else None,
    '回报回撤': lambda x: f"{x:.2f}" if x is not None else None,
    '盈亏比': lambda x: f"{x:.2f}" if x is not None else None
    }
    if not isinstance(results, (list, tuple)):
        results = [results]  # Ensure results is iterable
    for run in results:
        if not isinstance(run, (list, tuple)):
            run = [run]
        for substrategy in run:
            if hasattr(substrategy, 'params'):
                collector.append(
                    RSI = substrategy.params.rsi_period,
                    超买 = substrategy.params.rsi_lower,
                    超买Deltea = substrategy.params.rsi_lower_deltha,
                    ATR = substrategy.params.atr_period,
                    下影线百分比 = substrategy.params.stop_loss_pct,
                    前值数 = substrategy.params.shadown_list_len,
                    均线 = substrategy.params.ma_slow_period,

                    初始均线下止损 = substrategy.params.init_stop_los_par,
                    初始均线上止损 = substrategy.params.init_stop_los_par_plus,
                    初始均线下止盈  = substrategy.params.init_stop_profit_par,
                    初始均线上止盈 = substrategy.params.init_stop_profit_par_plus,  
                    
                    均线下止损 = substrategy.params.stop_los_par,
                    均线上止损 = substrategy.params.stop_los_par_plus,
                    均线下止盈  = substrategy.params.stop_profit_par,
                    均线上止盈 = substrategy.params.stop_profit_par_plus,  

                     
                    杠杆 = 50,
                    费率 = substrategy.analyzers.funding_fee_analyzer.get_analysis()["funding_fees"],

                    最终盈利 = substrategy.analyzers.tradeanalyzer.get_analysis().pnl.net.total,
                    最大盈利 = substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['max_profit'],
                    平均盈利 = substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['avg_profit'],
                    最大亏损 = substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['max_loss'],
                    平均亏损 = substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['avg_loss'],
                    期望收益 = substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['expected_return'],
                    盈亏比   = substrategy.analyzers.tradeanalyzer.get_analysis().won.pnl.total / abs(substrategy.analyzers.tradeanalyzer.get_analysis().lost.pnl.total),
                    
                    最大回撤 = substrategy.analyzers.drawdown.get_analysis().max.drawdown,
                    回撤时间 = substrategy.analyzers.drawdown.get_analysis().max.len,
                    回报回撤 = substrategy.analyzers.MyAddationalAnalyzer.get_analysis()['total_return_rate']/substrategy.analyzers.drawdown.get_analysis().max.drawdown,
    
                    交易总数 = substrategy.analyzers.tradeanalyzer.get_analysis().total.closed,
                    胜率 = substrategy.analyzers.tradeanalyzer.get_analysis().won.total / substrategy.analyzers.tradeanalyzer.get_analysis().total.closed,

                    formatters=formatters
                )
    collector.print_top_n(top_n, primary_key, secondary_key, primary_ascending, secondary_ascending)
    collector.to_csv(csv_filename, primary_key, secondary_key, primary_ascending, secondary_ascending)
    # collector.to_excel(excel_filename, primary_key, secondary_key, primary_ascending, secondary_ascending)


if __name__ == '__main__':
    #Create one cerebro
    cerebro = bt.Cerebro()
    
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer,_name='tradeanalyzer')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    cerebro.addanalyzer(FundingFeeAnalyzer, _name='funding_fee_analyzer')
    cerebro.addanalyzer(MyAddationalAnalyzer, _name='MyAddationalAnalyzer')

    
 
    # 设置初始投入
    inputcash = 500000
    cerebro.broker.setcash(inputcash)
    cerebro.broker.setcommission(commission = 0.0005, commtype = bt.CommInfoBase.COMM_PERC,leverage = 50)
    # print('===============Init Money============:%2f' %cerebro.broker.getvalue())

    # 准备数据
    csv_file = 'data/BTCUSDT-2024-5m.csv'
    from_dt = None #datetime.datetime(2024, 6, 11, 0, 0, 0) #None  datetime(2024, 6, 24, 18, 0, 0)
    to_dt   = None #datetime.datetime(2024, 9, 11, 23, 0, 0)  #datetime(2024, 6, 24, 18, 0, 0)
    p_start = None #3000 #4000 #60
    p_length = None #3000 #3000 #200 #300
    #Get data via panda from csv
    bndata = Process_bn_data(filename=csv_file,from_date=from_dt,to_date = to_dt, start=p_start, length=p_length)
    # print(bndata.p.dataname)

    # Add data to cerbro
    cerebro.adddata(bndata)
    # cerebro.addstrategy(BN_UM_Futures_RSIStrategy)
    # results = cerebro.run(volume=False) #单线程运行 maxcpus=1 

    cerebro.optstrategy(BN_UM_Futures_RSIStrategy,
                        rsi_period = range(6,25),  # 参数就是5，6
                        # rsi_lower_deltha = range(0,5),
                        rsi_lower = range(20,30),
                        atr_period = range(4,30), 
                        # stop_loss_pct = range(5, 101), #[x / 100000.0 for x in range(1, 201)],
                        # shadown_list_len = range(5,8),
                        ma_slow_period = range(40,81),

                        # init_stop_los_par = [x / 10.0 for x in range(3, 50)], 
                        # init_stop_los_par_plus = [x / 10.0 for x in range(3, 50)],
                        # init_stop_profit_par = [x / 10.0 for x in range(3, 50)],
                        # init_stop_profit_par_plus = [x / 10.0 for x in range(3, 50)],
                        
                        # stop_los_par = [x / 10.0 for x in range(3, 50)],
                        # stop_los_par_plus = [x / 10.0 for x in range(3, 50)],
                        # stop_profit_par = [x / 10.0 for x in range(3, 50)],
                        # stop_profit_par_plus = [x / 10.0 for x in range(3, 50)]

                        )
    
    results = cerebro.run(maxcpus = 14) #maxcpus=1

    

        
    # print('Final :%2f' %cerebro.broker.getvalue())


    # Save pig to use analysis
    # print("==================保存图片中======================")
    # fig = cerebro.plot(volume=False)[-1][0]  # style = 'candle'
    # # fig.set_size_inches(30, 10)
    # # fig.savefig('debug/output.svg',format='svg')
    
    # fig.savefig('debug/output.png')
    # print("===================保存完毕=======================")

    print('打印交易分析结果:')
    collect_and_export_results(results=results) 
        
        
       
        

        