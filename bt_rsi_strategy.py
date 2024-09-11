import backtrader as bt
from bn_trade_rate import Bn_UM_Futures_FundingRate
from bt_ma_strategy import BaseLogStrategy
from bn_trade_rate import Bn_UM_Futures_FundingRate


#自建分析器，用来统计除Backtrader自带分析器外，需要额外分析统计的信息
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

        self.win_streak = 0      # 当前的盈利连续次数
        self.loss_streak = 0     # 当前的亏损连续次数
        self.max_win_streak = 0  # 历史最大盈利连续次数
        self.max_loss_streak = 0 # 历史最大亏损连续次数
        self.previous_result = None  # 前一笔交易结果
        
        # 分析结果字典      
        self.rets = {
            'total_return_rate': None,
            'max_profit': None,
            'max_loss': None,
            'avg_profit': None,
            'avg_loss': None,
            'expected_return': None,
            'max_holding_period': None,
            'min_holding_period': None,
            'max_win_streak': None,
            'max_loss_streak': None
        }

        # 字段的中文别名映射
        self.aliases = {
            'total_return_rate': '收益率',
            'max_profit': '最大盈利',
            'max_loss': '最大亏损',
            'avg_profit': '平均盈利',
            'avg_loss': '平均亏损',
            'expected_return': '预期收益',
            'max_holding_period': '最长持仓时间',
            'min_holding_period': '最短持仓时间',
            'max_win_streak': '最长连续盈利次数',
            'max_loss_streak': '最长连续亏损次数'
        }

    def start(self):
        # 在策略启动时记录初始现金
        self.starting_cash = self.strategy.broker.get_cash()

    def notify_trade(self, trade):
        if trade.isclosed:
            profit = trade.pnlcomm  # 利润（扣除手续费）
            self.total_trades += 1# 更新总交易次数
            if profit >= 0:
                self.win_trades += 1
                self.total_profit += profit
                self.max_profit = max(self.max_profit, profit)

                if self.previous_result is None or self.previous_result > 0:
                    self.win_streak += 1  # 连续盈利
                else:
                    self.win_streak = 1  # 重新开始盈利连击

                self.loss_streak = 0  # 清零亏损连击

                # 更新历史最大盈利连击
                if self.win_streak > self.max_win_streak:
                    self.max_win_streak = self.win_streak

            else:
                self.loss_trades += 1
                self.total_loss += profit
                self.max_loss = min(self.max_loss, profit)

                if self.previous_result is None or self.previous_result < 0:
                    self.loss_streak += 1  # 连续亏损
                else:
                    self.loss_streak = 1  # 重新开始亏损连击

                self.win_streak = 0  # 清零盈利连击

                # 更新历史最大亏损连击
                if self.loss_streak > self.max_loss_streak:
                    self.max_loss_streak = self.loss_streak
            
             # 保存当前交易结果作为前一次交易结果
            self.previous_result = profit

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

        self.rets['total_return_rate'] = total_return_rate  #收益率
        self.rets['max_profit'] = self.max_profit  #最大盈利
        self.rets['max_loss'] = self.max_loss      #最大亏损
        self.rets['avg_profit'] = avg_profit       #平均盈利
        self.rets['avg_loss'] = avg_loss           #平均亏损
        self.rets['expected_return'] = expected_return #平均亏损或盈利
        self.rets['max_holding_period'] = self.max_holding_period #最大持仓时间
        self.rets['min_holding_period'] = self.min_holding_period #最小持仓时间
        self.rets['max_win_streak'] = self.max_win_streak #连续盈利次数
        self.rets['max_loss_streak'] = self.max_loss_streak #连续亏损次数

    def get_analysis(self):
        return self.rets
    
    def print_results(self):
        print("分析结果:")
        for key, value in self.rets.items():
            # 获取中文别名，没有别名则使用原字段名
            alias = self.aliases.get(key, key)
            if value is not None:  # 只打印有值的字段
                print(f"{alias}: {value}")
            else:
                print(f"{alias}: 未计算")

#自建指标，可以用来在plot里面显示自己需要的统计信息，此为测试指标
class TestIndicator(bt.Indicator):
    lines = ('stop_profit_price',)
    plotinfo = dict(
            subplot=True, # 不在主图显示
            plotname = 'Test', # 显示名称
            # plotymargin = 0.15, # y轴边距 
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

#自建指标，可以用来在plot里面显示盈利亏损窗口的百分比
class LosAndProfitPctInd(bt.Indicator):
    lines = ('stop_profit_pct','stop_loss_pct',)
    plotinfo = dict(
                subplot = True,
                plotname = 'LosAndProfitPct',
                plotymargin = 0.15, #轴边距
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

#自建指标，可以用来显示用来在持仓时描画止盈止损边界
class LosAndProfitIndicator(bt.Indicator):
    lines = ('stop_profit_price','stop_loss_price',)
    plotinfo = dict(
                subplot = False,
                plotname = 'LosAndProfitPrice',
                # plotymargin = 0.15,
                )
    plotlines = dict(
            stop_profit_price = dict(color='red',   linewidth=1.0, _plotvalue = True, _plotskip = False,),
            stop_loss_price   = dict(color='green', linewidth=1.0, _plotvalue = True, _plotskip = False,),
    )

    def __init__(self,init_value = 0):
        self.init_value = init_value
    
    def next(self):
        self.lines.stop_profit_price[0] = self.init_value
        self.lines.stop_loss_price[0] = self.init_value

#此指标为仿照Chatgpt来制作的kDJ指标，因为backtrader标准库并没又提供KDJ指标
class KDJ(bt.Indicator):
    lines = ('k', 'd', 'j')
    params = (('period', 14), ('smooth_k', 3), ('smooth_d', 3))

    def __init__(self):
        self.addminperiod(self.params.period)
        
        highest_high = bt.ind.Highest(self.data.high(-1), period=self.params.period)
        lowest_low = bt.ind.Lowest(self.data.low(-1), period=self.params.period)
        
        # 添加一个很小的值来避免除以零
        rsv = (self.data.close(-1) - lowest_low) / (highest_high - lowest_low + 1e-5) * 100
        
        self.lines.k = bt.indicators.EMA(rsv, period=self.params.smooth_k)
        self.lines.d = bt.indicators.EMA(self.lines.k, period=self.params.smooth_d)
        self.lines.j = 3 * self.lines.k - 2 * self.lines.d


#RSI基础策略
class MyRSIStrategy(BaseLogStrategy):
    params = (
        ('rsi_period', 6),          # RSI 取值周期 #6   #RSI 上升算法取值 50
        ('rsi_lower', 23.8),          # RSI 超卖阈值 # 23.8  #RSI上升算法取值 58.7
        ('rsi_lower_deltha', 0.6),    # RSI 超卖阀值所加Delth，shadown算法使用 #过优化后， 0.6
        ('atr_period', 6),          # ATR 取值周期 6
        ('stop_loss_pct', 77),      # shadown 算法里面下影线的长度
        ('shadown_list_len', 6),    # shadown 算法用来比较下影线的前值个数
        ('ma_slow_period', 50),     # 止损均线参数 50
        ('ma_fast_period', 300),

        ('kdj_period', 6),    # KDJ 取值周期  
        ('kdj_smooth_k', 4),   # KDJ K参数
        ('kdj_smooth_d', 4),   # KDJ D参数

        ('init_stop_los_par', 1.3),  #1.3  #ATR策略初始止损参数
        ('init_stop_profit_par', 4), #3.9  #ATR策略初始止盈参数
        ('stop_los_par_plus', 4.6),    #4.4  4.7  #ATR策略跟踪止损参数
        ('stop_profit_par_plus', 3.2), #3.2  3.5  #ATR策略跟踪止盈参数


        # ('rsi_upper', 70),          # RSI 超买阈值
        # ('stddev_period',6),        # 标准差取值周期
        # ('boll_period', 20),        # 布林带周期数  
        # ('boll_dev', 2),            # 布林带参数
        # ('macd_fast', 12),          # MACD快线 参数
        # ('macd_slow', 26),          # MACDman线 参数
        # ('macd_signal', 9),         # MACD信号参数

        ('profit_pct',1.09), #1.04   #ATR比例法止损策略止损参数
        ('loss_pct',0.94),   #0.98   #ATR比例法止损策略止盈参数

        ('init_profit_pct',1.01),  #固定比例止损策略初始止损参数
        ('init_loss_pct',0.96),    #固定比例止损策略跟踪止盈参数
        ('profit_pct_plus',1.02),  #固定比例止损策略跟踪止损参数
        ('loss_pct_plus',0.99),    #固定比例止损策略跟踪止盈参数
        
        ('lowerest_period', 3),    #前期最低值止损策略 前期k线个数
        ('max_loss_pct', 0.99),    #最高比例止损参数
        ('max_duration', 212),     #最长时间止损策略 k线个数，乘以分钟数等于时间

    )

    def __init__(self):
        # Initialize indicators
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        self.slow_ema = bt.indicators.EMA(self.data.close,period = self.params.ma_slow_period)
        self.kdj = KDJ(self.data, period=self.params.kdj_period,
                       smooth_k=self.params.kdj_smooth_k, smooth_d=self.params.kdj_smooth_d)

        # self.lowestind = bt.ind.Lowest(self.data.low, period=self.params.lowerest_period)
        # self.stddev = bt.indicators.StdDev(self.data.close, period=self.params.stddev_period)
        # self.fast_ema = bt.indicators.EMA(self.data.close,period = self.params.ma_fast_period)
        # self.boll = bt.indicators.BollingerBands(self.data.close, period=self.params.boll_period, devfactor=self.params.boll_dev)
        # self.ema = bt.indicators.EMA(self.data.close, period=self.params.ema_period)
        # self.sma = bt.indicators.SMA(self.data.close, period=self.params.ema_period)  # 如果需要简单移动均线
        # self.macd = bt.indicators.MACD(self.data.close, 
        #                                period_me1=self.params.macd_fast, 
        #                                period_me2=self.params.macd_slow, 
        #                                period_signal=self.params.macd_signal)
        # self.adx = bt.indicators.ADX(self.data, period=6)

        self.id_loss_profit_price = LosAndProfitIndicator(self.data, init_value=float('nan'))  # 设置初始nan值默认隐藏线段
        # self.testdata = TestIndicator(self.data, init_value=1)
        # self.id_lost_profit_pct = LosAndProfitPctInd(self.data, init_value= 0)

        # 初始化参数
        self.buy_price = 0
        self.stop_loss_price = 0
        self.stop_profit_price = 0
        self.buy_time = 0
        self.lowest_price = 0

        # 初始化统计变量
        self.max_profit_pct_window = 0 #初始化最大止盈百分比窗口
        self.min_profit_pct_window = 100 #初始化最小止盈百分比窗口
        self.current_pct = 0
        self.lost_pct = 0
        self.profit_pct = 0

    #内置函数，初始化盈利亏损窗口参数
    def _init_profit_window(self):
        self.current_pct = 0
        self.lost_pct = 0
        self.profit_pct = 0

        self.stop_profit_price = 0
        self.stop_loss_price = 0
    #内置函数，将盈利窗口信息更新给指标
    def _update_profit_indicator(self):
        self.id_loss_profit_price.lines.stop_profit_price[0] = self.stop_profit_price if self.stop_profit_price != 0 else float('nan')  #有数据的时候再显示
        self.id_loss_profit_price.lines.stop_loss_price[0] = self.stop_loss_price if self.stop_loss_price !=0 else float('nan')
        # self.testdata.lines.stop_profit_price[0]  = self.current_pct
        # self.id_lost_profit_pct.lines.stop_profit_pct[0] = self.lost_pct
        # self.id_lost_profit_pct.lines.stop_loss_pct[0] = self.profit_pct
        pass
    # 用来计算盈亏比窗口，为indicator使用
    def _caculate_profit_window(self): 
        self.current_pct = (self.stop_profit_price-self.stop_loss_price)*100/self.data.close[0]
        self.lost_pct = (self.stop_loss_price - self.data.close[0])*100/self.data.close[0]
        self.profit_pct = (self.stop_profit_price - self.data.close[0])*100/self.data.close[0]
        if self.current_pct > self.max_profit_pct_window:
            self.max_profit_pct_window = self.current_pct
        if self.current_pct < self.min_profit_pct_window: 
            self.min_profit_pct_window = self.current_pct
    # 内置参数，判断k线是否为下影线
    def _is_lower_shadow(self, data, index):
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
    # 买入条件1， RSI + KDJ + 特定下影线比例
    def _is_buy_condition1_use_shadown(self):
        if self.data.close[0] < self.slow_ema[0]:
            if self.rsi[-1] < self.params.rsi_lower and self.rsi[0] > (self.params.rsi_lower+self.params.rsi_lower_deltha):
                lower_shadow_1 = (self.data.open[0] - self.data.low[0]) / self.data.open[0]
                lower_shadow_2 = (self.data.open[-1] - self.data.low[-1]) / self.data.open[-1]
                if min(lower_shadow_1, lower_shadow_2) > (self.params.stop_loss_pct/100000):
                    if (self._is_lower_shadow(self.data, 0) == True) or (self._is_lower_shadow(self.data, -1) == True ): 
                        low_values = list(self.data.low.get(size=self.params.shadown_list_len))  # 获取前五个 low 值
                        min_value = min(low_values)  # 找到最小值
                        min_index = low_values.index(min_value)  # 找到最小值在列表中的索引
                        relative_index = -len(low_values) + min_index + 1  # 计算相对于当前数据点的索引
                        if relative_index == 0 or relative_index == -1:
                            # if self.kdj.j[-1]<0 and self.kdj.j[0]>0:
                            if self.kdj.j[0] < self.kdj.k[0] and self.kdj.k[0] < self.kdj.d[0]: 
                            # if self.kdj.k[-1] < self.kdj.d[-1] and self.kdj.k[0] > self.kdj.d[0]:
                                return True
        return False
    # 买入条件2， 用来验证RSI比例
    def _is_buy_condition2_use_basicrsi(self):
        if self.rsi[-1] < 10 and self.rsi[0] > 20:
            # if self.kdj.j[0] < self.kdj.k[0] and self.kdj.k[0] < self.kdj.d[0]:
            # if self.kdj.j[-1]<0 and self.kdj.j[0]>0:
            # if self.kdj.k[-1] < self.kdj.d[-1] and self.kdj.k[0] > self.kdj.d[0]:
            # if self.kdj.k[-1] < self.kdj.d[-1] and self.kdj.k[0] > self.kdj.d[0] and self.kdj.j[0] > self.kdj.k[0] and self.kdj.j[0] > self.kdj.d[0]:
                # if self.data.close[0] < self.fast_ema[0]:
                    return True
        return False   
    # 计算止盈止损窗口，集成了ATR，固定比例，ATR比例等止盈止损方法，并可以将初始参数和跟踪参数分开
    def _caculate_profit_loss_parameter(self,is_init = True, mode = 'ATR_Par'):
        #ATR止盈止损方法
        if mode == 'ATR_Par':
            if is_init == True:
                profit_parameter = self.params.init_stop_profit_par
                los_parameter = self.params.init_stop_los_par
            else:
                profit_parameter = self.params.stop_profit_par_plus
                los_parameter = self.params.stop_los_par_plus
            self.stop_profit_price = self.data.close[0] + profit_parameter*self.atr[0]
            self.stop_loss_price = self.data.close[0]-los_parameter*self.atr[0]
        #固定比例止盈止损方法
        if mode == 'Fix_Par':
            if is_init == True:
                self.stop_profit_price = self.data.close[0]*self.p.init_profit_pct
                self.stop_loss_price = self.data.close[0]*self.p.init_loss_pct 
            else:
                self.stop_profit_price = self.data.close[0]*self.p.profit_pct_plus
                self.stop_loss_price = self.data.close[0]*self.p.loss_pct_plus 
        # ATR 百分比止盈方法 
        if mode == 'ATRPct_Par':
            if is_init == True:
                up_parmeter = self.atr[0]*self.p.profit_pct/self.data.open[0]
                down_parmeter = self.atr[0]*self.p.loss_pct/self.data.open[0]
            else:
                up_parmeter = self.atr[0]*self.p.profit_pct/self.data.open[0]
                down_parmeter = self.atr[0]*self.p.loss_pct/self.data.open[0]
            self.stop_profit_price = self.data.close[0]*(1+up_parmeter) 
            self.stop_loss_price = self.data.close[0]*(1-down_parmeter)  
    def next(self):
        current_price = self.data.close[0]
        current_put  = 100*50
        put_size = (current_put/current_price)
        if not self.position:  # 如果未持仓
            if self._is_buy_condition1_use_shadown() == True:
            # if self._is_buy_condition2_use_basicrsi() == True:
                    self.buy_price = self.data.close[0] #open???
                    self.buy_time = len(self)
                    current_put  = 100*50
                    put_size = (current_put/current_price)
                    self.buy(size = put_size)
                    # self._caculate_profit_loss_parameter(is_init=True, mode='ATRPct_Par')  # ATR 百分比止盈方法
                    self._caculate_profit_loss_parameter(is_init = True, mode = 'ATR_Par') # ATR止盈方法                       
                    # self._caculate_profit_loss_parameter(is_init = True, mode = 'Fix_Par') # 固定比例止盈方法

                    # 前期最低值 + 固定盈亏比 止盈止损法
                    # self.stop_profit_price = self.data.close[0]+ (self.data.close[0] - self.lowestind[0])*1.5
                    # self.stop_loss_price = self.data.close[0]- (self.data.close[0] - self.lowestind[0])*1 
                    
                    # 计算盈利窗口，统计用
                    self._caculate_profit_window()

        else:  # 持仓中
            # hold_duration = len(self) - self.buy_time  计算持仓时长
            # current_profit = (self.data.close[0] - self.buy_price)
            if self.data.close[0] >= self.stop_profit_price:
                # self.close() #可以一次盈利后即可止盈
                # self._caculate_profit_loss_parameter(is_init=False, mode='ATRPct_Par')  # ATR 百分比止盈方法                
                self._caculate_profit_loss_parameter(is_init=False, mode='ATR_Par')    # ATR止盈方法                
                # self._caculate_profit_loss_parameter(is_init=False, mode='Fix_Par')   # 固定比例止盈方法

                # 前期最低值 + 固定盈亏比 止盈止损法
                # self.stop_profit_price = self.data.close[0]+ (self.data.close[0] - self.lowestind[0])*1.5
                # self.stop_loss_price = self.data.close[0]- (self.data.close[0] - self.lowestind[0])*1 

                # 计算盈利窗口，统计用
                self._caculate_profit_window() 
            elif (self.data.close[0] < self.stop_loss_price                              # 小于止损值，关闭交易
                #   or self.data.close[0] < (self.buy_price * self.p.max_loss_pct)         #小于最低止损下限，关闭交易 
                #   or (hold_duration >= self.params.max_duration and current_profit <= 0) # 如果持仓时长超过最大时长，且没有盈利，g关闭交易 
                ):
                self.close()
                # 交易结束，重新初始化盈利窗口
                self._init_profit_window() 
        # 更新盈利窗口统计
        self._update_profit_indicator()
    def notify_trade(self, trade):
        # super().notify_trade(trade)
        pass
    def notify_order(self, order):
        #关闭继承的log
        pass

    def stop(self):
        self.close()
        # self.log(f'RSI策略回测结束: 资金 {self.broker.getvalue():.2f}, 余额 {self.broker.getcash():.2f}')



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
