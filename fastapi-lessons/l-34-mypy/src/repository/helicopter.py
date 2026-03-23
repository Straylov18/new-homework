from typing import Any, Dict

from sqlalchemy import Select

from src.model.helicopter import HelicopterModel
from src.repository.base_repository import SQLAlchemyRepository


class HelicopterRepository(SQLAlchemyRepository[HelicopterModel]):
    _model = HelicopterModel

    def _get_filtered_query(self, query: Select[tuple[HelicopterModel]],
                            filter_attributes: Dict[str, Any]) -> Select[tuple[HelicopterModel]]:
        filtered_query = query
        if filter_attributes.get('search_str', '') != '':
            search_str = filter_attributes.get('search_str', '')
            filtered_query = filtered_query.filter(
                HelicopterModel.model_title.ilike(f'%{search_str}%')
            )
        # date
        if filter_attributes.get('registration_date_lte', '') != '':
            registration_date_lte = filter_attributes['registration_date_lte']
            filtered_query = filtered_query.filter(
                HelicopterModel.registration_date <= registration_date_lte
            )
        if filter_attributes.get('registration_date_gte', '') != '':
            registration_date_gte = filter_attributes['registration_date_gte']
            filtered_query = filtered_query.filter(
                HelicopterModel.registration_date >= registration_date_gte
            )
        return filtered_query
