import csv
import re
from pathlib import Path

prefixes = ('454', '455', '460', '461', '466')
output = Path('中国所有地区.csv')
count = 0

mapping = {
    'B.1[A-X].{1,3}': '北京',
    'B.2[A-H].{1,3}': '黑龙江',
    'B.2[I-P].{1,3}': '吉林',
    'B.2[Q-X].{1,3}': '辽宁',
    'B.3[A-F].{1,3}': '天津',
}

region_ids = {k: [] for k in mapping.values()}

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
            for pattern, region in mapping.items():
                if re.match(pattern, row[1].strip()):
                    region_ids[region].append(row[0].strip())
# 分区处理
    for region, ids in region_ids.items():
        print(f'{region}: {len(ids)} 条记录')
        with open(f'{region}.csv', 'w', encoding='utf-8-sig', newline='') as region_file:
            writer = csv.writer(region_file)
            writer.writerow(header)
            for row in reader:
                if row and row[0].strip() in ids:
                    writer.writerow(row)
if count == 0:
    raise RuntimeError('没有匹配记录，停止发布，请检查源数据。')
print(f'已生成 {output}，共 {count} 条记录。')
