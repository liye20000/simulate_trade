import backtrader as bt
import pandas as pd
import datetime

#Involve to use plot infomation
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bt_ma_strategy import BuyAndHoldStrategy 
# from bt_ma_strategy import ShortDMAStrategy
from bn_trade_rate import Bn_UM_Futures_Commission
from bt_ma_strategy import LongDMAStrategy
from bt_ma_strategy import ShortDMAStrategy
from bt_ma_strategy import BN_UM_Futures_LongDMAStrategy 
from bt_ma_strategy import BN_UM_Futures_ShortDMAStrategy
# from bn_trade_rate import CombinedStrategy


# from bn_trade_rate import Bn_UM_Futures_FundingRate

from data_sorting import DataCollector
from bn_data_process import Process_bn_data
from bn_trade_rate import FundingFeeAnalyzer
# from bt_ma_strategy import DMAStrategy

def collect_and_export_results(results, top_n=3, primary_key='最终盈利', secondary_key='最大亏损', primary_ascending=False, secondary_ascending=True, csv_filename='debug/results.csv', excel_filename='debug/results.xlsx'):
    
    collector = DataCollector( '短期均线参数','长期均线参数', 
                               '杠杆','成交量win','成交量Thr','止损p',
                               '最终盈利','最大亏损','最大回撤',
                               '胜率','回撤时间','资金费率')
    
    if not isinstance(results, (list, tuple)):
        results = [results]  # Ensure results is iterable
    
    for run in results:
        if not isinstance(run, (list, tuple)):
            run = [run]
        for substrategy in run:
            if hasattr(substrategy, 'params'):
                fast_period = substrategy.params.fast_period
                slow_period = substrategy.params.slow_period
                use_lever = substrategy.params.use_lever
                volume_window = substrategy.params.volume_window
                volume_threshold = substrategy.params.volume_threshold
                lost_perc = substrategy.params.lost_perc 
                max_lost = substrategy.analyzers.tradeanalyzer.get_analysis().lost.pnl.max
                value = substrategy.analyzers.tradeanalyzer.get_analysis().pnl.net.total
                max_drawn = substrategy.analyzers.drawdown.get_analysis().max.drawdown
                win_perc = substrategy.analyzers.tradeanalyzer.get_analysis().won.total / substrategy.analyzers.tradeanalyzer.get_analysis().total.closed
                drawdown_time = substrategy.analyzers.drawdown.get_analysis().max.len
                funding_fees = substrategy.analyzers.funding_fee_analyzer.get_analysis()["funding_fees"]
                
                collector.append(fast_period, slow_period, use_lever, volume_window, volume_threshold, lost_perc, value, max_lost, max_drawn, win_perc, drawdown_time, funding_fees)
    
    collector.print_top_n(top_n, primary_key, secondary_key, primary_ascending, secondary_ascending)
    collector.to_csv(csv_filename, primary_key, secondary_key, primary_ascending, secondary_ascending)
    collector.to_excel(excel_filename, primary_key, secondary_key, primary_ascending, secondary_ascending)


    # trade_analyzer = results[0].analyzers.tradeanalyzer.get_analysis()
    # drawdown = results[0].analyzers.drawdown.get_analysis()   
    # funding_fees = results[0].analyzers.funding_fee_analyzer.get_analysis() #funding_fee_analyzer
    # if trade_analyzer:
        #     print(f'完成的交易次数:{trade_analyzer.total.closed} 最终盈亏 {trade_analyzer.pnl.net.total}')
        #     print(f'盈利次数:{trade_analyzer.won.total} 盈利: {trade_analyzer.won.pnl.total}')
        #     print(f'亏损次数:{trade_analyzer.lost.total} 亏损: {trade_analyzer.lost.pnl.total}')
        #     print(f'胜率:{trade_analyzer.won.total / trade_analyzer.total.closed}')
        #     print(f'最大亏损：{trade_analyzer.lost.pnl.max}')
        #     print(f'多头交易次数:{trade_analyzer.long.total} 多头交易总盈利：{trade_analyzer.long.pnl.total}')
        #     print(f'空头交易次数:{trade_analyzer.short.total} 空头交易总盈利：{trade_analyzer.short.pnl.total}')
        #     print(f'最大回撤：{drawdown.max.drawdown:.2f}%')
        #     print(f'最大回撤金额：{drawdown.max.moneydown:2f}')
        #     print(f'最大回撤时间(天）：{drawdown.max.len}')
        #     print(f'消耗资金费率总和: {funding_fees["funding_fees"]}') 


if __name__ == '__main__':
    #Create one cerebro
    cerebro = bt.Cerebro()
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer,_name='tradeanalyzer')
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(FundingFeeAnalyzer, _name='funding_fee_analyzer')
    # cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    
    #设置滑点
    # cerebro.broker.set_slippage_fixed(0.1) #绝对滑点ß
    # cerebro.broker.set_slippage_perc(0.001) #相对滑点
    
    # 设置初始投入
    inputcash = 70000
    cerebro.broker.setcash(inputcash)
    print('===============Init Money============:%2f' %cerebro.broker.getvalue())
    
    # 设置交易费率
    # 设置commtype，明确交易手续费采用百分比方式，设置leverage后，可以在strategy里面设置杠杆而不报错
    cerebro.broker.setcommission(commission = 0.0005, commtype = bt.CommInfoBase.COMM_PERC,leverage = 1000)
    # cerebro.broker.setcommission(commission=0.0005)
    # 也可以使用自己的Commission类
    # cerebro.broker.addcommissioninfo(Bn_UM_Futures_Commission())


    # 准备数据
    csv_file = 'data/BTCUSDT-2022-1h.csv'
    from_dt = None # datetime.datetime(2024, 5, 1) #None  windows = 5
    to_dt = None #datetime.datetime(2024, 5, 2)
    p_start = None #60
    p_length = None #200 #300
    #Get data via panda from csv
    bndata = Process_bn_data(filename=csv_file,from_date=from_dt,to_date = to_dt, start=p_start, length=p_length)
    # Another data type csv
    # data = pd.read_csv('data/btc_usdt_test.csv',parse_dates=['timestamp'],index_col='timestamp')
    # bndata = bt.feeds.PandasData(dataname=data )
    print(bndata.p.dataname)
    # Add data to cerbro
    cerebro.adddata(bndata)

    optimize_option = False #是否为优化测算
    fp=11 #7 ORDI  #15 SOL  11，23 short 最优  80，20 11 30 
    sp=21 #20 ORDI #25 SOL
    

    if optimize_option:
        #对参数进行优化
        cerebro.optstrategy(BN_UM_Futures_ShortDMAStrategy, 
                            fast_period=range(5, 12),  #（5，15）
                            slow_period=range(15, 30), #（20，40）
                            use_lever=range(4,9),
                            volume_window = range(5,6),
                            volume_threshold = [x / 10.0 for x in range(15, 16)], #range(1.0,2.0),  #[x / 10.0 for x in range(1, 20)]
                            lost_perc = [x / 100.0 for x in range(5, 6)] #range(0.03, 0.08) #[x / 10.0 for x in range(1, 20)]
                            )        
        # cerebro.optstrategy(LongDMAStrategy, fast_period=range(5, 20), slow_period=range(20, 50))        
        
        results = cerebro.run() #单线程运行 maxcpus=1
        # 对优化数据进行打印
        collect_and_export_results(results=results)
       
    else:
        #在图表中加入卖买点
        # cerebro.addobserver(bt.observers.BuySell)

        # 运行策略
        
        # cerebro.addstrategy(BuyAndHoldStrategy)
        
        # cerebro.addstrategy(BN_UM_Futures_LongDMAStrategy,fast_period = fp, slow_period =sp,use_lever=8,lost_perc=0.05, volume_threshold = 1.5)
        # cerebro.addstrategy(LongDMAStrategy,fast_period = fp, slow_period =sp,use_lever = 1,use_lever=8,lost_perc=0.05, volume_threshold = 1.5)

        # cerebro.addstrategy(ShortDMAStrategy,fast_period = fp, slow_period =sp, use_lever =1,use_lever=8,lost_perc=0.05, volume_threshold = 1.5)
        cerebro.addstrategy(BN_UM_Futures_ShortDMAStrategy,fast_period = fp, slow_period =sp,use_lever=8,lost_perc=0.05, volume_threshold = 1.5 )
        
        results = cerebro.run() #单线程运行 maxcpus=1       
        
        print('Final :%2f' %cerebro.broker.getvalue())
        
        # Save pig to use analysis
        print("==================保存图片中======================")
        fig = cerebro.plot()[-1][0]
        fig.savefig('debug/output.png')
        print("===================保存完毕=======================")
        
        
        # 对优化数据进行打印
        print('打印交易分析结果:')
        collect_and_export_results(results=results) 
        

        