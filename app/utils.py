import io
import pandas as pd
from typing import List

from schemas import Data, DataFromDB, Price, Project


class CSVReadFailExceptoin(Exception):
    pass


def parse_csv(data: bytes) -> Data:
    for sep in [',', ';']:
        df = pd.read_csv(io.BytesIO(data), encoding='utf8', sep=sep)
        if len(df.columns) > 1:
            break
    else:
        raise CSVReadFailExceptoin
    data = Data()
    years = list(df.columns[2:])
    for row in df.values:
        index, name, *prices = row
        match index.count('.'):
            case 0:
                project = Project(name=name)
                data.projects.append(project)
            case 1:
                sub_project = Project(name=name)
                project.sub_projects.append(sub_project)
            case 2:
                for ind, price in enumerate(prices):
                    year = years[ind]
                    print(name)
                    print(type(price))
                    price = Price(year=year, price=price)
                    sub_project.prices.setdefault(name, []).append(price)
    return data


def create_csv(data: DataFromDB, years: List[int]):
    df = pd.DataFrame(columns=['code', 'project', 'total price'] + years)
    for project_num, project in enumerate(data.projects, start=1):
        code = project_num
        df.loc[len(df)] = {
            'code': code,
            'project': project.name,
            'total price': project.total_price,
        }
        for sub_project_num, sub_project in enumerate(project.sub_projects, start=1):
            code = f'{project_num}.{sub_project_num}'
            df.loc[len(df)] = {
                'code': code,
                'project': sub_project.name,
                'total price': sub_project.total_price,
            }
            for price_num, (price_name, prices) in enumerate(sub_project.prices.items(), start=1):
                code = f'{project_num}.{sub_project_num}.{price_num}'
                row = {'code': code, 'project': price_name}
                row.update((price.year, price.price) for price in prices)
                df.loc[len(df)] = row
    return df.to_csv(index=False)
