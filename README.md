# 宇宙语 (Cosmic Language) 🌌

> 一种基于方块字符的通用编码系统，将GB2312/GBK字符转换为视觉化的"宇宙文字"

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎥 演示视频

**B站介绍视频**: [▀▛▜▖▝▙▟▌▖▐▀▄█▟▞▀▗▀▙▙▜▄▛▛▟▜▞▛▞▌▜▄▛█▛▌▄▌▗▄](https://www.bilibili.com/video/BV1mMhizrE7h)

## 🌐 在线体验

**在线翻译器**: [http://dx3906.world](http://dx3906.world)

## 📖 项目简介

宇宙语是一个创新的字符编码系统，它将传统的GB2312/GBK编码转换为由16种不同方块字符组成的视觉化符号。每个原始字符都被编码为5个方块字符，形成了一种独特的"外星文字"效果。

### ✨ 特性

- 🎯 **通用支持**: 完整支持GB2312/GBK字符集，包括汉字、英文、数字、标点符号
- 🔧 **容错机制**: 内置校验系统，支持错误检测和自动修复
- 🎨 **视觉美观**: 使用16种不同的方块字符，形成独特的视觉效果
- 🔍 **智能解析**: 自动识别字符类型（单字节/双字节）
- 🛡️ **数据完整性**: 每个字符包含校验位，确保编解码准确性

## 🏗️ 编码原理

### 方块字符映射表

宇宙语使用16种Unicode方块字符，每种对应一个4位二进制值：

```
▀ → 1100    ▄ → 0011    █ → 1111    ▌ → 1010
▐ → 0101    ▓ → 0000    ▖ → 0010    ▗ → 0001
▘ → 1000    ▙ → 1011    ▚ → 1001    ▛ → 1110
▜ → 1101    ▝ → 0100    ▞ → 0110    ▟ → 0111
```

### 编码流程

1. **字符分析**: 识别字符类型（ASCII单字节 vs 汉字双字节）
2. **字节转换**: 将字符转换为GB2312/GBK字节序列
3. **位分组**: 将字节序列转换为16位二进制，分成4组（每组4位）
4. **方块映射**: 每组4位对应一个方块字符
5. **校验生成**: 计算前4个方块的校验和，生成第5个校验方块

### 编码格式

```
原字符 → [4个内容方块] + [1个校验方块] = 5个方块字符
```

**示例**:
- 字符 'A' → `▓▓▝▗▐`
- 字符 '中' → `▜▞▜▓█`

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/0x3fffff/cosmic-language.git
cd cosmic-language
```

### 基本使用

```python
from cosmic_language import CosmicLanguageCodec

# 创建编解码器实例
codec = CosmicLanguageCodec()

# 编码文本
text = "Hello 世界!"
encoded = codec.encode_text(text)
print(f"原文: {text}")
print(f"宇宙语: {encoded}")

# 解码文本
decoded, start_pos, skipped = codec.decode_text(encoded)
print(f"解码结果: {decoded}")
```


## 📊 编码示例

| 原字符 | 类型 | 字节值 | 二进制表示 | 宇宙语编码 |
|--------|------|--------|------------|------------|
| A | ASCII | 0x41 | 0000000001000001 | ▓▓▝▗▐ |
| 中 | 汉字 | 0xD6D0 | 1101011011010000 | ▜▞▜▓█ |
| ！ | 全角 | 0xA3A1 | 1010001110100001 | ▌▄▌▗▄ |

## 🔧 技术细节

### 字符类型识别

- **单字节字符** (TYPE_SINGLE_BYTE = 0): ASCII字符，编码值 < 128
- **双字节字符** (TYPE_DOUBLE_BYTE = 1): 汉字、全角符号等

### 校验算法

校验系统采用XOR异或运算结合奇偶校验：

```python
checksum = 0
for block in four_blocks:
    checksum ^= int(block_binary_value, 2)
checksum ^= char_type  # 添加类型信息
parity = bin(checksum).count('1') % 2
final_checksum = (checksum & 0x7) | (parity << 3)
```

### 容错机制

- **智能起始点检测**: 自动寻找有效的解码起始位置
- **错误跳过**: 遇到无效字符组时自动跳过并继续解码
- **校验验证**: 每个字符组都经过校验验证，确保数据完整性

## 🎨 视觉效果

宇宙语的方块字符在不同字体下呈现出独特的视觉效果：

```
普通文本: 你好，世界！
宇宙语版: ▀▝▛▄▀▙▌▀▄▟▌▄▌▀▛▀▌▀▓▙▙▜▛▟▛▌▄▌▗▄
```


## 🌟 应用场景

- **艺术创作**: 将文本转换为独特的视觉艺术形式
- **密码学习**: 理解字符编码和校验机制
- **教育工具**: 可视化字符编码过程
- **创意设计**: 为设计项目添加"外星文字"效果
- **数据隐写**: 在方块字符中隐藏信息


## 🐛 已知问题

- 某些生僻汉字可能需要使用GBK编码
- 非常长的文本编码后会显著增长（5倍长度）
- 部分emoji和特殊Unicode字符需要特殊处理

## 📜 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

## 👨‍💻 作者

- **原创者**: [0x3fffff]([https://example.com/encoding-principles](http://ox3fffff.cn/))
- **项目灵感**: 看到抖音的翻译会将方块字翻译成人物简介的Ai幻觉

## ⭐️ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=0x3fffff/cosmic-language&type=Date)](https://www.star-history.com/#0x3fffff/cosmic-language&Date)

---

**如果你觉得这个项目有趣，请给它一个 ⭐️！**

---

*让我们一起将宇宙语发扬光大，让Ai可以真正翻译方块字符！* 🚀✨
