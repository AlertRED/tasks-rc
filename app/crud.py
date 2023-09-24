from typing import List, Tuple
from sqlalchemy.sql import text
from sqlalchemy.orm import Session

from schemas import Data, DataFromDB, Price, ProjectFromDB


DATA_TRANSACTION_TEMPLATE = '''DO $$
    DECLARE
        version_id integer;
        project_id integer;
        sub_project_id integer;
BEGIN
{sql_raw}
END $$'''


class DataIsNotFoundException(Exception):
    pass


def create_data(data: Data, session: Session):
    statements = ['INSERT INTO version DEFAULT VALUES RETURNING version INTO version_id;']
    for project in data.projects:
        statement = (
            f'INSERT INTO project '
            f'(parent_id, name, version) VALUES '
            f'(NULL, \'{project.name}\', version_id) '
            f'RETURNING id INTO project_id;'
        )
        statements.append(statement)
        for sub_project in project.sub_projects:
            statement = (
                f'INSERT INTO project '
                f'(parent_id, name, version) VALUES '
                f'(project_id, \'{sub_project.name}\', NULL) '
                f'RETURNING id INTO sub_project_id;'
            )
            statements.append(statement)
            for price_name, prices in sub_project.prices.items():
                for price in prices:
                    statement = (
                        f'INSERT INTO price '
                        f'(project_id, name, price, year) VALUES '
                        f'(sub_project_id, \'{price_name}\', {price.price}, {price.year});'
                    )
                    statements.append(statement)
    sql_raw = '\n'.join(statement for statement in statements)
    with session.begin():
        session.execute(
            text(DATA_TRANSACTION_TEMPLATE.format(sql_raw=sql_raw)),
        )
    return session.execute(
        text('SELECT version FROM version ORDER BY version DESC LIMIT 1'),
    ).fetchone()[0]


def get_data(version: int, session: Session) -> Tuple[DataFromDB, List] | None:
    if session.execute(
        text(f'SELECT version FROM version WHERE version = {version}'),
    ).fetchone() is None:
        raise DataIsNotFoundException()
    years = set()
    data = DataFromDB(version=version)
    projects = session.execute(
        text(
            f'SELECT id, name FROM project '
            f'WHERE parent_id is NULL AND version = {version}'
        )
    ).fetchall()
    for project in projects:
        project_id, project_name = project
        project = ProjectFromDB(name=project_name)
        data.projects.append(project)
        sub_projects = session.execute(
            text(
                f'SELECT id, name FROM project '
                f'WHERE parent_id = {project_id}'
            )
        ).fetchall()
        for sub_project in sub_projects:
            sub_project_id, sub_project_name = sub_project
            sub_project = ProjectFromDB(name=sub_project_name)
            project.sub_projects.append(sub_project)
            prices = session.execute(
                text(
                    f'SELECT name, year, price FROM price '
                    f'WHERE project_id = {sub_project_id} '
                    f'ORDER BY name'
                )
            ).fetchall()
            for price in prices:
                price_name, year, price_per_year = price
                price = Price(year=year, price=price_per_year)
                sub_project.prices.setdefault(price_name, []).append(price)
                sub_project.total_price += price_per_year
                years.add(year)
            project.total_price += sub_project.total_price
        return data, sorted(years)
