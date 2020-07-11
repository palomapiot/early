Feature: About page

  Scenario: Access the about page

	Given an anonymous user
	When I submit the about page
	Then I am redirected to the about page
