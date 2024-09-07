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

        # print(f'total fit {self.total_profit}, total loss {self.total_loss} max_holding_period {self.max_holding_period} min_holding_period {self.min_holding_period}')
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

        ('init_stop_los_par', 1.3),  #1.3  
        ('init_stop_profit_par', 4), #3.9
        ('stop_los_par_plus', 4.6),    #4.4  4.7
        ('stop_profit_par_plus', 3.2), #3.2  3.5

        ('init_stop_los_par_plus', 0.3), #3.3  #2
        ('init_stop_profit_par_plus', 3.8),
        ('stop_los_par', 0.3),  #参数变得没有意义
        ('stop_profit_par', 3.8),   # 4也一样，参数变得没有意义


        ('atr_earn_multiplier', 1), # ATR 止盈的乘数
        ('atr_los_multiplier',1),   # ATR 止损的乘数

        ('rsi_upper', 70),          # RSI 超买阈值
        ('stddev_period',6),        # 标准差取值周期
        ('boll_period', 20),        
        ('boll_dev', 2),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),

        ('profit_pct',1.09), #1.04  # 2-4之间   #固定比例算法 1.09  #ATR比例法 2.95
        ('loss_pct',0.94),   #0.98             #固定比例算法 0.94  #ATR比例法  4.9

        ('profit_pct_plus',1.02),
        ('loss_pct_plus',0.99),

        ('init_profit_pct',1.01),
        ('init_loss_pct',0.96),
        
        ('init_profit_pct_plus',1.03),
        ('init_loss_pct_plus',0.9),
        ('lowerest_period',62),

    )

    def __init__(self):
        # Initialize indicators
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        # self.stddev = bt.indicators.StdDev(self.data.close, period=self.params.stddev_period)
        # self.fast_ema = bt.indicators.EMA(self.data.close,period = self.params.ma_fast_period)
        self.slow_ema = bt.indicators.EMA(self.data.close,period = self.params.ma_slow_period)
        self.kdj = KDJ(self.data, period=self.params.kdj_period,
                       smooth_k=self.params.kdj_smooth_k, smooth_d=self.params.kdj_smooth_d)

        # self.lowestind = bt.ind.Lowest(self.data.close, period=self.params.lowerest_period)
        # self.boll = bt.indicators.BollingerBands(self.data.close, period=self.params.boll_period, devfactor=self.params.boll_dev)
        # self.ema = bt.indicators.EMA(self.data.close, period=self.params.ema_period)
        # self.sma = bt.indicators.SMA(self.data.close, period=self.params.ema_period)  # 如果需要简单移动均线
        # self.macd = bt.indicators.MACD(self.data.close, 
        #                                period_me1=self.params.macd_fast, 
        #                                period_me2=self.params.macd_slow, 
        #                                period_signal=self.params.macd_signal)
        # self.adx = bt.indicators.ADX(self.data, period=6)

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

        #费用
        self.money_out = 0
        self.money_in = 0

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
        if self.data.close[0] < self.slow_ema[0]:
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
                            # if self.kdj.j[-1]<0 and self.kdj.j[0]>0:
                            if self.kdj.j[0] < self.kdj.k[0] and self.kdj.k[0] < self.kdj.d[0]:  #TODO addation optimize?
                            # if self.kdj.k[-1] < self.kdj.d[-1] and self.kdj.k[0] > self.kdj.d[0]:
                                return True
        return False
    
    def _is_buy_condition2_use_basicrsi(self):
        if self.rsi[-1] < self.p.rsi_lower and self.rsi[0] > self.p.rsi_lower:
            # if self.kdj.j[0] < self.kdj.k[0] and self.kdj.k[0] < self.kdj.d[0]:
            # if self.kdj.j[-1]<0 and self.kdj.j[0]>0:
            # if self.kdj.k[-1] < self.kdj.d[-1] and self.kdj.k[0] > self.kdj.d[0]:
            # if self.kdj.k[-1] < self.kdj.d[-1] and self.kdj.k[0] > self.kdj.d[0] and self.kdj.j[0] > self.kdj.k[0] and self.kdj.j[0] > self.kdj.d[0]:
                # if self.data.close[0] < self.fast_ema[0]:
                    return True
        return False   
    def _caculate_profit_loss_parameter(self,is_init = True, mode = 'ATR_Par'):
        if mode == 'ATR_Par':
            if is_init == True:
                profit_parameter = self.params.init_stop_profit_par
                los_parameter = self.params.init_stop_los_par
            else:
                profit_parameter = self.params.stop_profit_par_plus
                los_parameter = self.params.stop_los_par_plus
            self.stop_profit_price = self.data.close[0] + profit_parameter*self.atr[0]
            self.stop_loss_price = self.data.close[0]-los_parameter*self.atr[0]
        
        if mode == 'Fix_Par':
            if is_init == True:
                self.stop_profit_price = self.data.close[0]*self.p.init_profit_pct
                self.stop_loss_price = self.data.close[0]*self.p.init_loss_pct 
            else:
                # if self.data.close[0] > self.slow_ema[0]:
                    self.stop_profit_price = self.data.close[0]*self.p.profit_pct_plus
                    self.stop_loss_price = self.data.close[0]*self.p.loss_pct_plus 
                # else:
                    # self.stop_profit_price = self.data.close[0]*self.p.profit_pct
                    # self.stop_loss_price = self.data.close[0]*self.p.loss_pct
        
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
        # current_put  = 100*50
       
        # current_put = max(self.broker.getcash(),100)*50
        
        current_put  = 100*50
        put_size = (current_put/current_price)
        # self.log(f'date {self.data.datetime[0]} low {self.data.low[0]} high {self.data.high[0]} open {self.data.open[0]} close {self.data.close[0]} ris {self.rsi[0]}')
        if not self.position:  # 如果未持仓
            if self._is_buy_condition1_use_shadown() == True:
            # if self._is_buy_condition2_use_basicrsi() == True:
                    self.buy_price = self.data.close[0] #open???
                    current_put  = 100*50
                    put_size = (current_put/current_price)
                    self.buy(size = put_size)
                     

                    # self._caculate_profit_loss_parameter(is_init=True, mode='ATRPct_Par')  # ATR 百分比止盈方法
                    self._caculate_profit_loss_parameter(is_init = True, mode = 'ATR_Par') # ATR止盈方法                       
                    # self._caculate_profit_loss_parameter(is_init = True, mode = 'Fix_Par') # 固定比例止盈方法

                    # self.stop_profit_price = self.data.close[0] + (self.data.close[0] - self.lowestind[0])*1
                    # self.stop_loss_price = self.lowestind[0]
                    self._caculate_profit_window()

                    #统计信息：
                    stop_loss_percentage =( (self.buy_price - self.stop_loss_price )/ self.buy_price) * 100
                    if stop_loss_percentage > self.stop_loss_percentage:
                        self.stop_loss_percentage = stop_loss_percentage

                    # dt = bt.num2date(self.data.datetime[0])
                    # self.log(f"{dt}: 买入价格: {self.buy_price} 止损价格：{self.stop_loss_price} shadow1: {lower_shadow_1} shadow2: {lower_shadow_2}")

            

        else:  # 持仓中
            if self.data.close[0] > self.stop_profit_price:
                # self.close()
                # self._caculate_profit_loss_parameter(is_init=False, mode='ATRPct_Par')  # ATR 百分比止盈方法                
                self._caculate_profit_loss_parameter(is_init=False, mode='ATR_Par')    # ATR止盈方法                
                # self._caculate_profit_loss_parameter(is_init=False, mode='Fix_Par')   # 固定比例止盈方法

                # self.stop_loss_price = self.lowestind[0]
                # 计算盈利窗口，统计用
                self._caculate_profit_window()
            # elif self.data.close[0] < self.lowestind[0]:  #or self.data.close[0]< self.fast_ema[0]:  # or self.data.close[0]>self.stop_profit_price:
            elif self.data.close[0] < self.stop_loss_price:  #or self.data.close[0] < self.lowestind[0]:  #or self.data.close[0]< self.fast_ema[0]:  # or self.data.close[0]>self.stop_profit_price:
                self.close()
                # 交易结束后初始化盈利窗口
                self._init_profit_window()
            
            # 统计信息，不参与计算 
            current_drawdown = self.data.open[0] - self.data.low[0]
            current_drawdown_pct = (current_drawdown / self.data.open[0]) * 100  # 转换为百分比

            if current_drawdown > self.max_drawdown:
                self.max_drawdown = current_drawdown
                self.max_drawdown_pct = current_drawdown_pct  # 更新最大振幅的百分比
                
     
        self._update_profit_indicator()


    def notify_trade(self, trade):
        # super().notify_trade(trade)

        # 计算补充本金和提取收益的方法
        # if trade.isclosed: 
        #     current_cash = self.broker.getcash()
        #     if current_cash < 500:
        #         #补充本金
        #         self.money_in = self.money_in + (500-self.broker.getcash())
            
        #     elif current_cash >500:
        #         # 提取收益
        #         self.money_out = self.money_out + (current_cash-500)
        #     self.broker.setcash(500)
        #     self.log(f'当前账户现金: {current_cash} 补充本金：{self.money_in} 提取收益： {self.money_out}')
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
        # self.log(f'策略结束： KDJ_Period {self.p.kdj_period}, KDJ_Smooth_k {self.p.kdj_smooth_k}, KDJ_Smooth_d {self.p.kdj_smooth_d}')
        # self.log(f'策略结束： rsi_lower_deltha {self.p.rsi_lower_deltha}, rsi_lower {self.p.rsi_lower}, stop_loss_pct {self.p.stop_loss_pct}')
        # self.log(f'策略结束： init_stop_los_par {self.p.init_stop_los_par}, init_stop_profit_par {self.p.init_stop_profit_par}, stop_los_par_plus {self.p.stop_los_par_plus}, stop_profit_par_plus {self.p.stop_profit_par_plus}')
        # self.log(f'策略结束： Atr period {self.p.atr_period} rsi_lower {self.p.rsi_lower} Ma_fast_period {self.p.ma_fast_period}')
        # self.log(f'策略结束：profit_pct_plus {self.p.profit_pct_plus} loss_pct_plus {self.p.loss_pct}')
        # self.log(f'profit_pct {self.p.profit_pct}, loss_pct {self.p.loss_pct}，ATR {self.p.atr_period}, slow_ma {self.p.ma_slow_period}')
        # self.log(f'RSI策略回测结束: 资金 {self.broker.getvalue():.2f}, 余额 {self.broker.getcash():.2f}')
        # self.log(f"最大向下振幅: {self.max_drawdown:.2f} ({self.max_drawdown_pct:.2f}%)")
        # self.log(f"止损占仓位的最大百分比: {self.stop_loss_percentage:.2f}%")
        # self.log(f"fast_sma: {self.p.ma_fast_period}")
        self.log(f"lowerest_period: {self.p.lowerest_period}")
        # self.log(f'止盈窗口最小{self.min_profit_pct_window:.2f}%, 止盈窗口最大{self.max_profit_pct_window:.2f}%')
        # self.log(f'补充本金：{self.money_in} 提取收益： {self.money_out}, 最终提取收益：{self.money_out-self.money_in}')



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
