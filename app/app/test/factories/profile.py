"""
    Copyright 2020-2021 Paloma Piot Pérez-Abadín
	
	This file is part of early.
    early is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    early is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with early.  If not, see <https://www.gnu.org/licenses/>.
"""

import factory
from app.api.models import Profile


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
        #django_get_or_create = ('experiment_id')
        # Defaults (can be overrided)
    experiment_id = 'behave_test_1'
    id = 1
