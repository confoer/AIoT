import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt
import subprocess



def generate_data():
    # 假设数据记录了 365 天（一年）的体重
    num_days = 365
    # 时间序列
    t = np.arange(num_days)
    # 最大理论体重（克）
    L_inf = 2000
    # 生长系数
    k = 0.005
    # 理论上体重为 0 时的时间
    t_0 = 0
    # 根据 Von - Bertalanffy 方程计算体重
    weights = L_inf * (1 - np.exp(-k * (t - t_0)))
    # 添加随机噪声来模拟实际情况中的不确定性
    noise = np.random.normal(0, 5, num_days)
    weights = weights + noise
    # 创建日期索引
    dates = pd.date_range(start='2024-01-01', periods=num_days, freq='D')
    data = pd.DataFrame({'Date': dates, 'Weight': weights})
    return data


# 数据预处理
def preprocess_data(data, time_step=1):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    X, y = [], []
    for i in range(len(scaled_data) - time_step):
        X.append(scaled_data[i:(i + time_step), 0])
        y.append(scaled_data[i + time_step, 0])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X, y, scaler


# 构建 LSTM 模型
def build_model(time_step):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
    model.add(LSTM(50, return_sequences=True))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


# 主函数
def main():
    time_step = 100

    # 生成模拟数据（一年）
    data = generate_data()
    weight = data['Weight'].values.reshape(-1, 1)

    # 数据预处理
    X, y, scaler = preprocess_data(weight, time_step)

    # 划分训练集和测试集
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # 构建模型
    model = build_model(time_step)

    # 训练模型
    model.fit(X_train, y_train, epochs=100, batch_size=64, verbose=1)

    # 预测两年的数据
    num_days_to_predict = 365 * 2
    predictions = []
    current_sequence = X[-1].reshape(1, time_step, 1)
    for _ in range(num_days_to_predict):
        next_prediction = model.predict(current_sequence)
        predictions.append(next_prediction[0, 0])
        current_sequence = np.roll(current_sequence, -1, axis=1)
        current_sequence[0, -1, 0] = next_prediction

    # 反归一化
    predictions = np.array(predictions).reshape(-1, 1)
    predictions = scaler.inverse_transform(predictions)

    # 生成两年的日期索引
    all_dates = pd.date_range(start='2024-01-01', periods=365 + num_days_to_predict, freq='D')

    # 可视化结果
    plt.figure(figsize=(12, 6))
    plt.plot(data['Date'], weight, label='Original Data (Von - Bertalanffy, 1 year)')
    plt.plot(all_dates[365:], predictions, label='Predicted Data (2 years)')
    plt.xlabel('Time')
    plt.ylabel('Weight (g)')
    plt.title('Fish Weight Prediction: 1 - year Data, 2 - year Prediction')
    plt.legend()



if __name__ == "__main__":
    main()
    try:
        subprocess.run(['python', '鲈鱼.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"运行鲈鱼.py 时出错: {e}")