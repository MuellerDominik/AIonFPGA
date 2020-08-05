#!/usr/bin/env python3

'''aionfpga ~ fhnwtoys.definitions
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import random

import MySQLdb

from tensorflow.keras import utils

from .settings import *

# Classes --------------------------------------------------------------------

class Dataset_Generator(utils.Sequence):
    def __init__(self, frames_name, labels_name, directory, num_batches, batch_size):
        self.frames_name = frames_name
        self.labels = np.load(directory / f'{labels_name}.npy')
        self.directory = directory
        self.num_batches = num_batches
        self.batch_size = batch_size

    def __len__(self):
        return self.num_batches

    def __getitem__(self, idx):
        start = idx * self.batch_size
        end = start + self.batch_size

        frames = np.load(self.directory / f'{self.frames_name}_batch_{idx}_of_{self.num_batches}.npy')

        batch_x = frames.astype(np.float32) / 255.0
        batch_y = np.asarray(self.labels[start:end])

        return batch_x, batch_y

class RNG():
    def __init__(self, seed):
        self.seed = seed
        self.rand = random.Random(seed)

    def shuffle(self, x): # shuffle x in place
        return self.rand.shuffle(x)

# Functions ------------------------------------------------------------------

# replace 'o_n' with 'n_n' (rep=[(o_0, n_0), ..., (o_n, n_n)]), if in 'string'
def repl(string, rep):
    for o, n in rep:
        if o in string:
            string = string.replace(o, n)
    return string

# Database Functions ---------------------------------------------------------

# execute query
def db_write(queries, database):
    db = MySQLdb.connect(host=host, port=port, user=user,
                         passwd=passwd, db=database)
    cursor = db.cursor()
    for query in queries:
        cursor.execute(query)
    db.commit()
    cursor.close()
    db.close()

# return the first match
def db_fetch_field(query, database):
    db = MySQLdb.connect(host=host, port=port, user=user,
                         passwd=passwd, db=database)
    cursor = db.cursor()
    cursor.execute(query)
    field = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return field

# return the matching rows
def db_fetch_rows(query, database):
    db = MySQLdb.connect(host=host, port=port, user=user,
                         passwd=passwd, db=database)
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return rows

# fetch specific field from specific row
def fetch_field(table, row, field, database=database):
    query = f"SELECT {field} FROM {table} WHERE id = '{row}'"
    return db_fetch_field(query, database)

# fetch 'fields' from rows where 'column' equals 'value' in 'table'
def fetch_rows(table, column, value, fields, database=database):
    query = f"SELECT {fields} FROM {table} WHERE {column} = '{value}'"
    return db_fetch_rows(query, database)

# fetch 'fields' from all rows in 'table'
def fetch_all_rows_fields(table, fields, database=database):
    query = f"SELECT {fields} FROM {table}"
    return db_fetch_rows(query, database)

# returns all rows from 'table'
def fetch_all_rows(table, database = database):
    query = f"SELECT * FROM {table}"
    return db_fetch_rows(query, database)

def fetch_rows_and(table, columns, values, fields, database=database):
    query = f"SELECT {fields} FROM {table} WHERE {columns[0]} = '{values[0]}'"
    columns.pop(0); values.pop(0)
    for c, v in zip(columns, values):
        query += f" AND {c} = '{values[0]}'"
    return db_fetch_rows(query, database)

# set 'field' of 'row' to 'value' in 'table'
def update_field(table, row, field, value, database=database):
    update_fields(table, [row], field, [value])

# set 'field' of 'rows' to 'values' in 'table'
# 'rows' and 'values' need to be lists of same size
def update_fields(table, rows, field, values, database=database):
    queries = []
    for row, value in zip(rows, values):
        queries.append((f"UPDATE {table} SET {field} = '{value}' "
                        f"WHERE id = '{row}'"))
    db_write(queries, database)

# insert single 'row' into 'table'
def insert_row(table, row, database=database):
    insert_rows(table, [row])

# insert multiple 'rows' into 'table'
def insert_rows(table, rows, database=database):
    queries = []
    for row in rows:
        query = f'INSERT INTO {table} VALUES (NULL, '
        for val in row:
            query += f'{val}, '
        queries.append(f'{query[:-2]})')
    db_write(queries, database)
