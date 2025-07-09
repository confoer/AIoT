import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
from qbstyles import mpl_style

# 设置随机种子，这里使用 4 作为示例
random.seed(4)

mpl_style(dark=False)  # 开启 light 主题
plt.rcParams['font.sans-serif'] = ['SimHei']
# 解决负号显示问题
plt.rcParams['axes.unicode_minus'] = False

# 生成近半年模拟数据
end_date = datetime.now()
start_date = end_date - timedelta(days=180)
date_range = pd.date_range(start=start_date, end=end_date)
prices = []
current_price = 12.4
i = 0
while i < len(date_range):
    # 随机决定连续增长或下降的天数
    consecutive_days = random.randint(7, 15)
    # 随机决定是增长还是下降
    is_increase = random.choice([True, False])
    # 随机生成变化率
    change_rate = random.uniform(0.001, 0.005)

    for _ in range(consecutive_days):
        if i >= len(date_range):
            break
        if is_increase:
            current_price *= (1 + change_rate)
        else:
            current_price *= (1 - change_rate)
        prices.append(current_price)
        i += 1

data = {
    '日期': date_range,
    '价格': prices
}
df = pd.DataFrame(data)

# 将日期列转换为日期类型
df['日期'] = pd.to_datetime(df['日期'])

# 按日期排序
df = df.sort_values(by='日期')

# 生成未来半年的日期序列
future_end_date = end_date + timedelta(days=180)
future_date_range = pd.date_range(start=end_date + timedelta(days=1), end=future_end_date)

# 以当前最后价格为基础，随机生成未来半年价格
future_prices = []
last_price = df['价格'].iloc[-1]
current_price = last_price
i = 0
while i < len(future_date_range):
    # 随机决定连续增长或下降的天数
    consecutive_days = random.randint(7, 15)
    # 随机决定是增长还是下降
    is_increase = random.choice([True, False])
    # 随机生成变化率
    change_rate = random.uniform(0.001, 0.005)

    for _ in range(consecutive_days):
        if i >= len(future_date_range):
            break
        if is_increase:
            current_price *= (1 + change_rate)
        else:
            current_price *= (1 - change_rate)
        future_prices.append(current_price)
        i += 1

future_data = {
    '日期': future_date_range,
    '价格': future_prices
}
future_df = pd.DataFrame(future_data)

# 绘制价格走势图
plt.figure(figsize=(12, 6))

# 绘制蓝色的线表示过去半年价格，并填充淡蓝色
line, = plt.plot(df['日期'], df['价格'], color='blue', linestyle='-', label='过去半年价格')
plt.fill_between(df['日期'], df['价格'], color='lightblue', alpha=0.5)  # 原有填充

# 绘制红色的线表示未来半年预测价格，并填充淡红色
plt.plot(future_df['日期'], future_df['价格'], color='red', linestyle='-', label='未来半年预测价格')
plt.fill_between(future_df['日期'], future_df['价格'], color='lightcoral', alpha=0.3)  # 新增的红色填充

# 设置图表标题和坐标轴标签等（保持不变）
plt.title('LSTM预测海鲈鱼价格走势')
plt.xlabel('日期')
plt.ylabel('价格(元/斤)')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()
