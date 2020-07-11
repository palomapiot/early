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