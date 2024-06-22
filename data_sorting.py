import pandas as pd
from tabulate import tabulate

class DataCollector:
    def __init__(self, *args):
        self.columns = args
        self.data = {column: [] for column in self.columns}
    
    def append(self, *values):
        if len(values) != len(self.columns):
            raise ValueError("Number of values must match number of columns")
        for column, value in zip(self.columns, values):
            self.data[column].append(value)
    
    def sort_data(self, primary_key, secondary_key, primary_ascending=True, secondary_ascending=True):
        df = pd.DataFrame(self.data)
        sorted_df = df.sort_values(
            by=[primary_key, secondary_key],
            ascending=[primary_ascending, secondary_ascending]
        )
        return sorted_df
    
    def print_all(self, primary_key, secondary_key, primary_ascending=True, secondary_ascending=True):
        sorted_df = self.sort_data(primary_key, secondary_key, primary_ascending, secondary_ascending)
        print(tabulate(sorted_df, headers='keys', tablefmt='pretty', showindex=True))
        # print(sorted_df.to_string(justify='left'))
    
    def print_top_n(self, n, primary_key, secondary_key, primary_ascending=True, secondary_ascending=True):
        sorted_df = self.sort_data(primary_key, secondary_key, primary_ascending, secondary_ascending)
        print(tabulate(sorted_df.head(n), headers='keys', tablefmt='pretty', showindex=True))
        # print(sorted_df.head(n).to_string(justify='middle'))

if __name__ == '__main__':
    # 使用示例
    # 假设我们有三列：盈利金额、亏损金额、持有天数
    collector = DataCollector('盈利金额', '亏损金额', '持有天数')

    # 模拟数据收集
    collector.append(100, 50, 10)
    collector.append(200, 60, 20)
    collector.append(150, 40, 15)
    collector.append(120, 70, 5)

    # 打印所有数据，按照盈利金额由高到低排序，亏损金额由低到高排序
    collector.print_all('盈利金额', '亏损金额', primary_ascending=False, secondary_ascending=True)

    # 打印前三条数据，按照盈利金额由高到低排序，亏损金额由低到高排序
    collector.print_top_n(3, '盈利金额', '亏损金额', primary_ascending=False, secondary_ascending=True)