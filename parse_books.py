import os
import re
import glob
import pandas as pd
import spacy
from tqdm import tqdm

SECTION_BREAKS = [b'\xc2\xa0', b'\xe3\x80\x80']
SECTION_BREAKS_RE = b'|'.join(SECTION_BREAKS)
NLP = spacy.load('en_core_web_sm')


def parse_sentences(text):
    parsed = NLP(text)
    return [s.text for s in parsed.sents]


def read_book_to_df(book_path):
    with open(book_path, 'rb') as f:
        chapter_bytes_list = f.readlines()

    chapter_dfs = []
    enum = enumerate(chapter_bytes_list)
    for i, chapter_bytes in tqdm(enum, total=len(chapter_bytes_list)):
        # bad hardcoded replacements to make decode work
        # if you're reading this.. this is not best practice
        # be better than me
        chapter_bytes = chapter_bytes.replace(b'\xc2\xa8C', b'-')
        chapter_bytes = chapter_bytes.replace(b'\xe2\x80\x93', b'-')
        chapter_bytes = chapter_bytes.replace(b'\xe2\x80\x94', b'-')
        chapter_bytes = chapter_bytes.replace(b'\xc2\xa8\xc2\xa6', b'e')
        chapter_bytes = chapter_bytes.replace(b'\xe2\x80\x98', b"'")
        chapter_bytes = chapter_bytes.replace(b'\xe2\x80\x99', b"'")
        chapter_bytes = chapter_bytes.replace(b'\xe2\x80\x9c', b'"')
        chapter_bytes = chapter_bytes.replace(b'\xe2\x80\x9d', b'"')
        chapter_bytes = chapter_bytes.replace(b'\xe2\x80\xa6', b'... ')

        section_bytes = re.split(SECTION_BREAKS_RE, chapter_bytes)
        section_text = [sb.decode('ascii') for sb in section_bytes]

        chapter_df = pd.DataFrame({'chapter_num': i + 1,
                                   'sentence': section_text})

        chapter_df['sentence'] = chapter_df['sentence'].apply(parse_sentences)
        chapter_df = chapter_df.explode('sentence')
        chapter_dfs.append(chapter_df)

    book_df = pd.concat(chapter_dfs)

    return book_df


def parse_books(book_text_dir, parse_output_dir):
    book_glob = os.path.join(book_text_dir, '*.txt')
    book_paths = glob.glob(book_glob)

    for i, book_path in enumerate(book_paths):
        print(f'\nParsing: {book_path} ({i + 1} of {len(book_paths)})')
        book_df = read_book_to_df(book_path)

        file_name = os.path.split(book_path)[-1]
        book_df['file_name'] = file_name

        base_file_name = os.path.splitext(file_name)[0]
        csv_path = os.path.join(parse_output_dir, base_file_name + '.csv')

        book_df.to_csv(csv_path, index=False)


if __name__ == '__main__':
    parse_books(book_text_dir='text', parse_output_dir='data/parsed_books')
