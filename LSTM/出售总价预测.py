import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
from qbstyles import mpl_style

# 设置随机种子，保证结果可复现
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

# 随机生成每天的销售量
sales_volumes = [random.randint(5000, 5200) for _ in range(len(date_range))]

# 计算每天的出售总价
total_sales_prices = [price * volume for price, volume in zip(prices, sales_volumes)]

data = {
    '日期': date_range,
    '出售总价': total_sales_prices
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
last_price = prices[-1]
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

# 随机生成未来半年每天的销售量
future_sales_volumes = [random.randint(5000, 5200) for _ in range(len(future_date_range))]

# 计算未来半年每天的出售总价
future_total_sales_prices = [price * volume for price, volume in zip(future_prices, future_sales_volumes)]

future_data = {
    '日期': future_date_range,
    '出售总价': future_total_sales_prices
}
future_df = pd.DataFrame(future_data)

# 合并过去和未来的数据
combined_df = pd.concat([df, future_df], ignore_index=True)

# 找到最高点
max_point = combined_df['出售总价'].idxmax()
max_date = combined_df.loc[max_point, '日期']
max_price = combined_df.loc[max_point, '出售总价']

# 绘制出售总价走势图
plt.figure(figsize=(12, 6))
# 绘制蓝色的线表示过去半年出售总价
line, = plt.plot(df['日期'], df['出售总价'], color='blue', linestyle='-', label='过去半年总利润')
# 为线以下区域添加淡蓝色渐变填充
plt.fill_between(df['日期'], df['出售总价'], color='lightblue', alpha=0.5)
# 绘制红色的线表示未来半年出售总价预测
plt.plot(future_df['日期'], future_df['出售总价'], color='red', linestyle='-', label='未来半年总利润预测')
# 为红色线条下方区域添加淡红色渐变填充
plt.fill_between(future_df['日期'], future_df['出售总价'], color='lightcoral', alpha=0.5)

# 绘制横纵坐标虚线
plt.axvline(x=max_date, color='gray', linestyle='--')
plt.axhline(y=max_price, color='gray', linestyle='--')

# 标注最高点的出售日期与价格，增大字体大小，减小 shrink 值使箭头边长变长
plt.annotate(f'日期: {max_date.strftime("%Y-%m-%d")}\n价格: {max_price:.2f} 元',
             xy=(max_date, max_price),
             xytext=(max_date + timedelta(days=10), max_price * 0.8),
             arrowprops=dict(facecolor='black', shrink=0.001),  # 箭头边长变长
             fontsize=15)  # 字体大小增大到 12

# 设置图表标题和坐标轴标签
plt.title('海鲈鱼出售利润走势图')
plt.xlabel('日期')
plt.ylabel('出售总价(元)')

# 设置 x 轴日期显示格式
plt.xticks(rotation=45)

# 显示网格线
plt.grid(True)

# 显示图例
plt.legend(fontsize=15)

# 显示图表
plt.tight_layout()
plt.show()