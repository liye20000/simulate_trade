import backtrader as bt
import datetime

# 本文件通过重构费率类进行资金费率和交易类来实现不同的交易所（币安，其他），不同的交易品种（合约，现货，其他）的收费策略
class Bn_UM_Futures_Commission(bt.CommInfoBase):
    params = (
        ('buy_fee', 0.0005),  # 买入手续费率 0.05%
        ('sell_fee', 0.0005),  # 卖出手续费率 0.05%
    )

    def _getcommission(self, size, price, pseudoexec):
        if size > 0:  # 买入
            return size * price * self.p.buy_fee
        elif size < 0:  # 卖出
            return -size * price * self.p.sell_fee
        else:
            return 0


class Bn_UM_Futures_FundingRate(bt.Strategy):
    FUNDING_TIMES = [
        (0, 0),   # 00:00
        (8, 0),   # 08:00
        (16, 0)   # 16:00
    ]

    params = (
        ('funding_rate', 0.0001),  # 资金费率 0.3%
    )

    def __init__(self):
        self.next_funding_time = None
        # self.funding_fee = 0

    def set_next_funding_time(self):
        current_datetime = self.datas[0].datetime.datetime(0)
        current_time = current_datetime.time()
        current_date = current_datetime.date()

        for hour, minute in self.FUNDING_TIMES:
            funding_datetime = datetime.datetime.combine(current_date, datetime.time(hour, minute))
            if funding_datetime > current_datetime:
                self.next_funding_time = funding_datetime
                return
        
        # If none of the funding times are after the current time, set to the next day's first funding time
        next_day = current_date + datetime.timedelta(days=1)
        self.next_funding_time = datetime.datetime.combine(next_day, datetime.time(*self.FUNDING_TIMES[0]))
    
    def next(self):
        if self.next_funding_time is None:
            self.set_next_funding_time()

        current_datetime = self.datas[0].datetime.datetime(0)

        # 检查是否到达资金费率扣除时间
        if current_datetime >= self.next_funding_time:
            for position in self.broker.positions.values():
                if position.size != 0: #处理多头和空头
                    price = self.datas[0].close
                    funding_fee =  price* position.size * self.p.funding_rate
                    # funding_fee = position.price * position.size * self.p.funding_rate
                    self.broker.cash -= funding_fee
                    # self.funding_fee += funding_fee
                    # 更新分析器
                    if hasattr(self, 'analyzers') and hasattr(self.analyzers, 'funding_fee_analyzer'):
                        self.analyzers.funding_fee_analyzer.funding_fees += funding_fee
                    # self.log_funding_fee(current_datetime,funding_fee)
            self.set_next_funding_time()

    def log_funding_fee(self, current_datetime, funding_fee):
        print(f'Current Time: {current_datetime}, Next Funding Time: {self.next_funding_time}')
        print('Funding Fee Deducted: %.2f, Cash: %.2f' % (funding_fee, self.broker.cash))
        print(f'Fundig fee total is {self.analyzers.funding_fee_analyzer.funding_fees} ')

class CombinedStrategy(bt.Strategy):
    def __init__(self):
        self.rate_strategy = Bn_UM_Futures_FundingRate() #self.p.tradestrategy()
        self.rate_strategy.broker = self.broker
        self.rate_strategy.datas = self.datas
    def next(self):
        self.rate_strategy.next()  # 调用现货交易策略的 next 方法



class FundingFeeAnalyzer(bt.Analyzer):
    def __init__(self):
        self.funding_fees = 0

    def notify_cashvalue(self, cash, value):
        if hasattr(self.strategy, 'funding_fee'):
            self.funding_fees += self.strategy.funding_fee
            print(f'Analysier: funding_fees is {self.funding_fees}')

    def get_analysis(self):
        # print(f'Got Funding Fees:{self.funding_fees}')
        return {'funding_fees': self.funding_fees}

