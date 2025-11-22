# X/Y/Z 测试数据生成（30行 × 50列）
X = [i for i in range(50)]        # 列标签
Y = [i for i in range(30)]        # 行标签
Z = [[i*j for j in range(50)] for i in range(30)]  # 生成简单测试值：Z[i][j] = i*j

# 输出为可直接复制到 Entry 的字符串
import pprint
print(X)
print(Y)
print(Z)
