Feature: Password reset form

  Scenario: Access the password reset form

	Given an anonymous user
	When I submit a valid email
	Then I am redirected to the reset password success page

	Given an anonymous user
	When I submit an empty email
	Then I am redirected to the reset password fail page