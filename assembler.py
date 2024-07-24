# 注：所有数据采用小端在左的编码格式，例如：3 -> 1100, 4 -> 0010 

class Assembler():
    def __init__(self):
        self.op_codes = {
            'nop': '0000',
            'add': '1000',
            'sub': '0100',
            'and': '1100',
            'or': '0010',
            'sta': '1010',
            'lda': '0110',
            '>>': '1110',
            '<<': '0001',
            '==': '1001',
            '!=': '0101',
            'gpu': '1101',
            'jmp': '11'
        }
        # 所有寄存器的最高位地址（最右边）都置为1
        # 所有立即数的最高位地址（最右边）都置为0
        self.registers = {
            'score': '0001',
            'key': '1001',
            'r0': '0101',
            'r1': '1101',
            'r2': '0011',
            'r3': '1011',
            'rand': '0111',
            'r4': '1111'
        }

    def parse_int(self, num):
        if num < 0 or num > 7:
            raise Exception('错误：整数 {} 超出处理器支持的范围'.format(num))
        res = ''
        for i in range(4):
            res += str(num % 2)
            num = num // 2
        return res

    def parse_addr(self, addr):
        if addr < 0 or addr > 64:
            raise Exception('错误：地址 {} 超出处理器支持的范围'.format(addr))
        high, low = '', ''
        for i in range(4):
            low += str(addr % 2)
            addr = addr // 2
        for i in range(2):
            high += str(addr % 2)
            addr = addr // 2
        return high, low

    def filter_comments(self, raw_codes: str):
        pos = raw_codes.find('//')
        if pos >= 0:
            code = raw_codes[:pos]
        else:
            code = raw_codes
        code = code.strip(' ').strip('\t')
        return code

    def assemble(self, codes: str):
        self.labels = {}
        asm_pos = 0
        asm_codes = ''
        # Collect labels.
        for raw_code in codes.split('\n'):
            raw_code = raw_code.strip('\r')
            code = self.filter_comments(raw_code)
            if code.endswith(':'):
                label = code.replace(':', '')
                if label in self.labels:
                    raise Exception('错误：重复定义的 label:{}'.format(label))
                self.labels[label] = asm_pos
            if code != '' and not code.endswith(':'):
                asm_pos += 1
        # Parse operations.
        line_num = 0
        asm_pos = 0
        for raw_code in codes.split('\n'):
            raw_code = raw_code.strip('\r')
            code = self.filter_comments(raw_code)
            print('正在编译代码：{}'.format(code))
            if code == '':
                asm_codes += '\n'
            elif code.endswith(':'):
                asm_codes += '{}\n'.format(code)
            else:
                ops = code.split(' ')
                op = ops[0]
                if op not in self.op_codes:
                    raise Exception('line {} >> 错误：不支持的操作 {}'.format(line_num, op))
                op_code = self.op_codes[op]
                op_data = '0000'
                if op == 'nop':
                    pass
                elif op == 'lda':
                    if ops[1] in self.registers:
                        op_data = self.registers[ops[1]]
                    else:
                        raise Exception('line {} >> 错误：无效的操作数 {}'.format(line_num, ops[1]))
                elif op == 'gpu':
                    if ops[1] == 'set':
                        op_data = '1000'
                elif op == 'jmp':
                    label = code.replace('jmp ', '')
                    if label not in self.labels:
                        raise Exception('line {} >> 错误：找不到要跳转的位置 {}'.format(line_num, label))
                    jmp_addr = self.labels[label]
                    high, low = self.parse_addr(jmp_addr)
                    op_code = high + self.op_codes[op]
                    op_data = low
                else:
                    if ops[1] in self.registers:
                        op_data = self.registers[ops[1]]
                    elif ops[1].isdecimal():
                        op_data = self.parse_int(int(ops[1]))
                    else:
                        raise Exception('line {} >> 错误：无效的操作数 {}'.format(line_num, ops[1]))
                asm = op_code + '  ' + op_data
                asm_codes += '{}: {}\n'.format(str(asm_pos).zfill(2), asm)
                asm_pos += 1
                if asm_pos >= 64:
                    raise Exception('line {} >> 错误：超出内存容量限制！'.format(line_num))
                line_num += 1
        return asm_codes[:-1]
