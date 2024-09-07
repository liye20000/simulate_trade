import pandas as pd
import backtrader as bt

def Process_bn_data(filename,from_date = None,to_date=None,start = None, length = None):
    #Prepare binance data to pandas,and from panda to back trader:
    df = pd.read_csv(filename)
    df['opentime'] = pd.to_datetime(df['open_time'],unit='ms')
    df = df.drop(columns=['open_time','close_time','taker_buy_volume','taker_buy_quote_volume','quote_volume'])
    new_order = ['opentime','open','high','low','close','volume','ignore']
    df = df.loc[:,new_order]

    # print("Close min:", df['close'].min())
    # print("Close max:", df['close'].max())


    # 当前处理是先取条数，再看时间
    if start is None and length is None:
        data_slice = df
    elif start is None:
        data_slice = df.iloc[:length]
    elif length is None:
        data_slice = df.iloc[start:]
    else:
        data_slice = df.iloc[start:start + length]


    bndata = bt.feeds.PandasData( dataname=data_slice,
                                fromdate=from_date,
                                todate=to_date,
                                datetime=0,
                                open=1,
                                high=2,
                                low=3,
                                close=4,
                                volume = 5)
    return bndata

if __name__ == '__main__':
    # 函数测试代码
    # bndata = Process_bn_data(filename='data/BTCUSDT-2023-1h.csv',start= 10, length = 10)
    bndata = Process_bn_data(filename='data/BTCUSDT-2023-1h.csv')
    
    # 另外一种方式，直接读取CSV文件
    # data = pd.read_csv('data/btc_usdt_test.csv',parse_dates=['timestamp'],index_col='timestamp')
    # bndata = bt.feeds.PandasData(dataname=data )
    
    
    
    # 打印数据
    print(bndata.p.dataname)
    # import os
    # print(bndata)

    # print("Current working directory:", os.getcwd())
    # file_path = "test_file.txt"
    # with open(file_path, "r") as file:
    #     content = file.read()
    #     print(content)


    # # 时间戳
    # timestamp = 1717018200000
    # # 转换为 pandas 的 Timestamp 对象
    # pandas_timestamp = pd.to_datetime(timestamp, unit='ms')
    # # print("转换后的日期时间为:", pandas_timestamp)




    # print('test...')
    # df = pd.read_csv('bn_test.csv')
    # df['opentime'] = pd.to_datetime(df['open_time'],unit='ms')
    # df = df.drop(columns=['open_time','close_time','taker_buy_volume','taker_buy_quote_volume','quote_volume'])
    # new_order = ['opentime','open','high','low','close','volume','ignore']
    # df = df.loc[:,new_order]
    # # df.set_index('opentime',inplace=True)
    # print(df)



