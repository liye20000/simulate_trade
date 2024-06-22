import backtrader as bt
import backtrader.indicators as btid
import logging
from log_config import logger

# 构建买入并持有策略，作为与其他策略的比较基准，并用来进行比较测试
class BuyAndHoldStrategy(bt.Strategy):
    def __init__(self):
       self._tradehistoryon = True  #打开交易记录记录开关 
    def next(self):
        # print(f'data:{self.data.close[0]}')
        if len(self.data) == 1:
            self.size = self.broker.get_cash() // self.data.close[0]
            # self.buy_order = self.sell(size=self.size,transmit=True)

            # # 买入订单完成后，设置止损和止盈单
            # stop_price = self.data.close[0] * 1.1
            # take_profit_price = self.data.close[0] * 0.95
        
            # # 创建止损单，不立即传输
            # self.buy(
            #     exectype=bt.Order.Stop, 
            #     size=self.size,
            #     price=stop_price, 
            #     parent= self.buy_order, #order
            #     transmit=True
            # )
         
            
            # # 创建止盈单，传输止损单和止盈单
            # self.buy(
            #     exectype=bt.Order.Limit, 
            #     size=self.size,
            #     price=take_profit_price, 
            #     parent=self.buy_order, 
            #     transmit=False
            # )
            
            #bracket 不可以单独设置 止盈（limitprice）和止损（stopprice），但是如果现金不够，止盈止损需要先计算好，否则bracket订单不能执行
       
            self.sell_order = self.sell_bracket(
                    limitprice= self.data.close[0] * 0.5,  # 止盈价格 
                    stopprice= self.data.close[0] * 2,   # 止损价格
                    price=self.data.close[0],            # 卖出价格
                    size = 1
            )
    def notify_trade(self, trade):
        # 在每次交易完成后，输出想了解的交易信息： 交易开始时间，开始点位，投入金额，结束时间，结束点位，交易后的总金额，扣除手续费后的收益
        if trade.isclosed:            
            start_date = bt.num2date(trade.history[0].status.dt)
            start_price = trade.history[0].status.price
            size = trade.history[0].status.size

            close_date = bt.num2date(trade.history[-1].status.dt)
            # close_price = trade.history[-1].status.price
            print(f'交易开始时间: {start_date} 买入点位:{start_price}  买入数量:{size} '
                  f'交易结束时间: {close_date} ' 
                #   f'交易手续费：{commission} '
                  f'未扣除交易费率利润: {gross_profit} 扣除交易费率利润：{com_profit}')
        # TODO: 合约交易中，除了交易费用，还有资金费率，如交易保留时间大于8小时，则可能需要扣除资金费率，需要进行额外计算，计算思路，当持仓时间超过8小时，对于本金仓位，扣除一次资金费率（也可能是增加）

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.issell():
                print(f'SELL ORDER COMPLETED. Price: {order.executed.price}, Size: {order.executed.size}')              

                
            elif order.isbuy():
                print(f'BUY ORDER COMPLETED. Price: {order.executed.price}, Size: {order.executed.size}')
                # 清空订单引用

    # def stop(self):   
    #     # 在策略结束时卖出
    #     if self.position:
    #         self.sell(size=self.position.size)  # 卖出所有持仓
    #         self.has_sold = True  # 更新标记，确保只卖出一次
     
class BaseLogStrategy(bt.Strategy):
    def log(self, txt, level=logging.INFO):
        # 预留，可以设置系统时间
        # dt = dt or self.datas[0].datetime.date(0)
        # log_msg = f'{dt.isoformat()} {txt}'
        log_msg = f'{txt}'
        logger.log(level, log_msg)

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
                self.log(f'完成卖出订单:'
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
                  f'未扣除交易费率利润:{trade.pnl} ' 
                  f'交易手续费:{trade.commission} '
                  f'扣除交易费率利润:{trade.pnlcomm}'
                  )
        # TODO: 合约交易中，除了交易费用，还有资金费率，如交易保留时间大于8小时，则可能需要扣除资金费率，需要进行额外计算，计算思路，当持仓时间超过8小时，对于本金仓位，扣除一次资金费率（也可能是增加）

class BaseDMAStrategy(BaseLogStrategy):
    params = (
        ('fast_period',5),
        ('slow_period',15),
     )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.sma_fast = btid.MovAv.SMA(self.datas[0],period = self.p.fast_period)
        self.sma_slow = btid.MovAv.SMA(self.datas[0],period = self.p.slow_period)
        self.signal = btid.CrossOver(self.sma_fast,self.sma_slow)

class LongDMAStrategy(BaseDMAStrategy):
    params = (
        ('lost_perc',0.05),
    )

    def __init__(self):
        super().__init__() # 调用父类的__init__方法
        self.long_stop_price = 0  #记录当前多单止损价格
 
    def next(self):
        current_price = self.data.close[0]
        current_put  = self.broker.get_cash()
        put_size = int(current_put/current_price) 

        if not self.position:  #没有仓位
            if self.signal > 0 :
                self.long_stop_price = current_price*(1-self.p.lost_perc)                    
                self.buy(size = put_size,price = current_price)
                self.log(f'[做多]触发均线上穿买入{put_size}, 当前买入价格{current_price} 设定止损价格：{self.long_stop_price}')         
        else:
            if self.signal < 0 :
                self.log(f'[做多]触发均线下穿卖出，当前卖出价格{current_price}, 设定止损价格{self.long_stop_price}')
                self.close()
            elif self.long_stop_price >= current_price:
                self.log(f'[做多]触发止损卖出，当前卖出价格{current_price}, 设定止损价格{self.long_stop_price}')
                self.close()

class ShortDMAStrategy(BaseDMAStrategy):
    params = (
        ('lost_perc',0.05),
    )

    def __init__(self):
        super().__init__() # 调用父类的__init__方法
        self.short_stop_price = 0 
   
    def next(self):
        current_price = self.data.close[0]
        current_put  = self.broker.get_cash()
        put_size = int(current_put/current_price)

        if not self.position:
            if self.signal < 0:
                self.short_stop_price = current_price*(1+self.p.lost_perc)
                self.sell(size=put_size,price=current_price)
                self.log(f'[做空]触发均线下穿卖出{put_size},当前卖出价格:{current_price} ,设定止损价格:{self.short_stop_price}')
        else:
            if self.signal > 0:
                self.log(f'[做空]触发均线上穿买入,当前买入价格:{current_price},设定止损价格:{self.short_stop_price}')
                self.close()
            elif self.short_stop_price <= current_price:
                self.log(f'[做空]触发止损买入,当前买入价格:{current_price}，设定止损价格:{self.short_stop_price}')
                self.close()