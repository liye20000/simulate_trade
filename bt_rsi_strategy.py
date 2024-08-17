import backtrader as bt
from bn_trade_rate import Bn_UM_Futures_FundingRate
from bt_ma_strategy import BaseLogStrategy


class MyAddationalAnalyzer(bt.Analyzer):
    def __init__(self):
        self.win_trades = 0
        self.loss_trades = 0
        self.total_profit = 0.0
        self.total_loss = 0.0
        self.max_profit = 0.0 #float('-inf')
        self.max_loss = 0.0 #float('-inf')
        self.total_trades = 0# 总交易次数
        self.starting_cash = None #初始现金

    def start(self):
        # 在策略启动时记录初始现金
        self.starting_cash = self.strategy.broker.get_cash()

    def notify_trade(self, trade):
        if trade.isclosed:
            profit = trade.pnlcomm  # 利润（包括手续费）
            self.total_trades += 1# 更新总交易次数
            if profit >= 0:
                self.win_trades += 1
                self.total_profit += profit
                self.max_profit = max(self.max_profit, profit)
            else:
                self.loss_trades += 1
                self.total_loss += profit
                self.max_loss = min(self.max_loss, profit)

    def stop(self):
        # 在策略结束时可以记录其他信息，或者计算结果
        final_value = self.strategy.broker.getvalue()
        pnl = final_value - self.starting_cash
        total_return_rate = pnl/self.starting_cash * 100
        
        avg_profit = self.total_profit / self.win_trades if self.win_trades > 0 else 0
        avg_loss = self.total_loss / self.loss_trades if self.loss_trades > 0 else 0
        expected_return = (self.total_profit + self.total_loss) / self.total_trades if self.total_trades > 0 else 0 


        self.rets['total_return_rate'] = total_return_rate
        self.rets['max_profit'] = self.max_profit
        self.rets['max_loss'] = self.max_loss
        self.rets['avg_profit'] = avg_profit
        self.rets['avg_loss'] = avg_loss
        self.rets['expected_return'] = expected_return
        

    def get_analysis(self):
        return self.rets
        # avg_profit = self.total_profit / self.win_trades if self.win_trades > 0 else 0
        # avg_loss = self.total_loss / self.loss_trades if self.loss_trades > 0 else 0
        # expected_return = (self.total_profit + self.total_loss) / self.total_trades if self.total_trades > 0 else 0 
        # return {
        #     '最大盈利': self.max_profit,
        #     '最大损失': self.max_loss,
        #     '平均盈利': avg_profit,
        #     '平均损失': avg_loss,
        #     '期望收益': expected_return,
        # }

class MyRSIStrategy(BaseLogStrategy):
    params = (
        ('rsi_period', 6),          # RSI 取值周期
        ('rsi_upper', 70),          # RSI 超买阈值
        ('rsi_lower', 20),          # RSI 超卖阈值
        ('atr_period', 6),          # ATR 取值周期
        ('atr_earn_multiplier', 1), # ATR 止盈的乘数
        ('atr_los_multiplier',3),   # ATR 止损的乘数

        ('boll_period', 20),        
        ('boll_dev', 2),
        ('ema_period', 50),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
    )

    def __init__(self):
        # Initialize indicators
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        # self.boll = bt.indicators.BollingerBands(self.data.close, period=self.params.boll_period, devfactor=self.params.boll_dev)
        # self.ema = bt.indicators.EMA(self.data.close, period=self.params.ema_period)
        # self.sma = bt.indicators.SMA(self.data.close, period=self.params.ema_period)  # 如果需要简单移动均线
        # self.macd = bt.indicators.MACD(self.data.close, 
        #                                period_me1=self.params.macd_fast, 
        #                                period_me2=self.params.macd_slow, 
        #                                period_signal=self.params.macd_signal)
        self.buy_price = None
        self.stop_loss_price = None
        self.take_profit_price = None

       

    def next(self):
        # self.log(f'date {self.data.datetime[0]} RSI {self.rsi[0]} ATR {self.atr[0]} open {self.data.open[0]} close {self.data.close[0]}')
        if not self.position:  # 如果未持仓
            if self.rsi[-1] < self.params.rsi_lower and self.rsi[0] >= self.params.rsi_lower:
                # RSI 上穿超卖线，执行买入
                self.buy_price = self.data.open[0]
                self.stop_loss_price = self.buy_price - self.atr[0] * self.params.atr_los_multiplier
                self.take_profit_price = self.buy_price + self.atr[0] * self.params.atr_earn_multiplier
                # self.log(f'stop_loss_price {self.stop_loss_price}')
                # self.log(f'take_profit_price {self.take_profit_price}')
                self.buy()

        else:  # 持仓中
            if self.data.close[0] >= self.take_profit_price:
                # 如果价格达到止盈点，启用动态止损，取消止盈
                self.stop_loss_price = max(self.stop_loss_price, self.data.close[0] - self.atr[0] * self.params.atr_earn_multiplier)
                # self.sell()ß

            if self.data.close[0] <= self.stop_loss_price:
                # 价格低于动态止损价，卖出平仓
                self.sell()

    def notify_trade(self, trade):
        super().notify_trade(trade)
        # TODO 内部量收集使用
        pass

    def stop(self):
        self.log(f'RSI策略回测结束: 资金 {self.broker.getvalue():.2f}, 余额 {self.broker.getcash():.2f}')



