import backtrader as bt
from bn_trade_rate import Bn_UM_Futures_FundingRate
from bt_ma_strategy import BaseLogStrategy
from bn_trade_rate import Bn_UM_Futures_FundingRate



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

        self.max_holding_period = 0  # 初始化最大持仓时间
        self.min_holding_period = 0  # 初始化最小持仓时间
        self.current_holding_period = 0  # 当前持仓时间

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
            
            holding_period = trade.barclose - trade.baropen
            self.current_holding_period = holding_period

            if self.current_holding_period > self.max_holding_period:
                self.max_holding_period = self.current_holding_period
            
            if self.min_holding_period == 0 :
                self.min_holding_period = self.current_holding_period
            elif self.current_holding_period < self.min_holding_period:
                self.min_holding_period = self.current_holding_period
            


    def stop(self):
        # 在策略结束时可以记录其他信息，或者计算结果
        final_value = self.strategy.broker.getvalue()
        pnl = final_value - self.starting_cash
        total_return_rate = pnl/self.starting_cash * 100
        
        avg_profit = self.total_profit / self.win_trades if self.win_trades > 0 else 0
        avg_loss = self.total_loss / self.loss_trades if self.loss_trades > 0 else 0
        expected_return = (self.total_profit + self.total_loss) / self.total_trades if self.total_trades > 0 else 0 

        print(f'total fit {self.total_profit}, total loss {self.total_loss} max_holding_period {self.max_holding_period} min_holding_period {self.min_holding_period}')
        self.rets['total_return_rate'] = total_return_rate
        self.rets['max_profit'] = self.max_profit
        self.rets['max_loss'] = self.max_loss
        self.rets['avg_profit'] = avg_profit
        self.rets['avg_loss'] = avg_loss
        self.rets['expected_return'] = expected_return
        self.rets['max_holding_period'] = self.max_holding_period
        self.rets['min_holding_period'] = self.min_holding_period
        

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


class TestIndicator(bt.Indicator):
    lines = ('stop_profit_price',)
    plotinfo = dict(
            subplot=True, # 不在主图显示
            plotname = 'Test', # 显示名称
            plotymargin = 0.15, # y轴边距 
            )  
    plotlines = dict(
        stop_profit_price=dict(
            color='blue',  # 设置线条颜色
            linewidth=0.5,  # 线条宽度
            _plotvalue=True,  # 显示当前值
            _plotskip=False,  # 是否跳过不显示
        ),
    )

    def __init__(self, init_value = 0):
        # self.lines.stop_profit_price[0] = init_value
        self.init_value = init_value
    
    def next(self):
        # 在策略运行时动态更新
        self.lines.stop_profit_price[0] = self.init_value

class LosAndProfitPctInd(bt.Indicator):
    lines = ('stop_profit_pct','stop_loss_pct',)
    plotinfo = dict(
                subplot = True,
                plotname = 'LosAndProfitPct',
                plotymargin = 0.15,
            )
    plotlines = dict(
            stop_profit_pct = dict(color = 'red',   linewidth = 0.5, _plotvalue = True, _plotskip = False),
            stop_loss_pct   = dict(color = 'green', linewidth = 0.5, _plotvalue = True, _plotskip = False),
            )
    def __init__(self, init_value=0):
        self.init_value = init_value
    
    def next(self):
        self.lines.stop_profit_pct[0] = self.init_value
        self.lines.stop_loss_pct[0] = self.init_value

class LosAndProfitIndicator(bt.Indicator):
    lines = ('stop_profit_price','stop_loss_price',)
    plotinfo = dict(
                subplot = False,
                plotname = 'LosAndProfitPrice',
                plotymargin = 0.15,
                )
    plotlines = dict(
            stop_profit_price = dict(color='red',   linewidth=0.5, _plotvalue = True, _plotskip = False,),
            stop_loss_price   = dict(color='green', linewidth=0.5, _plotvalue = True, _plotskip = False,),
    )

    def __init__(self,init_value = 0):
        self.init_value = init_value
    
    def next(self):
        self.lines.stop_profit_price[0] = self.init_value
        self.lines.stop_loss_price[0] = self.init_value


class MyRSIStrategy(BaseLogStrategy):
    params = (
        ('rsi_period', 6),          # RSI 取值周期
        ('rsi_lower', 24),          # RSI 超卖阈值
        ('rsi_lower_deltha', 0),    # RSI 超卖阀值所加Delth，shadown算法使用
        ('atr_period', 6),          # ATR 取值周期
        ('stop_loss_pct', 68),      # shadown 算法里面下影线的长度
        ('shadown_list_len', 6),    # shadown 算法用来比较下影线的前值个数
        ('ma_slow_period', 50),     # 止损均线参数 50

        ('init_stop_los_par', 1.3),  #1.3  
        ('init_stop_los_par_plus', 2), #3.3
        ('init_stop_profit_par', 4),
        ('init_stop_profit_par_plus', 4),

        ('stop_los_par', 2),  #参数变得没有意义
        ('stop_los_par_plus', 4.7),    #4.4  4.7
        ('stop_profit_par', 2),   # 4也一样，参数变得没有意义
        ('stop_profit_par_plus', 3.5), #3.2  3.5


        ('atr_earn_multiplier', 1), # ATR 止盈的乘数
        ('atr_los_multiplier',1),   # ATR 止损的乘数

        ('rsi_upper', 70),          # RSI 超买阈值
        ('stddev_period',6),        # 标准差取值周期
        ('boll_period', 20),        
        ('boll_dev', 2),
        ('ma_fast_period', 10),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),

        ('take_profit_pct',1.01)
    )

    def __init__(self):
        # Initialize indicators
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        # self.stddev = bt.indicators.StdDev(self.data.close, period=self.params.stddev_period)
        # self.fast_ema = bt.indicators.EMA(self.data.close,period = self.params.ma_fast_period)
        self.slow_ema = bt.indicators.EMA(self.data.close,period = self.params.ma_slow_period)
        # self.boll = bt.indicators.BollingerBands(self.data.close, period=self.params.boll_period, devfactor=self.params.boll_dev)
        # self.ema = bt.indicators.EMA(self.data.close, period=self.params.ema_period)
        # self.sma = bt.indicators.SMA(self.data.close, period=self.params.ema_period)  # 如果需要简单移动均线
        # self.macd = bt.indicators.MACD(self.data.close, 
        #                                period_me1=self.params.macd_fast, 
        #                                period_me2=self.params.macd_slow, 
        #                                period_signal=self.params.macd_signal)
        # self.adx = bt.indicators.ADX(self.data, period=20)

        # self.testdata = TestIndicator(self.data, init_value=1)
        # self.id_loss_profit_price = LosAndProfitIndicator(self.data, init_value=0)
        # self.id_lost_profit_pct = LosAndProfitPctInd(self.data, init_value= 0)

        self.buy_price = 0
        self.stop_loss_price = 0
        self.take_profit_price = 0
        self.stop_profit_price = 0
        

        # 统计用
        self.max_drawdown = 0.0
        self.max_drawdown_pct = 0.0  # 用于记录最大振幅的百分比
        self.stop_loss_percentage = 0.0

        self.max_profit_pct_window = 0 #初始化最大止盈百分比窗口
        self.min_profit_pct_window = 100 #初始化最小止盈百分比窗口

        self.current_pct = 0
        self.lost_pct = 0
        self.profit_pct = 0

    def _init_profit_window(self):
        self.current_pct = 0
        self.lost_pct = 0
        self.profit_pct = 0

        self.stop_profit_price = 0
        self.stop_loss_price = 0

    def _update_profit_indicator(self):
        # self.testdata.lines.stop_profit_price[0]  = self.current_pct
        # self.id_loss_profit_price.lines.stop_profit_price[0] = self.stop_profit_price
        # self.id_loss_profit_price.lines.stop_loss_price[0] = self.stop_loss_price
        # self.id_lost_profit_pct.lines.stop_profit_pct[0] = self.lost_pct
        # self.id_lost_profit_pct.lines.stop_loss_pct[0] = self.profit_pct
        pass

    def _caculate_profit_window(self):
        self.current_pct = (self.stop_profit_price-self.stop_loss_price)*100/self.data.close[0]
        self.lost_pct = (self.stop_loss_price - self.data.close[0])*100/self.data.close[0]
        self.profit_pct = (self.stop_profit_price - self.data.close[0])*100/self.data.close[0]

        if self.current_pct > self.max_profit_pct_window:
            self.max_profit_pct_window = self.current_pct
        
        if self.current_pct < self.min_profit_pct_window: 
            self.min_profit_pct_window = self.current_pct

        # self.current_pct =current_pct

    def is_lower_shadow(self, data, index):
        open_price = data.open[index]
        close_price = data.close[index]
        low_price = data.low[index]

        # 阳线的下影线条件
        if close_price > open_price and low_price < open_price:
            return True

        # 阴线的下影线条件
        elif close_price < open_price and low_price < close_price:
            return True

        # 平盘时的下影线条件
        elif close_price == open_price and low_price < open_price:
            return True

        return False

    def _is_buy_condition1_use_shadown(self):
        if self.rsi[-1] < self.params.rsi_lower and self.rsi[0] > (self.params.rsi_lower+self.params.rsi_lower_deltha):
            lower_shadow_1 = (self.data.open[0] - self.data.low[0]) / self.data.open[0]
            lower_shadow_2 = (self.data.open[-1] - self.data.low[-1]) / self.data.open[-1]
            if min(lower_shadow_1, lower_shadow_2) > (self.params.stop_loss_pct/100000):
                if (self.is_lower_shadow(self.data, 0) == True) or (self.is_lower_shadow(self.data, -1) == True ): 
                    low_values = list(self.data.low.get(size=self.params.shadown_list_len))  # 获取前五个 low 值
                    min_value = min(low_values)  # 找到最小值
                    min_index = low_values.index(min_value)  # 找到最小值在列表中的索引
                    relative_index = -len(low_values) + min_index + 1  # 计算相对于当前数据点的索引
                    if relative_index == 0 or relative_index == -1:
                        return True
        return False
    
    def _is_buy_condition2_use_basicrsi(self):
        if self.rsi[-1] < self.params.rsi_lower and self.rsi[0] > self.params.rsi_lower:
           if self.atr[0] > 100:  #and self.adx[0] < 30:
               return True
        return False   
    
    def next(self):
        current_price = self.data.close[0]
        current_put  = 100*50
        put_size = (current_put/current_price)
        # self.log(f'date {self.data.datetime[0]} low {self.data.low[0]} high {self.data.high[0]} open {self.data.open[0]} close {self.data.close[0]}')
        if not self.position:  # 如果未持仓
            # if self._is_buy_condition1_use_shadown() == True:
            if self._is_buy_condition1_use_shadown() == True:
                self.buy_price = self.data.close[0] #open???
                self.buy(size = put_size)
                if self.data.close[0] > self.slow_ema[0]:
                    profit_parameter = self.params.init_stop_profit_par_plus
                    los_parameter = self.params.init_stop_los_par_plus
                else:
                    profit_parameter = self.params.init_stop_profit_par
                    los_parameter = self.params.init_stop_los_par
                    
                self.stop_profit_price = self.data.close[0] + profit_parameter*self.atr[0]
                self.stop_loss_price = self.data.close[0]-los_parameter*self.atr[0]
                

                self._caculate_profit_window()

                #统计信息：
                stop_loss_percentage =( (self.buy_price - self.stop_loss_price )/ self.buy_price) * 100
                if stop_loss_percentage > self.stop_loss_percentage:
                    self.stop_loss_percentage = stop_loss_percentage

                # dt = bt.num2date(self.data.datetime[0])
                # self.log(f"{dt}: 买入价格: {self.buy_price} 止损价格：{self.stop_loss_price} shadow1: {lower_shadow_1} shadow2: {lower_shadow_2}")

            

        else:  # 持仓中
            if self.data.close[0] > self.stop_profit_price:
                if self.data.close[0] > self.slow_ema[0]:
                    profit_parameter = self.params.stop_profit_par_plus
                    los_parameter = self.params.stop_los_par_plus
                else:
                    profit_parameter = self.params.stop_profit_par
                    los_parameter = self.params.stop_los_par
                    
                self.stop_profit_price = self.data.close[0] + profit_parameter*self.atr[0]
                self.stop_loss_price = self.data.close[0]-los_parameter*self.atr[0]
                
                self._caculate_profit_window()
            if self.data.close[0] < self.stop_loss_price: # or self.data.close[0]>self.stop_profit_price:
                self.close()
                self._init_profit_window()
            
            
            current_drawdown = self.data.open[0] - self.data.low[0]
            current_drawdown_pct = (current_drawdown / self.data.open[0]) * 100  # 转换为百分比

            if current_drawdown > self.max_drawdown:
                self.max_drawdown = current_drawdown
                self.max_drawdown_pct = current_drawdown_pct  # 更新最大振幅的百分比
                
     
        self._update_profit_indicator()


    def notify_trade(self, trade):
        # super().notify_trade(trade)
        # TODO 内部量收集使用
        pass

    def notify_order(self, order):
        pass

    def stop(self):
        self.close()
        # print(f'策略结束：RSI:{self.params.rsi_period}\
        #       RSI_L:{self.params.rsi_lower}\
        #       RSI_L_D:{self.params.rsi_lower_deltha}\
        #       ATR:{self.params.atr_period}\
        #       STOP_L_P:{self.params.stop_loss_pct}\
        #       SHA_L_L:{self.params.shadown_list_len}\
        #       MA_S:{self.params.ma_slow_period}\
        #       INIT_S_L_P:{self.params.init_stop_los_par}\
        #       INIT_S_L_PP:{self.params.init_stop_los_par_plus}\
        #       INIT_S_P_P:{self.params.init_stop_profit_par}\
        #       INIT_S_P_PP:{self.params.init_stop_profit_par_plus}\
        #       S_L_P:{self.params.stop_los_par}\
        #       S_L_PP:{self.params.stop_los_par_plus}\
        #       S_P_P:{self.params.stop_profit_par}\
        #       S_P_PP:{self.params.stop_profit_par_plus}')
        self.log(f'RSI策略回测结束: 资金 {self.broker.getvalue():.2f}, 余额 {self.broker.getcash():.2f}')
        self.log(f"最大向下振幅: {self.max_drawdown:.2f} ({self.max_drawdown_pct:.2f}%)")
        self.log(f"止损占仓位的最大百分比: {self.stop_loss_percentage:.2f}%")
        self.log(f'止盈窗口最小{self.min_profit_pct_window:.2f}%, 止盈窗口最大{self.max_profit_pct_window:.2f}%')



class BN_UM_Futures_RSIStrategy(MyRSIStrategy):
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
