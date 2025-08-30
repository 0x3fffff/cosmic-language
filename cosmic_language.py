class CosmicLanguageCodec:
    """
    通用的块字符编解码器 - 支持所有GB2312字符
    包括：汉字、英文字母、数字、标点符号等
    每个字符编码为5个块字符：4个内容字符 + 1个校验字符
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
        self.char_group_size = 5  # 每个字符占5个块字符

        # 字符类型标识
        self.TYPE_SINGLE_BYTE = 0  # ASCII字符（1字节）
        self.TYPE_DOUBLE_BYTE = 1  # 双字节字符（汉字、全角符号等）

    def _get_char_encoding_info(self, char):
        """获取字符的编码信息"""
        try:
            # 尝试GB2312编码
            gb_bytes = char.encode('gb2312')
            return gb_bytes, len(gb_bytes) == 1
        except UnicodeEncodeError:
            # 如果GB2312失败，尝试GBK
            try:
                gbk_bytes = char.encode('gbk')
                return gbk_bytes, len(gbk_bytes) == 1
            except UnicodeEncodeError:
                # 如果都失败，使用UTF-8作为备选
                utf8_bytes = char.encode('utf-8')
                return utf8_bytes, False

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
        """将单个字符编码为5个块字符"""
        try:
            encoded_bytes, is_single_byte = self._get_char_encoding_info(char)

            if len(encoded_bytes) == 0:
                return '▓▓▓▓▓'  # 错误标记

            # 处理不同长度的字节序列
            if len(encoded_bytes) == 1:
                # 单字节字符（ASCII）
                value = encoded_bytes[0]
                bits = format(value, '08b').zfill(16)  # 补齐到16位
                char_type = self.TYPE_SINGLE_BYTE

            elif len(encoded_bytes) == 2:
                # 双字节字符（大部分汉字和全角符号）
                value = (encoded_bytes[0] << 8) | encoded_bytes[1]
                bits = format(value, '016b')
                char_type = self.TYPE_DOUBLE_BYTE

            elif len(encoded_bytes) == 3:
                # 三字节UTF-8字符，压缩到16位
                value = (encoded_bytes[0] << 16) | (encoded_bytes[1] << 8) | encoded_bytes[2]
                # 使用哈希函数压缩到16位
                compressed = ((value >> 8) ^ (value & 0xFFFF)) & 0xFFFF
                bits = format(compressed, '016b')
                char_type = self.TYPE_DOUBLE_BYTE  # 当作双字节处理

            else:
                # 更长的UTF-8序列，使用哈希压缩
                hash_val = hash(encoded_bytes) & 0xFFFF
                bits = format(hash_val, '016b')
                char_type = self.TYPE_DOUBLE_BYTE

            # 分成4组，每组4位
            blocks = []
            for i in range(0, 16, 4):
                four_bits = bits[i:i + 4]
                block = self.binary_to_block.get(four_bits, '▓')
                blocks.append(block)

            # 计算并添加校验位
            checksum = self._calculate_checksum(blocks, char_type)
            blocks.append(checksum)

            return ''.join(blocks)

        except Exception as e:
            print(f"编码错误 '{char}': {e}")
            return '▓▓▓▓▓'

    def encode_text(self, text):
        """编码整个文本"""
        result = []
        for char in text:
            result.append(self.encode_char(char))
        return ''.join(result)

    def _try_decode_group(self, group):
        """尝试解码一个5字符组"""
        if len(group) != 5:
            return None, False, None

        # 检查是否所有字符都是有效的块字符
        if not all(c in self.block_chars_set for c in group):
            return None, False, None

        content_blocks = group[:4]
        checksum_block = group[4]

        # 尝试两种字符类型
        for char_type in [self.TYPE_SINGLE_BYTE, self.TYPE_DOUBLE_BYTE]:
            if self._verify_checksum(content_blocks, checksum_block, char_type):
                # 解码内容
                try:
                    bits = ''
                    for block in content_blocks:
                        bits += self.block_chars[block]

                    value = int(bits, 2)

                    if char_type == self.TYPE_SINGLE_BYTE:
                        # 单字节字符
                        if value < 256:  # 确保是有效的单字节值
                            decoded_char = bytes([value]).decode('gb2312')
                            return decoded_char, True, char_type
                    else:
                        # 双字节字符
                        if value >= 256:  # 确保是有效的双字节值
                            byte1 = (value >> 8) & 0xFF
                            byte2 = value & 0xFF

                            # 尝试GB2312解码
                            try:
                                decoded_char = bytes([byte1, byte2]).decode('gb2312')
                                return decoded_char, True, char_type
                            except:
                                # 如果GB2312失败，尝试GBK
                                try:
                                    decoded_char = bytes([byte1, byte2]).decode('gbk')
                                    return decoded_char, True, char_type
                                except:
                                    pass

                except Exception as e:
                    continue

        return None, False, None

    def find_valid_start_position(self, encoded_text, start_pos=0):
        """
        从指定位置开始寻找有效的解码起始位置
        返回: (起始位置, 是否找到)
        """
        max_search_range = min(self.char_group_size, len(encoded_text) - start_pos)

        for offset in range(max_search_range):
            pos = start_pos + offset
            if pos + self.char_group_size > len(encoded_text):
                continue

            group = encoded_text[pos:pos + self.char_group_size]
            decoded_char, is_valid, char_type = self._try_decode_group(group)

            if is_valid:
                return pos, True

        return start_pos, False

    def decode_from_position(self, encoded_text, start_pos=0):
        """
        从指定位置开始解码，自动寻找有效起始点
        返回: (解码结果, 实际起始位置, 跳过的字符数, 解码详情)
        """
        # 寻找有效的起始位置
        valid_start, found = self.find_valid_start_position(encoded_text, start_pos)
        skipped_chars = valid_start - start_pos

        if not found:
            return "", start_pos, len(encoded_text) - start_pos, []

        result = []
        decode_details = []
        current_pos = valid_start

        while current_pos + self.char_group_size <= len(encoded_text):
            group = encoded_text[current_pos:current_pos + self.char_group_size]
            decoded_char, is_valid, char_type = self._try_decode_group(group)

            if is_valid:
                result.append(decoded_char)
                type_name = "单字节" if char_type == self.TYPE_SINGLE_BYTE else "双字节"
                decode_details.append({
                    'position': current_pos,
                    'char': decoded_char,
                    'type': type_name,
                    'blocks': group
                })
                current_pos += self.char_group_size
            else:
                # 遇到无效组，尝试寻找下一个有效位置
                next_valid, found_next = self.find_valid_start_position(encoded_text, current_pos + 1)
                if found_next:
                    current_pos = next_valid
                else:
                    break

        return ''.join(result), valid_start, skipped_chars, decode_details

    def decode_text(self, encoded_text, start_pos=0, show_details=False):
        """完整解码文本"""
        result, actual_start, skipped, details = self.decode_from_position(encoded_text, start_pos)
        if show_details:
            return result, actual_start, skipped, details
        return result, actual_start, skipped

    def analyze_text(self, text):
        """分析文本中的字符类型"""
        analysis = {
            'ascii': [],  # ASCII字符
            'chinese': [],  # 汉字
            'symbols': [],  # 符号
            'numbers': [],  # 数字
            'punctuation': [],  # 标点
            'others': []  # 其他
        }

        for char in text:
            try:
                encoded_bytes, is_single = self._get_char_encoding_info(char)

                if is_single and len(encoded_bytes) == 1:
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