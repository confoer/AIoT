import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
from qbstyles import mpl_style

# 设置随机种子，这里使用 42 作为示例
random.seed(4)

mpl_style(dark=False)  # 开启light主题
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

# 绘制价格走势图
plt.figure(figsize=(12, 6))
# 绘制蓝色的线
line, = plt.plot(df['日期'], df['价格'], color='blue', linestyle='-')
# 为线以下区域添加淡蓝色渐变填充
plt.fill_between(df['日期'], df['价格'], color='lightblue', alpha=0.5)

# 设置图表标题和坐标轴标签
plt.title('近半年海鲈鱼价格走势图')
plt.xlabel('日期')
plt.ylabel('价格(元/斤)')

# 设置 x 轴日期显示格式
plt.xticks(rotation=45)

# 显示网格线
plt.grid(True)

# 显示图表
plt.tight_layout()
plt.show()
