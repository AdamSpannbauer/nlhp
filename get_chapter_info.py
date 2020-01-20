import requests
import pandas as pd

output_csv = 'data/chapter_info.csv'
url = 'https://harrypotter.fandom.com/wiki/List_of_chapters_in_the_Harry_Potter_novels'

book_names = ["Harry Potter and the Philosopher's Stone",
              'Harry Potter and the Chamber of Secrets',
              'Harry Potter and the Prisoner of Azkaban',
              'Harry Potter and the Goblet of Fire',
              'Harry Potter and the Order of the Phoenix',
              'Harry Potter and the Half-Blood Prince',
              'Harry Potter and the Deathly Hallows']

response = requests.get(url)
html = response.text

col_names = ['series_chapter_num', 'book_chapter_num', 'chapter_picture',
             'chapter_title', 'chapter_start_date']
drop_cols = ['chapter_picture']
col_order = ['book_num', 'series_chapter_num', 'book_chapter_num',
             'book_title', 'chapter_title', 'chapter_start_date']

chapter_dfs = pd.read_html(html, header=0)
clean_chapter_dfs = []
for i, chapter_df in enumerate(chapter_dfs):
    chapter_df.columns = col_names
    chapter_df = chapter_df.drop(columns=drop_cols)
    chapter_df['book_num'] = i + 1
    chapter_df['book_title'] = book_names[i]
    chapter_df = chapter_df[col_order]
    clean_chapter_dfs.append(chapter_df)

full_chapter_df = pd.concat(clean_chapter_dfs)
full_chapter_df.to_csv(output_csv, index=False)
