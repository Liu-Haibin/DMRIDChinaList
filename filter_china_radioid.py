"""筛选 user.csv，生成保留原始表头和全部列的中国所有地区.csv。"""

import csv
from pathlib import Path

prefixes = ('454', '455', '460', '461', '466')
output = Path('中国所有地区.csv')
count = 0
with open('user.csv', encoding='utf-8-sig', newline='') as source:
    reader = csv.reader(source)
    header = next(reader, None)
    if not header or header[0].strip().upper() != 'RADIO_ID':
        raise RuntimeError(f'源 CSV 第一列不是 RADIO_ID: {header!r}')
    with output.open('w', encoding='utf-8-sig', newline='') as target:
        writer = csv.writer(target)
        writer.writerow(header)
        for row in reader:
            if row and row[0].strip().startswith(prefixes):
                writer.writerow(row)
                count += 1
if count == 0:
    raise RuntimeError('没有匹配记录，停止发布，请检查源数据。')
print(f'已生成 {output}，共 {count} 条记录。')
