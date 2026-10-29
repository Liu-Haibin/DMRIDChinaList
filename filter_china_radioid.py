"""筛选 RadioID 数据，并按呼号号段导出地区 CSV。

大陆地区依据《业余无线电台呼号编制和核发要求》附件 2。
呼号地区表示号段分配地区，不代表电台当前所在位置。
所有地区均使用 mapping 中的呼号正则判断，RADIO_ID 仅用于筛选总表。
"""

import csv
import re
from contextlib import ExitStack
from pathlib import Path

PREFIXES = ('454', '455', '460', '461', '466')

REGION_PATTENS = {
    r'VR2[A-Z0-9]{1,4}': '香港',
    r'XX9[A-Z0-9]{1,4}': '澳门',
    r'B[MNOPQUVWX][0-9][A-Z]{1,3}': '台湾',
    r'B.1[A-X].{1,3}': '北京',
    r'B.2[A-H].{1,3}': '黑龙江',
    r'B.2[I-P].{1,3}': '吉林',
    r'B.2[Q-X].{1,3}': '辽宁',
    r'B.3[A-F].{1,3}': '天津',
    r'B.3[G-L].{1,3}': '内蒙古',
    r'B.3[M-R].{1,3}': '河北',
    r'B.3[S-X].{1,3}': '山西',
    r'B.4[A-H].{1,3}': '上海',
    r'B.4[I-P].{1,3}': '山东',
    r'B.4[Q-X].{1,3}': '江苏',
    r'B.5[A-H].{1,3}': '浙江',
    r'B.5[I-P].{1,3}': '江西',
    r'B.5[Q-X].{1,3}': '福建',
    r'B.6[A-H].{1,3}': '安徽',
    r'B.6[I-P].{1,3}': '河南',
    r'B.6[Q-X].{1,3}': '湖北',
    r'B.7[A-H].{1,3}': '湖南',
    r'B.7[I-P].{1,3}': '广东',
    r'B.7[Q-X].{1,3}': '广西',
    r'B.7[Y-Z].{1,3}': '海南',
    r'B.8[A-F].{1,3}': '四川',
    r'B.8[G-L].{1,3}': '重庆',
    r'B.8[M-R].{1,3}': '贵州',
    r'B.8[S-X].{1,3}': '云南',
    r'B.9[A-F].{1,3}': '陕西',
    r'B.9[G-L].{1,3}': '甘肃',
    r'B.9[M-R].{1,3}': '宁夏',
    r'B.9[S-X].{1,3}': '青海',
    r'B.0[A-F].{1,3}': '新疆',
    r'B.0[G-L].{1,3}': '西藏',
}


def detect_region(callsign):
    callsign = callsign.strip().upper()
    for pattern, region in REGION_PATTENS.items():
        if re.fullmatch(pattern, callsign):
            return region
    return '未识别地区'


def main():
    output_dir = Path('csv')
    regions = list(dict.fromkeys(REGION_PATTENS.values())) + ['未识别地区']
    counts = dict.fromkeys(regions, 0)
    total = 0
    with open('user.csv', encoding='utf-8-sig', newline='') as source, ExitStack() as stack:
        reader = csv.reader(source)
        header = next(reader, None)
        if not header or header[0].strip().upper() != 'RADIO_ID':
            raise RuntimeError(f'源 CSV 第一列不是 RADIO_ID: {header!r}')
        try:
            callsign_index = [column.strip().upper() for column in header].index('CALLSIGN')
        except ValueError as error:
            raise RuntimeError('源 CSV 缺少 CALLSIGN 列') from error
        output_dir.mkdir(exist_ok=True)

        def writer_for(name):
            target = stack.enter_context((output_dir / f'{name}.csv').open(
                'w', encoding='utf-8-sig', newline=''))
            writer = csv.writer(target)
            writer.writerow(header)
            return writer

        combined = writer_for('中国所有地区')
        writers = {region: writer_for(region) for region in regions}
        for row in reader:
            if not row or not row[0].strip().startswith(PREFIXES):
                continue
            if len(row) != len(header):
                raise RuntimeError(f'CSV 第 {reader.line_num} 行列数异常')
            region = detect_region(row[callsign_index])
            combined.writerow(row)
            writers[region].writerow(row)
            counts[region] += 1
            total += 1
    if total == 0:
        raise RuntimeError('没有匹配记录，停止发布，请检查源数据。')
    for region, count in counts.items():
        print(f'{region}: {count} 条记录')
    print(f'已生成 {output_dir}/中国所有地区.csv，共 {total} 条记录。')


if __name__ == '__main__':
    main()
