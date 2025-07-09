import numpy as np
import time

# 定义矩阵和向量
A = np.array([[4, -1, 0],
              [-1, 4, -1],
              [0, -1, 4]], dtype=float)
b = np.array([15, 10, 10], dtype=float)

# 步骤二：高斯消元法（直接解法）
start_time = time.time()
x_gauss = np.linalg.solve(A, b)
gauss_time = time.time() - start_time

# 步骤三：雅可比迭代法
def jacobi(A, b, max_iter=1000, tol=1e-6):
    n = len(b)
    x = np.zeros(n)
    x_new = np.zeros(n)
    for it in range(max_iter):
        for i in range(n):
            sigma = np.dot(A[i, :], x) - A[i, i] * x[i]  # 计算非对角项的和
            x_new[i] = (b[i] - sigma) / A[i, i]
        # 检查收敛条件
        if np.linalg.norm(x_new - x, np.inf) < tol:
            break
        x = x_new.copy()  # 深拷贝更新解
    return x_new, it + 1

start_time = time.time()
x_jacobi, iterations = jacobi(A, b)
jacobi_time = time.time() - start_time

# 步骤四：结果验证与分析
error = np.linalg.norm(x_gauss - x_jacobi)
print("直接解法（高斯消元）的解：", x_gauss)
print("迭代解法（雅可比）的解：", x_jacobi)
print("解的差异范数：", error)
print("\n求解时间比较：")
print(f"高斯消元法：{gauss_time:.6f} 秒")
print(f"雅可比迭代法：{jacobi_time:.6f} 秒")
print(f"雅可比迭代次数：{iterations} 次")

# 收敛情况分析
if iterations < 1000:
    print("\n雅可比迭代在指定精度内收敛。")
else:
    print("\n雅可比迭代未在最大次数内收敛。")