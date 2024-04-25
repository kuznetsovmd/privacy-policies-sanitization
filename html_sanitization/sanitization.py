
from hashlib import md5
from multiprocessing import Pool
import os
import re
from tqdm import tqdm
from html_sanitization.sanitize import Sanitize
from utils.fsys import list_files, read_lines


def sanitize_html(input_files, sanitized_files, cpu_count, sanitizer_conf, 
                  deprecated_rules, uppercase_threshold, short_threshold, foreign_threshold, tqdm_conf):
    files = set(list(list_files(input_files)))
    # files = set(list(list_files(input_files))[:200])
    # files = set([
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/2210707.ru-politics.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/rukademia.ru-policy.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/edosk.ru-polzovatelskoe_soglashenie-p51.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/kuplu-hyundai.ru-pravovaya-informaciya.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/3815981.ru-privacy-policy.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/www.homeworkpro.ru-about-privacy-policy--PartnerId-11156.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/xn--90aoffsx5f.xn--p1ai-pol-t-ka-konf-djenc-alnost.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/prazdnikspb.su-polzovatelskoe-soglashenie.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/page-audit.ru-license.txt.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/434040.ru-pers.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/cpsmd.ru-index.php-route-information-information-agree-information_id-3.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/101poisk.ru-politika.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/34poliklinika.by-первичная-профсоюзная-организация-политика-обработки-персональных-данных.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/74gbi.ru-personalnye-dannye.html.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/1k.by-info1k-agreement.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/23doc.ru-users-agreement.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/aba-clinic.com-polzovatelskoe-soglashenie.html',
    #     '/mnt/Source/kuznetsovmd/__datasets/ppr-dataset/original_policies/pokrovskaia.pro-privacy_ru.html'
    # ])
    
    print(f'total input docs: {len(files)}')

    remove = deprecated(files, tqdm_conf, deprecated_rules)
    files = files.difference(remove)

    fn = Sanitize(sanitized_files, **sanitizer_conf)
    with Pool(cpu_count) as p:
        files = set(tqdm(p.imap(fn, files), desc='sanitize', total=len(files), **tqdm_conf))

    remove = short(files, tqdm_conf, short_threshold)
    remove.update(duplicates(files.difference(remove), tqdm_conf))
    remove.update(uppercase(files.difference(remove), tqdm_conf, uppercase_threshold))
    remove.update(foreign(files.difference(remove), tqdm_conf, foreign_threshold))

    for f in remove:
        os.remove(f)

    print(f'total output docs: {len(files.difference(remove))}')


def deprecated(input_files, tqdm_conf, deprecated_rules):
    filtered = set()
    for f in tqdm(input_files, desc='deprecated', **tqdm_conf):
        if any(rule(f) for rule in deprecated_rules):
            filtered.add(f)
    return filtered


def short(input_files, tqdm_conf, short_threshold=500): 
    filtered = set()
    for f in tqdm(input_files, desc='short', **tqdm_conf):
        if len(read_lines(f)) < short_threshold:
            filtered.add(f)
    return filtered


def duplicates(input_files, tqdm_conf):
    duplicates = set()
    unique = set()
    for f in tqdm(input_files, desc='duplicates', **tqdm_conf):
        content = read_lines(f)
        hash = md5(content.encode('utf-8')).hexdigest()
        if hash in unique:
            duplicates.add(f)
        unique.add(hash)
    return duplicates


def uppercase(input_files, tqdm_conf, uppercase_threshold=.1):
    filtered = set()
    for f in tqdm(input_files, desc='uppercase', **tqdm_conf):
        content = read_lines(f)
        upper = sum(1 for c in content if c.isupper())
        lower = sum(1 for c in content if c.islower())
        if upper / (upper + lower) > uppercase_threshold:
            filtered.add(f)
    return filtered


def foreign(input_files, tqdm_conf, foreign_threshold=.3):
    filtered = set()
    for f in tqdm(input_files, desc='foreign', **tqdm_conf):
        content = read_lines(f)
        russian = len(re.findall(r'[А-ЯЁа-яё]', content))
        foreign = len(re.findall(r'[^А-ЯЁа-яё0-9.,:;\\/\-\n\(\)\{\}\[\]*?!@#=+\^%$ ]', content))
        if foreign / (foreign + russian) > foreign_threshold:
            filtered.add(f)
    return filtered
