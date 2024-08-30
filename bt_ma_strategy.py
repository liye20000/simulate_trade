import backtrader as bt
import backtrader.indicators as btid
import logging
# from log_config import logger
from lb_logger import log as logger
from bn_trade_rate import Bn_UM_Futures_FundingRate

class BaseLogStrategy(bt.Strategy):
    def log(self, txt, level=logging.DEBUG):
        # 预留，可以设置系统时间
        # dt = dt or self.datas[0].datetime.date(0)
        # log_msg = f'{dt.isoformat()} {txt}'
        log_msg = f'{txt}'
        logger.info(log_msg)

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.issell():
                # print(dir(order.executed)) #pnl, pnlcomm              
                self.log(f'完成卖出订单:'
                      f'时间:{bt.num2date(order.executed.dt)} '
                      f'卖出价格:{order.executed.price} ' 
                      f'卖出仓位:{order.executed.size} ' 
                      f'手续费:{order.executed.comm} '
                      )   
            elif order.isbuy():
                self.log(f'完成买入订单:'
                      f'时间:{bt.num2date(order.executed.dt)} '
                      f'买入价格:{order.executed.price} ' 
                      f'买入仓位:{order.executed.size} ' 
                      f'手续费:{order.executed.comm} '
                      )   

   
    def notify_trade(self, trade):
        if trade.isclosed:            
            # print(dir(trade)) #打印出来可以看trade的相关信息，用来做参考
            self.log(f'完成交易:'
                  f'交易开始时间:{bt.num2date(trade.dtopen)} '
                  f'交易结束时间:{bt.num2date(trade.dtclose)} '
                  f'未扣除交易费率利润:{trade.pnl:.2f} ' 
                  f'交易手续费:{trade.commission:.2f} '
                  f'扣除交易费率利润:{trade.pnlcomm:.2f}'
                  f'剩余现金：{self.broker.getcash():.2f}'
                  )


# 构建买入并持有策略，作为与其他策略的比较基准，并用来进行比较测试
class BuyAndHoldStrategy(BaseLogStrategy):
    def __init__(self):
        self.put_size = 0
        self.dataclose = self.datas[0].close  # 获取数据集的收盘价
    def next(self):
        # print(f'date:{self.datas[0].datetime.datetime(0)}')
        if not self.position:  # 检查是否已经持有仓位
            # print(f'Money is {self.broker.get_cash()}')
            # self.buy()
            current_price = self.data.close[0]
            current_put  = self.broker.get_cash()
            self.put_size = int(current_put/current_price) 
            self.buy(size =self.put_size,price=current_price)
        if len(self.data) == self.data.buflen() - 1 and self.position:    
            self.sell(size=self.put_size) 
            # self.sell()
            # self.close()
    # def stop(self):
    #     if self.position: #有仓位
    #         self.log("没有数据了，卖出？")
    #         self.sell(size=self.put_size)

class BaseDMAStrategy(BaseLogStrategy):
    params = (
        ('fast_period',5),
        ('slow_period',15),
        ('volume_threshold',1.5), #交易量倍数阈值
        ('volume_window',5), #交易量攀升的窗口
     )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.sma_fast = btid.MovAv.SMA(self.datas[0],period = self.p.fast_period)
        self.sma_slow = btid.MovAv.SMA(self.datas[0],period = self.p.slow_period)
        self.volume_ma = btid.MovAv.SMA(self.data.volume,period=self.p.volume_window)

        self.ema_fast = btid.MovAv.EMA(self.datas[0],period = self.p.fast_period)
        self.ema_slow = btid.MovAv.EMA(self.datas[0],period = self.p.slow_period)
 


class LongDMAStrategy(BaseDMAStrategy):
    params = (
        ('lost_perc',0.05),
        ('use_lever',8),
    )

    def __init__(self):
        super().__init__() # 调用父类的__init__方法
        self.long_stop_price = 0  #记录当前多单止损价格
        self.long_earn_stop_price = 0 #记录止盈价格
        self.log(f'fast [{self.p.fast_period}] '
                 f'slow [{self.p.slow_period}] '
                 f'lost_perc [{self.p.lost_perc}] '
                 f'volume_threshold [{self.p.volume_threshold}] '
                 f'volume_window [{self.p.volume_window}] '
                 f'use_lever [{self.p.use_lever}] ',
                 level = logging.INFO)
        # self.log(f'fast[self.p.fast_period]',level = logging.CRITICAL)
        
        self.signal = btid.CrossOver(self.sma_fast,self.sma_slow)
 
    def next(self):
        current_price = self.data.close[0]
        current_put  = self.broker.getcash()*(self.p.use_lever)
        put_size = int(current_put/current_price)
        # put_size = 1 

        volume_increasing =  self.data.volume[0] >self.p.volume_threshold*self.volume_ma[0]

        # self.log(f'[RSI]{self.rsi[0]}')
    
        if not self.position:  #没有仓位
            if self.signal>0 and volume_increasing:
                self.long_stop_price = current_price*(1-self.p.lost_perc)     
                self.long_earn_stop_price =  current_price*1.1              
                self.buy(size = put_size,price = current_price)
                # self.log(f'[做多]触发均线上穿买入{put_size}, 当前买入价格{current_price} 设定止损价格：{self.long_stop_price}')         
        else:
            if self.signal < 0 and volume_increasing:
                # self.log(f'[做多]触发均线下穿卖出，当前卖出价格{current_price}, 设定止损价格{self.long_stop_price}')
                self.close()
            elif self.long_stop_price >= current_price:
                self.log(f'[做多]触发止损卖出，当前卖出价格{current_price}, 设定止损价格{self.long_stop_price}')
                self.close()
            # elif current_price >= self.long_earn_stop_price:
            #     self.log(f'[做多]触发止盈卖出，当前卖出价格{current_price}, 设定止损价格{self.long_earn_stop_price}')
            #     self.close()
class ShortDMAStrategy(BaseDMAStrategy):
    params = (
        ('lost_perc',0.05),
         ('use_lever',5),
         )

    def __init__(self):
        super().__init__() # 调用父类的__init__方法
        self.short_stop_price = 0 
        self.log(f'fast [{self.p.fast_period}] '
                 f'slow [{self.p.slow_period}] '
                 f'lost_perc [{self.p.lost_perc}] '
                 f'volume_threshold [{self.p.volume_threshold}] '
                 f'volume_window [{self.p.volume_window}] '
                 f'use_lever [{self.p.use_lever}] ',
                 level = logging.INFO)
        
        self.signal = btid.CrossOver(self.sma_fast,self.sma_slow)
 

    def next(self):
        current_price = self.data.close[0]
        current_put  = self.broker.getcash()*self.p.use_lever
        put_size = int(current_put/current_price)

        volume_increasing =  self.data.volume[0] >self.p.volume_threshold*self.volume_ma[0]

        if not self.position:
            if self.signal < 0 and volume_increasing:
                self.short_stop_price = current_price*(1+self.p.lost_perc)
                self.sell(size=put_size,price=current_price)
                self.log(f'[做空]触发均线下穿卖出{put_size},当前卖出价格:{current_price} ,设定止损价格:{self.short_stop_price}')
        else:
            if self.signal > 0 and volume_increasing:
                self.log(f'[做空]触发均线上穿买入,当前买入价格:{current_price},设定止损价格:{self.short_stop_price}')
                self.close()
            elif self.short_stop_price <= current_price:
                self.log(f'[做空]触发止损买入,当前买入价格:{current_price}，设定止损价格:{self.short_stop_price}')
                self.close()

class BN_UM_Futures_LongDMAStrategy(LongDMAStrategy):
    def __init__(self):
        super().__init__() # 调用父类的__init__方法
        self.rate_strategy = Bn_UM_Futures_FundingRate() #self.p.tradestrategy()
        self.rate_strategy.broker = self.broker
        self.rate_strategy.datas = self.datas 
        self.rate_strategy.analyzers = self.analyzers
    
    def next(self):
        super().next()
        self.rate_strategy.next()
        # print(f'The broker cash is {self.broker.cash}' )


class BN_UM_Futures_ShortDMAStrategy(ShortDMAStrategy):
    def __init__(self):
        super().__init__() # 调用父类的__init__方法
        self.rate_strategy = Bn_UM_Futures_FundingRate() #self.p.tradestrategy()
        self.rate_strategy.broker = self.broker
        self.rate_strategy.datas = self.datas 
        self.rate_strategy.analyzers = self.analyzers
    
    def next(self):
        super().next()
        self.rate_strategy.next()
        # print(f'The broker cash is {self.broker.cash}' )