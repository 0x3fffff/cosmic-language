# Cosmic Language 🌌
> A universal encoding system based on block characters that converts characters into visualized "cosmic text"

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🔠 Language
- [English](README.EN.md)
- [中文](README.md)

## 🎥 Demo Video
**Bilibili Introduction Video**: [▀▛▜▖▝▙▟▌▖▐▀▄█▟▞▀▗▀▙▙▜▄▛▛▟▜▞▛▞▌▜▄▛█▛▌▄▌▗▄](https://www.bilibili.com/video/BV1mMhizrE7h)

## 🌐 Online Experience
**Online Translator**: [http://dx3906.world](http://dx3906.world)

## 📖 Project Overview
Cosmic Language is an innovative character encoding system that converts traditional GB18030 (It includes all Unicode encodings) encoding into visualized symbols composed of 16 different block characters. Each original character is encoded as 5 block characters, creating a unique "alien text" effect.

### ✨ Features
- 🎯 **Universal Support**: Full support for GB18030 character sets, including the vast majority of rare Chinese characters and various characters in Unicode
- 🔧 **Error Tolerance**: Built-in validation system with error detection and automatic correction
- 🎨 **Visual Appeal**: Uses 16 different block characters to create unique visual effects
- 🔍 **Smart Parsing**: Automatic character type recognition (single-byte/double-byte)
- 🛡️ **Data Integrity**: Each character includes checksum bits to ensure encoding/decoding accuracy

## 🏗️ Encoding Principles

### Block Character Mapping Table
Cosmic Language uses 16 Unicode block characters, each corresponding to a 4-bit binary value:

```
▀ → 1100    ▄ → 0011    █ → 1111    ▌ → 1010
▐ → 0101    ▓ → 0000    ▖ → 0010    ▗ → 0001
▘ → 1000    ▙ → 1011    ▚ → 1001    ▛ → 1110
▜ → 1101    ▝ → 0100    ▞ → 0110    ▟ → 0111
```

### Encoding Process
1. **Character Analysis**: Identify character type (ASCII single-byte vs Chinese double-byte)
2. **Byte Conversion**: Convert character to GB18030 byte sequence
3. **Bit Grouping**: Convert byte sequence to 16-bit binary, split into 4 groups (4 bits each)
4. **Block Mapping**: Each 4-bit group corresponds to one block character
5. **Checksum Generation**: Calculate checksum of the first 4 blocks to generate the 5th checksum block

### Encoding Format
```
Original Character → [4 Content Blocks] + [1 Checksum Block] = 5 Block Characters
or
Original Character → [4 Content Blocks] + [1 Checksum Block] + [4 Content Blocks] + [1 Checksum Block] = 10 Block Characters
```

**Examples**:
- Character 'A' → `▓▓▝▗▐`
- Character '中' → `▜▞▜▓█`
- Character '㐀' → `▘▗▄▚▓▛▛▄▚▗`
- Character '🥰' → `▚▐▄▓▝▜▞▄▞▜`

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/0x3fffff/cosmic-language.git
cd cosmic-language
```

### Basic Usage
```python
from cosmic_language import CosmicLanguageCodec

# Create codec instance
codec = CosmicLanguageCodec()

# Encode text
text = "Hello 世界!"
encoded = codec.encode_text(text)
print(f"Original: {text}")
print(f"Cosmic Language: {encoded}")

# Decode text
decoded = codec.decode_text(encoded)
print(f"Decoded: {decoded}")
```

## 📊 Encoding Examples

| Original | Type | Byte Value | Binary Representation | Cosmic Encoding |
|----------|------|------------|----------------------|-----------------|
| A | ASCII | 0x41 | 0000000001000001 | ▓▓▝▗▐ |
| 中 | Chinese | 0xD6D0 | 1101011011010000 | ▜▞▜▓█ |
| ！ | Full-width | 0xA3A1 | 1010001110100001 | ▌▄▌▗▄ |
| 🥰 | emoji | 0x9530D636 | 10010101001100001101011000110110 | ▚▐▄▓▝▜▞▄▞▜ |

## 🔧 Technical Details

### Character Type Recognition
- **Single-byte Characters** (TYPE_SINGLE_BYTE = 0): ASCII characters.
- **Double-byte Characters** (TYPE_DOUBLE_BYTE = 1): Chinese characters, full-width symbols, etc.
- **Four-byte Characters** (TYPE_DOUBLE_BYTE = 3): All kinds of rare characters, symbols and expressions, etc.

### Checksum Algorithm
The validation system uses XOR operations combined with parity checking:

```python
checksum = 0
for block in four_blocks:
    checksum ^= int(block_binary_value, 2)
checksum ^= char_type  # Add type information
parity = bin(checksum).count('1') % 2
final_checksum = (checksum & 0x7) | (parity << 3)
```

### Error Tolerance Mechanism
- **Smart Start Point Detection**: Automatically finds valid decoding starting positions
- **Error Skipping**: Automatically skips invalid character groups and continues decoding
- **Checksum Validation**: Each character group undergoes checksum validation to ensure data integrity

## 🎨 Visual Effects
Cosmic Language block characters present unique visual effects in different fonts:

```
Regular Text: 你好，世界！
Cosmic Version: ▀▝▛▄▀▙▌▀▄▟▌▄▌▀▛▀▌▀▓▙▙▜▛▟▛▌▄▌▗▄
```

## 🌟 Use Cases
- **Artistic Creation**: Convert text into unique visual art forms
- **Cryptographic Learning**: Understand character encoding and validation mechanisms
- **Educational Tool**: Visualize the character encoding process
- **Creative Design**: Add "alien text" effects to design projects
- **Data Steganography**: Hide information within block characters

## 🐛 Known Issues
- None

## 📜 License
This project is open source under the [MIT License](LICENSE).

## 👨‍💻 Author
- **Creator**: [0x3fffff](http://ox3fffff.cn/)
- **Project Inspiration**: Inspired by observing AI hallucinations where translation apps would translate block characters into character descriptions on TikTok

## ⭐️ Star History
[![Star History Chart](https://api.star-history.com/svg?repos=0x3fffff/cosmic-language&type=Date)](https://www.star-history.com/#0x3fffff/cosmic-language&Date)

---
**If you find this project interesting, please give it a ⭐️!**

---
*Let's promote Cosmic Language together and enable AI to truly translate block characters!* 🚀✨
