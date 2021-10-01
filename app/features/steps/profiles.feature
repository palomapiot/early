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

Feature: Profiles actions

  Scenario: Access the profiles page

	Given a logged user
    And an existing profile
	When I load the profiles page
	Then I get a list of profiles

  Scenario: Access the profile detail page

	Given a logged user
    And an existing profile
	When I load the profile detail page
	Then I get the profile details

  Scenario: Validate profile

	Given a logged user
    And an existing profile
	When I validate an existing profile
	Then I am redirected to the success edit page

  Scenario: Validate invalid profile

	Given a logged user
    And an existing profile
	When I validate with wrong values an existing profile
	Then I get a submission error