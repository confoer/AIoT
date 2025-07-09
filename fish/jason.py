import json
import random

# 定义可能的鱼的品种列表
fish_species = ["Chamdom", "Doldom", "Gamseongdom", "Jopi - bollag", "Neobchi"]
# 定义通用的疾病列表，添加了 "health" 表示健康状态
common_diseases = ["health", "bleeding", "eyedefect", "findefect", "ulcer"]
# 非健康疾病列表
non_health_diseases = [d for d in common_diseases if d != "health"]

# 随机生成固定数量的鱼的信息
num_fixed_fishes = 106  # 可以修改这个值来控制固定鱼的数量
fixed_fishes = []

for _ in range(num_fixed_fishes):
    # 随机选择鱼的品种
    species = random.choice(fish_species)
    # 随机生成鱼的长度，范围在 10 到 100 厘米之间
    length = random.randint(10, 100)
    # 计算鱼的重量，使重量和长度正相关
    weight = round(length * length * random.uniform(0.03, 0.04) * random.uniform(0.05, 0.07), 1)

    # 以 90% 的概率让鱼处于健康状态
    if random.random() < 0.9:
        disease = "health"
    else:
        disease = random.choice(non_health_diseases)

    # 拼接成带品种前缀的疾病名称，如果是健康状态则保持原样
    if disease == "health":
        full_disease = disease
    elif species.lower() == "neobchi":
        full_disease = disease
    else:
        full_disease = f"{species.lower()}-{disease}"

    fish_info = {
        "s": species,
        "weight": weight,
        "count": 1,
        "length": length,
        "disease": full_disease
    }
    fixed_fishes.append(fish_info)

# 生成指定数量的识别数据
num_recognitions = 1200  # 可以修改这个值来控制生成的识别数据的数量
all_recognitions = []

for n in range(1, num_recognitions + 1):
    # 随机生成本次识别的鱼的总数，范围在 1 到 10 之间
    total_fish_count = random.randint(1, 10)
    fish_list = []
    available_fishes = fixed_fishes.copy()  # 复制固定鱼列表，避免修改原始列表

    # 确保本次识别中鱼不重复
    for _ in range(min(total_fish_count, len(available_fishes))):
        selected_fish = random.choice(available_fishes)
        fish_list.append(selected_fish)
        available_fishes.remove(selected_fish)

    recognition_data = {
        "n": n,
        "num": len(fish_list),
        "fishes": fish_list
    }
    all_recognitions.append(recognition_data)

# 将数据转换为 JSON 格式
json_data = {"data": all_recognitions}

# 将 JSON 数据保存到文件中
with open('fish_recognition_data.json', 'w') as f:
    json.dump(json_data, f, indent=4)

print("JSON 文件已生成：fish_recognition_data.json")