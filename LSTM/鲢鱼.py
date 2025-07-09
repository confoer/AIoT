import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import mplcyberpunk


# 将字体设置为黑体


# Von - Bertalanffy 方程计算体长
def von_bertalanffy_length(t, L_inf, k, t_0):
    return L_inf * (1 - np.exp(-k * (t - t_0)))


# 根据体长计算体重
def length_to_weight(L, a, b):
    return a * (L ** b)


# 生成数据
def generate_data():
    # 时间范围，两年共 730 天
    t = np.arange(0, 365 * 3)
    # 转换为日期
    dates = pd.date_range(start='2024-01-01', periods=365 * 3, freq='D')

    # 体长相关参数，调小生长系数 k 让生长速度变慢
    L_inf_length = 40  # 最大理论体长（厘米）
    k_length = 0.003  # 体长生长系数，调小该值减缓生长速度
    t_0_length = 0  # 理论上体长为 0 时的时间

    # 体重相关参数
    a = 1  # 体重 - 体长关系中的常数 a
    b = 2.2  # 体重 - 体长关系中的常数 b

    # 计算体长和体重
    lengths = von_bertalanffy_length(t, L_inf_length, k_length, t_0_length)
    weights = length_to_weight(lengths, a, b)

    # 为体长和体重添加抖动
    length_jitter = np.random.normal(0, 0.5, lengths.shape)
    weight_jitter = np.random.normal(0, 20, weights.shape)
    lengths_with_jitter = lengths + length_jitter
    weights_with_jitter = weights + weight_jitter

    return dates, lengths, weights, lengths_with_jitter, weights_with_jitter


# 主函数
def main():
    dates, lengths, weights, lengths_with_jitter, weights_with_jitter = generate_data()
    plt.style.use("cyberpunk")  # 调用cyberpunk style
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False
    # 创建图形和坐标轴
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 绘制预测体长曲线
    color_pred_length = 'white'
    # 设置 x 轴标签字体大小
    ax1.set_xlabel('时间', fontsize=14)
    # 设置 y 轴标签字体大小
    ax1.set_ylabel('体长 (cm)', color=color_pred_length, fontsize=14)
    ax1.plot(dates, lengths, color=color_pred_length, label='预测体长', linewidth=2)

    # 找到2025-03-01对应的索引
    target_date = pd.Timestamp('2025-03-01')
    try:
        target_index = dates.tolist().index(target_date) + 1
    except ValueError:
        print(f"未找到日期 {target_date}")
        target_index = len(dates)

    color_orig_length = 'orange'
    ax1.plot(dates[:target_index], lengths_with_jitter[:target_index], color=color_orig_length, label='原始数据体长 ',
             linestyle='--')
    # 设置 y 轴刻度标签字体大小
    ax1.tick_params(axis='y', labelcolor=color_pred_length, labelsize=12)
    # 设置 x 轴刻度标签字体大小
    ax1.tick_params(axis='x', labelsize=12)

    # 创建第二个纵坐标（体重）
    ax2 = ax1.twinx()
    color_pred_weight = 'yellow'
    # 设置第二个 y 轴标签字体大小
    ax2.set_ylabel('体重 (g)', color=color_pred_weight, fontsize=14)
    ax2.plot(dates, weights, color=color_pred_weight, label='预测体重', linewidth=2)
    color_orig_weight = 'cyan'
    ax2.plot(dates[:target_index], weights_with_jitter[:target_index], color=color_orig_weight, label='原始数据体重',
             linestyle='--')
    # 设置第二个 y 轴刻度标签字体大小
    ax2.tick_params(axis='y', labelcolor=color_pred_weight, labelsize=12)

    # 设置 x 轴日期格式
    date_format = DateFormatter("%Y-%m")
    ax1.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()

    # 添加图例，设置图例字体大小
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines = lines1 + lines2
    labels = labels1 + labels2
    ax1.legend(lines, labels, loc='upper left', fontsize=12)

    # 设置标题字体大小
    plt.title('鲢鱼体重与体长预测', fontsize=16)
    plt.show()


if __name__ == "__main__":
    main()
