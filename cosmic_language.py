class CosmicLanguageCodec:
    """
    通用的块字符编解码器 - 支持所有GB18030字符
    包括：汉字、英文字母、数字、标点符号等
    每个字符编码为多个块字符：每4个内容字符 + 1个校验字符
    """

    def __init__(self):
        # 块字符映射
        self.block_chars = {
            '▀': '1100', '▄': '0011', '█': '1111', '▌': '1010', '▐': '0101',
            '▓': '0000', '▖': '0010', '▗': '0001', '▘': '1000', '▙': '1011',
            '▚': '1001', '▛': '1110', '▜': '1101', '▝': '0100', '▞': '0110', '▟': '0111'
        }

        self.binary_to_block = {v: k for k, v in self.block_chars.items()}
        self.block_chars_set = set(self.block_chars.keys())

        # 字符类型标识
        self.TYPE_SINGLE_BYTE = 0  # ASCII字符（1字节）
        self.TYPE_DOUBLE_BYTE = 1  # 双字节字符（汉字、全角符号等）
        self.TYPE_THREE_BYTE = 2  # 三字节字符
        self.TYPE_FOUR_BYTE = 3  # 四字节字符

    def _get_char_encoding_info(self, char):
        """获取字符的GB18030编码信息"""
        try:
            gb18030_bytes = char.encode('gb18030')
            return gb18030_bytes, len(gb18030_bytes)
        except UnicodeEncodeError:
            # 如果GB18030失败，使用UTF-8作为备选
            utf8_bytes = char.encode('utf-8')
            return utf8_bytes, len(utf8_bytes)

    def _calculate_checksum(self, four_blocks, char_type):
        """计算4个块字符的校验码"""
        checksum = 0
        for block in four_blocks:
            if block in self.block_chars:
                bits_value = int(self.block_chars[block], 2)
                checksum ^= bits_value
        checksum ^= char_type
        parity = bin(checksum).count('1') % 2
        final_checksum = (checksum & 0x7) | (parity << 3)  # 3位值 + 1位奇偶

        return self.binary_to_block.get(format(final_checksum, '04b'), '▓')

    def _verify_checksum(self, four_blocks, checksum_block, char_type):
        """验证校验是否正确"""
        expected_checksum = self._calculate_checksum(four_blocks, char_type)
        return checksum_block == expected_checksum

    def encode_char(self, char):
        """将单个字符编码为块字符"""
        try:
            encoded_bytes, byte_length = self._get_char_encoding_info(char)

            if len(encoded_bytes) == 0:
                return '▓▓▓▓▓'  # 错误标记

            # 根据字节长度处理
            if byte_length == 1:
                # 单字节字符（ASCII）- 补齐到16位
                value = encoded_bytes[0]
                bits = format(value, '016b')  # 直接补齐到16位
                char_type = self.TYPE_SINGLE_BYTE

            elif byte_length == 2:
                # 双字节字符 - 保持16位
                value = (encoded_bytes[0] << 8) | encoded_bytes[1]
                bits = format(value, '016b')
                char_type = self.TYPE_DOUBLE_BYTE

            elif byte_length == 3:
                # 三字节字符 - 高位补0到32位
                value = (encoded_bytes[0] << 16) | (encoded_bytes[1] << 8) | encoded_bytes[2]
                bits = format(value, '032b')  # 补齐到32位
                char_type = self.TYPE_THREE_BYTE

            else:
                # 四字节字符 - 保持32位
                value = 0
                for i, byte_val in enumerate(encoded_bytes[:4]):
                    value |= byte_val << (8 * (3 - i))
                bits = format(value, '032b')
                char_type = self.TYPE_FOUR_BYTE

            # 分组处理：每4位一组，每4组加一个校验位
            result_blocks = []
            for group_start in range(0, len(bits), 16):
                group_bits = bits[group_start:group_start + 16]
                if len(group_bits) < 16:
                    group_bits = group_bits.ljust(16, '0')  # 不足16位补0

                # 分成4组，每组4位
                blocks = []
                for i in range(0, 16, 4):
                    four_bits = group_bits[i:i + 4]
                    block = self.binary_to_block.get(four_bits, '▓')
                    blocks.append(block)

                # 计算并添加校验位
                checksum = self._calculate_checksum(blocks, char_type)
                blocks.append(checksum)

                result_blocks.extend(blocks)

            return ''.join(result_blocks)

        except Exception as e:
            print(f"编码错误 '{char}': {e}")
            return '▓▓▓▓▓'

    def encode_text(self, text):
        """编码整个文本"""
        result = []
        for char in text:
            result.append(self.encode_char(char))
        return ''.join(result)

    def _try_decode_group(self, group, expected_char_type=None):
        """尝试解码一个5字符组（4个内容 + 1个校验）"""
        if len(group) != 5:
            return None, False, None

        # 检查是否所有字符都是有效的块字符
        if not all(c in self.block_chars_set for c in group):
            return None, False, None

        content_blocks = group[:4]
        checksum_block = group[4]

        # 如果指定了字符类型，只尝试该类型
        char_types_to_try = [expected_char_type] if expected_char_type is not None else [
            self.TYPE_SINGLE_BYTE, self.TYPE_DOUBLE_BYTE,
            self.TYPE_THREE_BYTE, self.TYPE_FOUR_BYTE
        ]

        for char_type in char_types_to_try:
            if self._verify_checksum(content_blocks, checksum_block, char_type):
                try:
                    bits = ''
                    for block in content_blocks:
                        bits += self.block_chars[block]

                    value = int(bits, 2)
                    return value, True, char_type

                except Exception:
                    continue

        return None, False, None

    def _decode_character_from_groups(self, groups_data):
        """从多个组数据中解码出字符"""
        if not groups_data:
            return None

        # 根据组数量判断字符类型
        if len(groups_data) == 1:
            # 单组：单字节或双字节
            value, is_valid, char_type = groups_data[0]
            if not is_valid:
                return None

            try:
                if char_type == self.TYPE_SINGLE_BYTE:
                    # 单字节字符，取低8位
                    byte_val = value & 0xFF
                    return bytes([byte_val]).decode('gb18030')
                elif char_type == self.TYPE_DOUBLE_BYTE:
                    # 双字节字符
                    byte1 = (value >> 8) & 0xFF
                    byte2 = value & 0xFF
                    return bytes([byte1, byte2]).decode('gb18030')
            except:
                return None

        elif len(groups_data) == 2:
            # 双组：三字节或四字节
            value1, is_valid1, char_type1 = groups_data[0]
            value2, is_valid2, char_type2 = groups_data[1]

            if not (is_valid1 and is_valid2):
                return None

            try:
                if char_type1 == self.TYPE_THREE_BYTE:
                    # 三字节字符：第一组的低16位 + 第二组的高8位
                    combined_value = (value1 << 16) | value2
                    byte1 = (combined_value >> 16) & 0xFF
                    byte2 = (combined_value >> 8) & 0xFF
                    byte3 = combined_value & 0xFF
                    return bytes([byte1, byte2, byte3]).decode('gb18030')
                elif char_type1 == self.TYPE_FOUR_BYTE:
                    # 四字节字符：两组32位数据
                    combined_value = (value1 << 16) | value2
                    byte1 = (combined_value >> 24) & 0xFF
                    byte2 = (combined_value >> 16) & 0xFF
                    byte3 = (combined_value >> 8) & 0xFF
                    byte4 = combined_value & 0xFF
                    return bytes([byte1, byte2, byte3, byte4]).decode('gb18030')
            except:
                return None

        return None

    def decode_text(self, encoded_text, show_details=False):
        """解码文本"""
        result = []
        decode_details = []
        pos = 0

        while pos + 5 <= len(encoded_text):
            # 尝试解码当前位置的5字符组
            group = encoded_text[pos:pos + 5]
            value, is_valid, char_type = self._try_decode_group(group)

            if is_valid:
                if char_type in [self.TYPE_SINGLE_BYTE, self.TYPE_DOUBLE_BYTE]:
                    # 单组字符
                    char = self._decode_character_from_groups([(value, is_valid, char_type)])
                    if char:
                        result.append(char)
                        if show_details:
                            decode_details.append({
                                'position': pos,
                                'char': char,
                                'type': ['单字节', '双字节', '三字节', '四字节'][char_type],
                                'blocks': group
                            })
                    pos += 5

                elif char_type in [self.TYPE_THREE_BYTE, self.TYPE_FOUR_BYTE]:
                    # 多组字符，需要读取下一组
                    if pos + 10 <= len(encoded_text):
                        next_group = encoded_text[pos + 5:pos + 10]
                        next_value, next_is_valid, next_char_type = self._try_decode_group(next_group, char_type)

                        if next_is_valid:
                            char = self._decode_character_from_groups([
                                (value, is_valid, char_type),
                                (next_value, next_is_valid, next_char_type)
                            ])
                            if char:
                                result.append(char)
                                if show_details:
                                    decode_details.append({
                                        'position': pos,
                                        'char': char,
                                        'type': ['单字节', '双字节', '三字节', '四字节'][char_type],
                                        'blocks': group + next_group
                                    })
                                pos += 10
                                continue

                    # 如果无法读取完整的多组字符，跳过
                    pos += 1
                else:
                    pos += 1
            else:
                pos += 1

        if show_details:
            return ''.join(result), decode_details
        return ''.join(result)

    def analyze_text(self, text):
        """分析文本中的字符类型"""
        analysis = {
            'single_byte': [],  # 单字节字符
            'double_byte': [],  # 双字节字符
            'three_byte': [],  # 三字节字符
            'four_byte': [],  # 四字节字符
            'chinese': [],  # 汉字
            'ascii': [],  # ASCII字符
            'symbols': [],  # 符号
            'numbers': [],  # 数字
            'punctuation': [],  # 标点
            'others': []  # 其他
        }

        for char in text:
            try:
                encoded_bytes, byte_length = self._get_char_encoding_info(char)

                # 按字节长度分类
                if byte_length == 1:
                    analysis['single_byte'].append(char)
                elif byte_length == 2:
                    analysis['double_byte'].append(char)
                elif byte_length == 3:
                    analysis['three_byte'].append(char)
                elif byte_length == 4:
                    analysis['four_byte'].append(char)

                # 按字符类型分类
                if byte_length == 1 and len(encoded_bytes) == 1:
                    code = encoded_bytes[0]
                    if 32 <= code <= 126:  # 可打印ASCII
                        if '0' <= char <= '9':
                            analysis['numbers'].append(char)
                        elif 'A' <= char <= 'Z' or 'a' <= char <= 'z':
                            analysis['ascii'].append(char)
                        elif char in '.,;:!?()[]{}"\'-':
                            analysis['punctuation'].append(char)
                        else:
                            analysis['symbols'].append(char)
                    else:
                        analysis['others'].append(char)
                else:
                    if '\u4e00' <= char <= '\u9fff':
                        analysis['chinese'].append(char)
                    elif char in '，。；：！？（）【】""''':
                        analysis['punctuation'].append(char)
                    else:
                        analysis['symbols'].append(char)

            except:
                analysis['others'].append(char)

        return analysis

