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
from bt_ma_strategy import BN_UM_Futures_LongDMAStrategy 
# from bn_trade_rate import CombinedStrategy
# from bn_trade_rate import Bn_UM_Futures_FundingRate

from data_sorting import DataCollector
from bn_data_process import Process_bn_data
from bn_trade_rate import FundingFeeAnalyzer
# from bt_ma_strategy import DMAStrategy




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
    # cerebro.broker.set_slippage_fixed(0.1) #绝对滑点
    # cerebro.broker.set_slippage_perc(0.001) #相对滑点

    #Prepare binance data to pandas,and from panda to back trader:
    # PARAMETER：进行参数调节
    optimize_option = False #是否为优化测算
    inputcash = 70000

    csv_file = 'data/BTCUSDT-2023-1h.csv'
    from_dt = None # datetime.datetime(2024, 5, 1) #None  windows = 5
    to_dt = None #datetime.datetime(2024, 5, 2)
    p_start = None #60
    p_length = None #200 #300

    
    fp=12 #7 ORDI  #15 SOL  11，23 short 最优  80，20 11 30 
    sp=21 #20 ORDI #25 SOL
    
    
    
  

    #Get data via panda from csv
    bndata = Process_bn_data(filename=csv_file,from_date=from_dt,to_date = to_dt, start=p_start, length=p_length)
    # print(bndata.p.dataname)
    #Add Need Process Data to cerebro
    # 读取CSV文件
    # data = pd.read_csv('data/btc_usdt_test.csv',parse_dates=['timestamp'],index_col='timestamp')
    # bndata = bt.feeds.PandasData(dataname=data )
    cerebro.adddata(bndata)


    # 设置初始投入
    # cerebro.broker.setcash(100)
    cerebro.broker.setcash(inputcash)
    # 设置交易费率
    # TODO: 设置杠杆后的计算需要澄清
    cerebro.broker.setcommission(commission = 0.0005, commtype = bt.CommInfoBase.COMM_PERC,leverage = 1000)
    # cerebro.broker.setcommission(commission = 0.0005, commtype = bt.CommInfoBase.COMM_PERC,leverage = 10, margin = 50,stocklike=False, interest = 1, interest_long = True)
    # cerebro.broker.setcommission(commission=0.0002,leverage=10)
 
    # leverage = self.broker.getcommissioninfo(self.data).get_leverage()
            # size = int(cash * leverage / self.dataclose[0])
    # cerebro.broker.setcommission(commission=0.0005)
    # 也可以使用自己的Commission类
    # cerebro.broker.addcommissioninfo(Bn_UM_Futures_Commission())

    print('===============Init Money============:%2f' %cerebro.broker.getvalue())

    if optimize_option:
        #对参数进行优化
        cerebro.optstrategy(BN_UM_Futures_LongDMAStrategy, fast_period=range(5, 20), slow_period=range(20, 50))        
        # cerebro.optstrategy(LongDMAStrategy, fast_period=range(5, 20), slow_period=range(20, 50))        
        
        result = cerebro.run() #单线程运行 maxcpus=1
        # 对优化数据进行打印
        collector = DataCollector('短期均线参数','长期均线参数', '最终盈利','最大亏损','最大回撤')
        for run in result:
            for substrategy in run:
                fast_period = substrategy.params.fast_period
                slow_period = substrategy.params.slow_period
                max_lost = substrategy.analyzers.tradeanalyzer.get_analysis().lost.pnl.max
                value = substrategy.analyzers.tradeanalyzer.get_analysis().pnl.net.total
                max_drawn = substrategy.analyzers.drawdown.get_analysis().max.drawdown
                collector.append(fast_period,slow_period,value,max_lost,max_drawn)
                # print(f'短期均线参数:{fast_period} 长期均线参数:{slow_period} 最终盈利:{value},最大亏损{max_lost}')
        # collector.print_all('最终盈利', '最大亏损', primary_ascending=False, secondary_ascending=True)
        collector.print_top_n(3,'最终盈利', '最大亏损', primary_ascending=False, secondary_ascending=True)

    else:
        #在图表中加入卖买点
        # cerebro.addobserver(bt.observers.BuySell)

        # 单数据运行
        # 添加组合策略，传入现货策略类和资金费率数据
        # cerebro.addstrategy(BuyAndHoldStrategy)
        cerebro.addstrategy(BN_UM_Futures_LongDMAStrategy,fast_period = fp, slow_period =sp)
        # cerebro.addstrategy(LongDMAStrategy,fast_period = fp, slow_period =sp)

        results = cerebro.run() #单线程运行 maxcpus=1       
        print('Final :%2f' %cerebro.broker.getvalue())


        trade_analyzer = results[0].analyzers.tradeanalyzer.get_analysis()
        drawdown = results[0].analyzers.drawdown.get_analysis()   
        funding_fees = results[0].analyzers.funding_fee_analyzer.get_analysis() #funding_fee_analyzer
        # print(funding_fees["funding_fees"])
        # Save pig to use analysis
        print("==================保存图片中======================")
        fig = cerebro.plot()[-1][0]
        fig.savefig('debug/output.png')
        print("===================保存完毕=======================")


        # TODO: 交易信息分析可以把整个信息打印出来后，让chat gpt帮忙分析
        # print('Returns:',trade_analyzer) 
        print('交易分析结果:')
        if trade_analyzer:
            print(f'完成的交易次数:{trade_analyzer.total.closed} 最终盈亏 {trade_analyzer.pnl.net.total}')
            print(f'盈利次数:{trade_analyzer.won.total} 盈利: {trade_analyzer.won.pnl.total}')
            print(f'亏损次数:{trade_analyzer.lost.total} 亏损: {trade_analyzer.lost.pnl.total}')
            print(f'胜率:{trade_analyzer.won.total / trade_analyzer.total.closed}')
            print(f'最大亏损：{trade_analyzer.lost.pnl.max}')
            print(f'多头交易次数:{trade_analyzer.long.total} 多头交易总盈利：{trade_analyzer.long.pnl.total}')
            print(f'空头交易次数:{trade_analyzer.short.total} 空头交易总盈利：{trade_analyzer.short.pnl.total}')
            print(f'最大回撤：{drawdown.max.drawdown:.2f}%')
            print(f'最大回撤金额：{drawdown.max.moneydown:2f}')
            print(f'最大回撤时间(天）：{drawdown.max.len}')
            print(f'消耗资金费率总和: {funding_fees["funding_fees"]}')