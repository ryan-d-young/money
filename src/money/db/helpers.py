from sqlalchemy import MetaData, Table, Column, ForeignKey, types as t


def id_col():
    return Column("id", t.Integer, primary_key=True)